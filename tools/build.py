#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
站点生成器：problems/*.json + code/*.py  ==>  docs/ 静态站点。

    python3 tools/build.py            # 生成 docs/index.html 与 docs/problems/*.html
    python3 tools/build.py --check    # 只校验配置（CI 里先跑这个，出错即失败）

设计约定
    · problems/<id>-<slug>.json  —— 一道题的全部「非代码」信息（题号、标题、难度、
      标签、讲解文案、可视化配置）。加新题 = 加一个 json + 一个 py。
    · code/<题号>_<名字>.py        —— 解题程序，必须提供一个「轨迹函数」，
      供前端渲染成动图；轨迹与代码同源，不会出现「图画的和代码跑的不一样」。
    · docs/                        —— 全部由本脚本生成，勿手工修改。
      docs/assets/ 与 docs/templates/ 是手写资产。
"""

from __future__ import annotations

import argparse
import ast
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"
CODE_DIR = ROOT / "code"
DOCS_DIR = ROOT / "docs"
TEMPLATE_DIR = DOCS_DIR / "templates"

TEMPLATE_PROBLEM = TEMPLATE_DIR / "problem.html"
TEMPLATE_INDEX = TEMPLATE_DIR / "index.html"

PY_KEYWORDS = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "in", "not",
    "and", "or", "import", "from", "as", "None", "True", "False", "lambda",
    "break", "continue", "pass", "raise", "with", "try", "except", "finally",
    "yield", "global", "self",
}


# ---------------------------------------------------------------- 基础工具

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fill(template: str, values: dict) -> str:
    for key, val in values.items():
        template = template.replace("{{%s}}" % key, val)
    leftovers = re.findall(r"\{\{(\w+)\}\}", template)
    if leftovers:
        raise SystemExit("模板存在未替换的占位符: %s" % ", ".join(sorted(set(leftovers))))
    return template


# ---------------------------------------------------------------- 代码处理

def extract_class(code_src: str, class_name: str) -> str:
    """从源码里抠出某个 class 的完整定义（含装饰器与注释行）。"""
    tree = ast.parse(code_src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            lines = code_src.splitlines()
            start = node.lineno - 1
            for dec in node.decorator_list:
                start = min(start, dec.lineno - 1)
            return "\n".join(lines[start:node.end_lineno])
    raise KeyError("源码里找不到 class %s" % class_name)


def highlight_python(src: str) -> list[str]:
    """极简 Python 高亮：返回逐行的 HTML 片段列表。"""
    out = []
    for raw in src.split("\n"):
        buf, i, quote, n = "", 0, None, len(raw)
        while i < n:
            c = raw[i]
            if quote:
                buf += html.escape(c)
                if c == "\\" and i + 1 < n:
                    buf += html.escape(raw[i + 1])
                    i += 2
                    continue
                if c == quote:
                    quote = None
                i += 1
                continue
            if c in "\"'":
                quote = c
                buf += '<span class="s">' + html.escape(c)
                i += 1
                continue
            if c == "#":
                buf += '<span class="c">' + html.escape(raw[i:]) + "</span>"
                i = n
                break
            buf += html.escape(c)
            i += 1
        if quote:
            buf += "</span>"
        out.append(buf)
    return out


def import_module(path: Path):
    spec = importlib.util.spec_from_file_location("lc_%s" % path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError("无法加载 %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- Markdown

def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def render_md(text: str) -> str:
    """支持：段落、- 列表、> 引用、``` 围栏代码块、行内 `code` 与 **加粗**。"""
    if not text.strip():
        return ""
    blocks = []
    chunks = re.split(r"\n\s*\n", text.strip())
    for raw in chunks:
        lines = [l.rstrip() for l in raw.strip().split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0].startswith("```"):
            body = []
            for l in lines[1:]:
                if l.startswith("```"):
                    break
                body.append(l)
            blocks.append('<pre class="md-code">%s</pre>' % html.escape("\n".join(body)))
            continue
        if all(l.startswith("- ") for l in lines):
            items = "".join("<li>%s</li>" % md_inline(l[2:]) for l in lines)
            blocks.append('<ul class="md-list">%s</ul>' % items)
        elif all(l.startswith("> ") for l in lines):
            inner = "<br>".join(md_inline(l[2:]) for l in lines)
            blocks.append('<blockquote class="md-quote">%s</blockquote>' % inner)
        else:
            inner = "<br>".join(md_inline(l) for l in lines)
            blocks.append('<p class="md-p">%s</p>' % inner)
    return "\n".join(blocks)


# ---------------------------------------------------------------- 数据装配

def load_problems() -> list[dict]:
    metas = []
    for path in sorted(PROBLEMS_DIR.glob("*.json")):
        meta = json.loads(read(path))
        meta["_file"] = path.name
        metas.append(meta)
    metas.sort(key=lambda m: m.get("id", ""))
    return metas


def _load_module(meta: dict):
    code_path = ROOT / meta["code"]
    if not code_path.exists():
        raise SystemExit("[%s] 找不到代码文件 %s" % (meta["id"], meta["code"]))
    return code_path, import_module(code_path)


def _run_trace(module, meta: dict, fn_name: str, args: list, snippet_texts: list) -> list:
    fn = getattr(module, fn_name, None)
    if fn is None:
        raise SystemExit("[%s] 代码文件里没有轨迹函数 %s" % (meta["id"], fn_name))
    frames = list(fn(*args))
    for frame in frames:
        needle = frame.get("codeLine")
        frame["_codeIdx"] = -1
        if needle and snippet_texts:
            for idx, text in enumerate(snippet_texts):
                if needle in text:
                    frame["_codeIdx"] = idx
                    break
        frame.pop("codeLine", None)
    return frames


def derive_display(rtype: str, args: list, lane_cfg: dict) -> tuple:
    """从轨迹函数的入参推导出页面上要画的东西。

    array 渲染器：tokens = 数组里的元素
    digits 渲染器：rows  = 每个加数一行，且按「高位在左」的正常阅读顺序
    """
    if rtype == "digits":
        rows = lane_cfg.get("rows")
        if not rows:
            rows = [[str(x) for x in reversed(list(a))]
                    for a in args if isinstance(a, (list, tuple))]
        return [], rows

    tokens = lane_cfg.get("tokens")
    if not tokens and args:
        first = args[0]
        if isinstance(first, (list, tuple)):
            tokens = [str(x) for x in first]
        elif isinstance(first, str):
            tokens = list(first)
    return tokens or [], []


def build_lane(meta: dict, lane_cfg: dict, demo: dict) -> dict:
    """把「题目配置 + Python 轨迹函数」装配成前端可播放的一条轨道。"""
    code_path, module = _load_module(meta)
    fn_name = lane_cfg.get("trace")
    if not fn_name:
        raise SystemExit("[%s] 轨道缺少 trace 配置" % meta["id"])

    class_name = lane_cfg.get("code")
    snippet_html, snippet_texts = [], []
    if class_name:
        try:
            snippet = extract_class(read(code_path), class_name)
        except KeyError:
            raise SystemExit("[%s] 代码文件里没有 class %s" % (meta["id"], class_name))
        snippet_html = highlight_python(snippet)
        snippet_texts = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in snippet_html]

    rtype = demo.get("type", "array")
    if "args" in lane_cfg:
        demo_args = lane_cfg["args"]
    elif "args" in demo:
        demo_args = demo["args"]
    else:
        demo_args = [demo.get("input", "")]

    if "compareArgs" in demo:
        compare_args = demo["compareArgs"]
    elif "compareInput" in demo:
        compare_args = [demo["compareInput"]]
    else:
        compare_args = demo_args

    frames = _run_trace(module, meta, fn_name, demo_args, snippet_texts)
    cmp_frames = frames if compare_args == demo_args else _run_trace(
        module, meta, fn_name, compare_args, snippet_texts)

    tokens, rows = derive_display(rtype, demo_args, lane_cfg)
    cmp_tokens, cmp_rows = derive_display(rtype, compare_args, lane_cfg)

    return {
        "name": lane_cfg.get("name", "解法"),
        "badge": lane_cfg.get("badge", ""),
        "variant": lane_cfg.get("variant", "neutral"),
        "type": rtype,
        "input": demo.get("input", ""),
        "tokens": tokens,
        "rows": rows,
        "compareTokens": cmp_tokens,
        "compareRows": cmp_rows,
        "frames": frames,
        "compareFrames": cmp_frames,
        "codeClass": class_name,
        "codeLines": snippet_html,
        "showCode": bool(lane_cfg.get("showCode", False)),
    }


def build_problem(meta: dict) -> dict:
    demo = meta.get("demo") or {}
    lanes = [build_lane(meta, lane, demo) for lane in demo.get("lanes", [])]

    snippets = []
    for class_name in meta.get("snippets", []):
        code_src = read(ROOT / meta["code"])
        snippet = extract_class(code_src, class_name)
        snippets.append({
            "name": class_name,
            "html": highlight_python(snippet),
            "text": snippet,
        })

    complexity = meta.get("complexity") or []
    return {
        "meta": meta,
        "lanes": lanes,
        "snippets": snippets,
        "complexity": complexity,
    }


# ---------------------------------------------------------------- 页面渲染

def render_code_tabs(snippets: list[dict]) -> str:
    if not snippets:
        return ""
    buttons, panels = [], []
    for idx, sn in enumerate(snippets):
        sel = ' aria-selected="true"' if idx == 0 else ' aria-selected="false"'
        buttons.append(
            '<button type="button" role="tab" data-snippet="%d"%s>%s</button>' % (idx, sel, html.escape(sn["name"]))
        )
        body = "\n".join(sn["html"])
        panels.append(
            '<pre class="src" data-snippet-panel="%d"%s><code>%s</code></pre>'
            % (idx, "" if idx == 0 else " hidden", body)
        )
    return (
        '<div class="tabs" role="tablist" data-tabs>%s</div>\n%s'
        % ("".join(buttons), "\n".join(panels))
    )


def render_complexity(table: list) -> str:
    if not table:
        return ""
    head = "".join("<th>%s</th>" % html.escape(str(c)) for c in table[0])
    rows = []
    for row in table[1:]:
        cells = []
        for cell in row:
            text = html.escape(str(cell))
            if text in ("✅", "❌"):
                cells.append('<td class="mark">%s</td>' % text)
            else:
                cells.append("<td>%s</td>" % text)
        rows.append("<tr>%s</tr>" % "".join(cells))
    return (
        '<table class="cmp"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
        % (head, "".join(rows))
    )


DIFFICULTY_CLASSES = {"简单": "easy", "中等": "medium", "困难": "hard",
                      "easy": "easy", "medium": "medium", "hard": "hard"}


def difficulty_class(difficulty: str) -> str:
    return DIFFICULTY_CLASSES.get(str(difficulty).strip().lower(),
                                  str(difficulty).strip().lower() or "none")


def render_tags(tags: list, clickable: bool = False) -> str:
    cls = "tag tag-card" if clickable else "tag"
    return "".join(
        '<span class="%s" data-tag="%s">%s</span>' % (cls, html.escape(t), html.escape(t))
        for t in tags
    )


def render_problem_page(problem: dict, prev_problem: dict | None, next_problem: dict | None) -> str:
    meta = problem["meta"]
    payload = {
        "id": meta["id"],
        "type": (meta.get("demo") or {}).get("type", "window"),
        "compareTitle": (meta.get("demo") or {}).get("compareTitle", "同一个输入，两种写法并行跑一遍"),
        "lanes": problem["lanes"],
    }
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    nav = []
    if prev_problem:
        nav.append(
            '<a class="nav-prev" href="%s.html">← 上一题 · %s</a>'
            % (html.escape(prev_problem["meta"]["slug"]), html.escape(prev_problem["meta"]["title"]))
        )
    else:
        nav.append('<span></span>')
    if next_problem:
        nav.append(
            '<a class="nav-next" href="%s.html">下一题 · %s →</a>'
            % (html.escape(next_problem["meta"]["slug"]), html.escape(next_problem["meta"]["title"]))
        )
    else:
        nav.append('<span></span>')

    notes_section = ""
    if meta.get("notes"):
        notes_section = (
            '<section id="notes"><div class="sec-head"><h2>解题思路</h2></div>'
            '<div class="card md">%s</div></section>' % render_md(meta["notes"])
        )

    complexity_section = ""
    if problem["complexity"]:
        complexity_section = (
            '<section id="complexity"><div class="sec-head"><h2>复杂度对比</h2></div>'
            '<div class="card">%s</div></section>' % render_complexity(problem["complexity"])
        )

    return fill(read(TEMPLATE_PROBLEM), {
        "ID": html.escape(meta["id"]),
        "DIFFICULTY_CLASS": difficulty_class(meta.get("difficulty", "")),
        "NOTES_SECTION": notes_section,
        "COMPLEXITY_SECTION": complexity_section,
        "TITLE": html.escape(meta["title"]),
        "TITLE_EN": html.escape(meta.get("title_en", "")),
        "DIFFICULTY": html.escape(meta.get("difficulty", "")),
        "TAGS": render_tags(meta.get("tags", [])),
        "SUMMARY": md_inline(meta.get("summary", "")),
        "NOTES": render_md(meta.get("notes", "")),
        "COMPLEXITY": render_complexity(problem["complexity"]),
        "CODE_TABS": render_code_tabs(problem["snippets"]),
        "PLAYER": '<div id="player" class="player"></div>',
        "PAYLOAD": payload_json,
        "NAV": "".join(nav),
        "ROOT": "..",
    })


def render_index_page(problems: list[dict]) -> str:
    cards = []
    for problem in problems:
        meta = problem["meta"]
        tags = meta.get("tags", [])
        cards.append(
            '<a class="pcard" href="problems/%s.html" data-tags="%s">'
            '<span class="pcard-id">%s</span>'
            '<span class="pcard-title">%s</span>'
            '<span class="pcard-en">%s</span>'
            '<span class="pcard-foot">'
            '<span class="diff diff-%s">%s</span>'
            '<span class="tags">%s</span>'
            '</span>'
            '<span class="pcard-sum">%s</span>'
            "</a>"
            % (
                html.escape(meta["slug"]),
                html.escape("|".join(tags)),
                html.escape(meta["id"]),
                html.escape(meta["title"]),
                html.escape(meta.get("title_en", "")),
                difficulty_class(meta.get("difficulty", "")),
                html.escape(meta.get("difficulty", "")),
                render_tags(meta.get("tags", []), clickable=True),
                md_inline(meta.get("summary", "")),
            )
        )

    tag_counter: dict[str, int] = {}
    for problem in problems:
        for tag in problem["meta"].get("tags", []):
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    tag_cloud = (
        '<div class="tagbar" data-tag-filter role="group" aria-label="按标签筛选题目">'
        '<button type="button" class="tag tag-btn is-active" data-tag="" aria-pressed="true">'
        '全部 <b>%d</b></button>' % len(problems)
        + "".join(
            '<button type="button" class="tag tag-btn" data-tag="%s" aria-pressed="false">%s <b>%d</b></button>'
            % (html.escape(t), html.escape(t), c)
            for t, c in sorted(tag_counter.items(), key=lambda kv: (-kv[1], kv[0]))
        )
        + '</div><span class="filter-count" data-filter-count role="status" aria-live="polite"></span>'
    )

    return fill(read(TEMPLATE_INDEX), {
        "ASSETS": "assets",
        "COUNT": str(len(problems)),
        "CARDS": "\n".join(cards),
        "TAGS": tag_cloud,
    })


# ---------------------------------------------------------------- 主流程

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="生成 docs/ 静态站点")
    parser.add_argument("--check", action="store_true", help="只校验配置，不写文件")
    args = parser.parse_args(argv)

    metas = load_problems()
    if not metas:
        raise SystemExit("problems/ 下没有找到任何 *.json")

    problems = []
    for meta in metas:
        try:
            problems.append(build_problem(meta))
        except SystemExit as e:
            print("配置错误: %s" % e, file=sys.stderr)
            return 1
        print("[ok] %s  %s  (%d 条轨道)" % (meta["id"], meta["title"], len(problems[-1]["lanes"])))

    if args.check:
        print("校验通过，共 %d 道题" % len(problems))
        return 0

    out_dir = DOCS_DIR / "problems"
    out_dir.mkdir(parents=True, exist_ok=True)
    expected = set()

    for idx, problem in enumerate(problems):
        prev_p = problems[idx - 1] if idx > 0 else None
        next_p = problems[idx + 1] if idx + 1 < len(problems) else None
        page = render_problem_page(problem, prev_p, next_p)
        out = out_dir / ("%s.html" % problem["meta"]["slug"])
        write(out, page)
        expected.add(out.name)
        print("  -> %s" % out.relative_to(ROOT))

    # 清理已删除题目留下的过期页面
    for stale in sorted(out_dir.glob("*.html")):
        if stale.name not in expected:
            stale.unlink()
            print("  - 清理过期页面 %s" % stale.relative_to(ROOT))

    index = render_index_page(problems)
    write(DOCS_DIR / "index.html", index)
    print("  -> %s" % (DOCS_DIR / "index.html").relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
