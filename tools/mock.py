#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闭卷默写工具：从仓库里抽一道题，只给题面，计时，然后跟仓库的标准解对拍。

    python3 tools/mock.py                          # 随机抽一题，开始闭卷默写
    python3 tools/mock.py --list                   # 列出全部题目
    python3 tools/mock.py --id 0121                # 指定题号
    python3 tools/mock.py --tag 动态规划,哈希表      # 只在这些标签里抽（可重复）
    python3 tools/mock.py --difficulty 简单         # 按难度抽
    python3 tools/mock.py --id 0121 --reveal        # 直接看讲解
    python3 tools/mock.py --id 0121 --check mine.py # 把你写的解跟仓库解对拍

设计约定
    · 题面只来自 problems/*.json 的 statement / demo.args，**不泄露** notes 与代码
    · 标准答案 = 仓库自己的 Solution 类；样例取 demo.args 与 demo.compareArgs
    · 纯标准库，跟仓库其它工具一致
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"


# ---------------------------------------------------------------- 终端小工具

def _c(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return "%s%s%s" % (color, text, "\033[0m")


BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"


def hr(char: str = "─", width: int = 62) -> str:
    return char * width


# ---------------------------------------------------------------- 读配置

def load_problems() -> list[dict]:
    metas = []
    for path in sorted(PROBLEMS_DIR.glob("*.json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["_file"] = path.name
        metas.append(meta)
    metas.sort(key=lambda m: m.get("id", ""))
    return metas


def pick(problems: list[dict], pid: str | None, tags: list[str], difficulty: str | None):
    pool = problems
    if pid:
        pool = [m for m in pool if m.get("id") == pid]
        if not pool:
            raise SystemExit("没有题号 %s" % pid)
        return pool[0]
    if tags:
        want = set(tags)
        pool = [m for m in pool if want & set(m.get("tags", []))]
    if difficulty:
        pool = [m for m in pool if m.get("difficulty") == difficulty]
    if not pool:
        raise SystemExit("没有符合条件的题目")
    return random.choice(pool)


# ---------------------------------------------------------------- 题面

def _import(path: Path):
    spec = importlib.util.spec_from_file_location("mock_%s" % path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError("无法加载 %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def public_methods(code_src: str, class_name: str) -> list[str]:
    """列出某个 class 里对外的方法名（第一个就是 LeetCode 上要实现的那个）。"""
    tree = ast.parse(code_src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [n.name for n in node.body
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    return []


def param_names(meta: dict) -> list[str]:
    """从轨迹函数的签名里借参数名，好把样例输入写成 `nums = [...]` 这样的形式。"""
    demo = meta.get("demo") or {}
    lanes = demo.get("lanes") or []
    trace_name = lanes[0].get("trace") if lanes else None
    if not trace_name:
        return []
    try:
        module = _import(ROOT / meta["code"])
        fn = getattr(module, trace_name, None)
        if fn is None:
            return []
        return list(inspect.signature(fn).parameters)
    except Exception:
        return []


def sample_inputs(meta: dict) -> list[tuple[str, list]]:
    """一组用来演示的输入：demo.args 是主样例，demo.compareArgs 是对比样例。"""
    demo = meta.get("demo") or {}
    names = param_names(meta)
    out = []
    args = demo.get("args")
    if args is not None:
        out.append(("样例输入", args))
    cargs = demo.get("compareArgs")
    if cargs is not None and cargs != args:
        out.append(("对比样例", cargs))
    for label, a in out:
        yield_names = names
    return [(label, a, names) for label, a in out]


def fmt_args(args: list, names: list[str]) -> str:
    parts = []
    for i, value in enumerate(args):
        name = names[i] if i < len(names) else "arg%d" % i
        parts.append("%s = %s" % (name, json.dumps(value, ensure_ascii=False)))
    return ", ".join(parts)


def print_statement(meta: dict) -> None:
    """只打印题面 —— 不含 summary（那是解法摘要）、notes、代码。"""
    print()
    print(_c("【%s】%s" % (meta["id"], meta["title"]), BOLD))
    print(_c("  %s" % meta.get("title_en", ""), DIM))
    print("  %s %s" % (
        _c(meta.get("difficulty", ""), YELLOW),
        _c(" ".join("#" + t for t in meta.get("tags", [])), CYAN),
    ))
    print(hr())
    statement = meta.get("statement")
    if statement:
        print(statement.strip())
    else:
        print(_c("（这道题还没写 statement，去 problems/%s 补一条）" % meta["_file"], RED))
    print(hr())
    for label, args, names in sample_inputs(meta):
        print("%s：%s" % (label, fmt_args(args, names)))
    print()
    print(_c("题面页： https://leetcode.cn/problems/%s/" % meta["id"], BLUE))


# ---------------------------------------------------------------- 计时

def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    return "%02d:%02d" % (seconds // 60, seconds % 60)


def wait_for_user(meta: dict) -> float:
    """计时开始，等用户按回车结束；每 30 秒提醒一次。"""
    limit = (meta.get("interview") or {}).get("minutes")
    print()
    print(_c("计时开始（建议 %s 分钟）。写完按回车结束，Ctrl-C 可随时放弃。" % (
        limit if limit else "20"), DIM))
    start = time.time()
    try:
        input(_c("  计时中… 按回车结束", DIM))
    except (EOFError, KeyboardInterrupt):
        print()
    return time.time() - start


def report(elapsed: float, meta: dict) -> None:
    limit = (meta.get("interview") or {}).get("minutes")
    line = "  用时 %s" % fmt_duration(elapsed)
    if limit:
        line += " / 建议 %d 分钟" % limit
        if elapsed > limit * 60:
            line += "  " + _c("超时了", RED)
        elif elapsed <= limit * 60 * 0.6:
            line += "  " + _c("很利落", GREEN)
    print(_c(line, BOLD))


# ---------------------------------------------------------------- 对拍

def _call(module, class_name: str, method: str, args: list):
    cls = getattr(module, class_name, None)
    if cls is None:
        raise SystemExit("你的文件里没有 class %s" % class_name)
    fn = getattr(cls(), method, None)
    if fn is None:
        raise SystemExit("你的 class %s 里没有方法 %s" % (class_name, method))
    return fn(*args)


def _same(got, want) -> bool:
    """完全一致算对；「答案是一组下标/配对」时，顺序不同也算对。"""
    if got == want:
        return True
    if isinstance(got, (list, tuple)) and isinstance(want, (list, tuple)):
        try:
            return sorted(map(_norm, got)) == sorted(map(_norm, want))
        except TypeError:
            return False
    return False


def _norm(v):
    return tuple(v) if isinstance(v, list) else v


def check(meta: dict, user_file: Path, extra_cases: list[list]) -> int:
    """把用户写的解跟仓库的标准解逐个用例对拍。"""
    code_path = ROOT / meta["code"]
    repo_src = code_path.read_text(encoding="utf-8")
    snippets = meta.get("snippets") or ["Solution"]
    std_class = snippets[0]
    methods = public_methods(repo_src, std_class)
    if not methods:
        raise SystemExit("仓库解 %s 里找不到可调用方法" % std_class)
    method = methods[0]
    names = param_names(meta)

    repo_module = _import(code_path)
    try:
        user_module = _import(user_file)
    except FileNotFoundError:
        raise SystemExit("找不到文件 %s" % user_file)
    except Exception as e:
        raise SystemExit("加载你的文件失败：%s: %s" % (type(e).__name__, e))

    user_classes = [n.name for n in ast.parse(user_file.read_text(encoding="utf-8")).body
                    if isinstance(n, ast.ClassDef)]
    user_class = std_class if std_class in user_classes else ("Solution" if "Solution" in user_classes else None)
    if user_class is None:
        raise SystemExit("你的文件里没有 class Solution（或 %s），现有 class：%s"
                         % (std_class, "、".join(user_classes) or "无"))

    cases = [a for _, a, _ in sample_inputs(meta)]
    cases.extend(extra_cases)
    if not cases:
        raise SystemExit("这题没有样例可对拍，用 --case 自己加：--case '[[1,2],3]'")

    print()
    print(_c("对拍：%s.%s（标准解 %s.%s）" % (user_class, method, std_class, method), BOLD))
    print(hr())
    passed = failed = 0
    for args in cases:
        try:
            want = _call(repo_module, std_class, method, args)
        except Exception as e:
            print("  标准解在这个用例上出错了，仓库可能有 bug：%s" % e)
            return 2
        try:
            got = _call(user_module, user_class, method, args)
        except Exception as e:
            failed += 1
            print("  %s 输入 %s" % (_c("❌", RED), fmt_args(args, names)))
            print("     你的解抛异常：%s: %s" % (type(e).__name__, e))
            continue
        if _same(got, want):
            passed += 1
            print("  %s 输入 %s → %s" % (_c("✅", GREEN), fmt_args(args, names),
                                          json.dumps(got, ensure_ascii=False)))
        else:
            failed += 1
            print("  %s 输入 %s" % (_c("❌", RED), fmt_args(args, names)))
            print("     你的输出：%s" % json.dumps(got, ensure_ascii=False))
            print("     正确输出：%s" % json.dumps(want, ensure_ascii=False))
    print(hr())
    print("  通过 %d / %d" % (passed, passed + failed))
    if failed:
        print(_c("  有 %d 个用例没过 —— 别急着看答案，先自己查边界。" % failed, YELLOW))
    else:
        print(_c("  全部一致 ✅ 现在去动画里看自己的解是怎么跑的。", GREEN))
    return 0 if not failed else 1


# ---------------------------------------------------------------- 看答案

def reveal(meta: dict) -> None:
    print()
    print(_c("【%s】%s · %s" % (meta["id"], meta["title"], meta.get("difficulty", "")), BOLD))
    print(hr())
    notes = meta.get("notes", "")
    if notes:
        print(notes.strip())
    else:
        print(_c("（这题还没写 notes）", RED))
    table = meta.get("complexity") or []
    if table:
        print()
        print(_c("复杂度对比", BOLD))
        for i, row in enumerate(table):
            print("  " + " | ".join(str(c) for c in row))
            if i == 0:
                print("  " + "-" * 40)
    print()
    print(_c("题面页： https://leetcode.cn/problems/%s/" % meta["id"], BLUE))


# ---------------------------------------------------------------- 主流程

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LeetCode 闭卷默写工具")
    parser.add_argument("--id", help="题号，如 0121")
    parser.add_argument("--tag", action="append", default=[], help="标签过滤，可重复或用逗号分隔")
    parser.add_argument("--difficulty", help="难度过滤：简单 / 中等 / 困难")
    parser.add_argument("--list", action="store_true", help="列出全部题目")
    parser.add_argument("--reveal", action="store_true", help="直接看讲解")
    parser.add_argument("--check", metavar="FILE", help="把你的解和仓库解对拍")
    parser.add_argument("--case", action="append", default=[],
                        help="额外用例，参数数组，如 --case '[[3,3],6]'（可重复）")
    args = parser.parse_args(argv)

    problems = load_problems()
    if not problems:
        raise SystemExit("problems/ 下没有 *.json")

    if args.list:
        print()
        print(_c("%-6s %-6s %-22s %s" % ("题号", "难度", "标题", "标签"), BOLD))
        print(hr())
        for m in problems:
            print("%-6s %-6s %-22s %s" % (
                m.get("id", ""), m.get("difficulty", ""), m.get("title", ""),
                " ".join("#" + t for t in m.get("tags", []))))
        print()
        return 0

    tags: list[str] = []
    for chunk in args.tag:
        tags.extend(t.strip() for t in chunk.split(",") if t.strip())

    if args.check:
        meta = pick(problems, args.id, tags, args.difficulty)
        extra = []
        for raw in args.case:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                raise SystemExit("--case 不是合法 JSON：%s" % e)
            if not isinstance(parsed, list):
                raise SystemExit("--case 要写成「参数数组」，例如 --case '[[3,3],6]'")
            extra.append(parsed)
        return check(meta, Path(args.check), extra)

    meta = pick(problems, args.id, tags, args.difficulty)

    if args.reveal:
        reveal(meta)
        return 0

    print_statement(meta)
    elapsed = wait_for_user(meta)
    report(elapsed, meta)
    print()
    print(_c("下一步：", DIM))
    print("  看讲解        python3 tools/mock.py --id %s --reveal" % meta["id"])
    print("  对拍你的解    python3 tools/mock.py --id %s --check 你的文件.py" % meta["id"])
    print("  浏览器里看动画 cd docs && python3 -m http.server 8000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
