# AGENTS.md —— 给 AI Agent / 新会话的工作说明

> 本文件是**规则**，README.md 是**给人看的科普**。
> 两者冲突时，以本文件的「硬门槛」为准；想理解「为什么这么做」，去看 README。

## 0. 这是个什么仓库

一个 LeetCode 解题笔记仓库。**每道题 = 一份能跑的自测程序 + 一份题目配置 + 一段由程序执行轨迹生成的交互动图**。

```
code/<id>_<slug>.py          手写：Solution 类 + 轨迹函数 + 自测
problems/<id>-<slug>.json    手写：题目配置（文案、标签、动图轨道）
        ↓ tools/build.py 跑一遍轨迹函数
docs/index.html + docs/problems/*.html   生成物（CI 里现生成，不提交）
```

**核心约束：动图里的每一帧都是程序真实跑出来的**，不是手画的。所以轨迹函数必须真的执行算法。

---

## 1. 开始动手前

- **shell 命令一律加 `rtk` 前缀**：`rtk git status`、`rtk read <file>`、`rtk grep <pat>`、`rtk ls <path>`……没有对应过滤器的命令会原样执行，安全。没装 `rtk` 就去掉前缀，功能不受影响。
- **Serena 已配置**（`.serena/project.yml`，`language: python`）。要做符号级检索时先激活项目，别整文件读。
- **只用 Python 标准库**：`tools/build.py` 和所有 `code/*.py` 都是零第三方依赖，CI 用 Python 3.11 跑。不要引入 numpy/pytest 之类。
- 动图播放器是**通用**的：`docs/assets/site.js` 里**不允许出现任何题目相关逻辑**。要新的画法，就去 `RENDERERS` 注册一个通用渲染器。

---

## 2. 仓库地图

| 路径 | 作用 | 手改？ |
|---|---|---|
| `code/<id>_<slug>.py` | 解题程序：`Solution` 类 + 轨迹函数 + `_self_test()` | ✅ 手写，提交 |
| `problems/<id>-<slug>.json` | 题目配置：标题/难度/标签/讲解文案/复杂度表/动图轨道 | ✅ 手写，提交 |
| `tools/build.py` | 生成器：跑轨迹函数 → 序列化成 JSON → 渲染页面 | ✅ 手写，提交 |
| `tools/mock.py` | 闭卷默写 CLI：抽题 → 只给题面 → 计时 → 跟仓库解对拍 | ✅ 手写，提交 |
| `docs/assets/site.js` | 通用播放器 + 渲染器注册表 | ✅ 手写，提交 |
| `docs/assets/style.css` | 站点样式 | ✅ 手写，提交 |
| `docs/templates/*.html` | 页面骨架（`{{占位符}}` 模板） | ✅ 手写，提交 |
| `docs/index.html`、`docs/problems/` | **生成物**，已 `.gitignore` | ❌ 别手改、别提交 |
| `.github/workflows/pages.yml` | CI：跑自测 → `--check` → 构建 → 部署 Pages | ✅ 手写，提交 |

`docs/` 下只有 `assets/` 和 `templates/` 进版本库，页面由 CI 现生成。

---

## 3. 加一道新题：完整 SOP

### Step 0 · 读一遍现有题
挑一道结构相近的（`code/` 下有 10 道），照着它的骨架写。README 的「如何添加一道新题」有最小示例。

### Step 1 · 命名
| 东西 | 规则 | 例子 |
|---|---|---|
| 题号 id | **4 位零填充**的字符串 | `0005`、`0338`、`0392` |
| 代码文件 | `code/<id>_<英文短名>.py`（**下划线**） | `code/0005_longest_palindromic_substring.py` |
| 题目配置 | `problems/<id>-<英文短名>.json`（**连字符**） | `problems/0005-longest-palindromic-substring.json` |
| slug | `<id>-<英文短名>`，页面文件名由它决定 | `0005-longest-palindromic-substring` |

code 文件名和 slug 用**同一个英文短名**（只有第 3 题是历史例外，code 文件名写得更全：
`0003_longest_substring_without_repeating_characters.py` vs slug `0003-longest-substring`）。

id 用零填充后，字符串排序 == 数值排序，目录页的上下题导航才不会乱。

### Step 2 · 写 `code/<id>_<slug>.py`
见 §4。

### Step 3 · 写 `problems/<id>-<slug>.json`
见 §5。

### Step 4 · 选渲染器、造帧
见 §6。**每个轨道至少要有意义地动起来**——不要出现「一帧都没变」的轨道。

### Step 5 · 补面试相关内容 + 更新 README.md
- `problems/<id>-<slug>.json` 里写好 `statement`（题面）和 `interview`（面试官视角），见 §5.3
- README.md「题目列表」表格加一行（按题号插入）
- 补一节「### 本期要点回顾（LeetCode N）」：写这道题**最容易踩的坑**，而不是复述解法

### Step 6 · 本地校验（三连，缺一不可）
```bash
python3 code/<你的文件>.py          # 自测必须全绿
python3 tools/build.py --check      # 配置与轨迹函数必须对得上
python3 tools/build.py              # 生成站点
cd docs && python3 -m http.server 8000   # 浏览器里看一遍动画
```
`--check` 会**真的执行每条轨道的轨迹函数**，所以死循环/异常会当场暴露。

浏览器里还要顺手点一遍**「进入盲写」**：确认题面、样例、计时器都对，其余内容确实藏起来了。

### Step 7 · 提交 & 推送
```bash
git add code/ problems/ README.md
git commit -m "feat: 加入 LeetCode <N> <标题>"
git push origin main
```
推 `main` 会触发 CI：跑全部自测 → 校验配置 → 构建 → 部署到 GitHub Pages。

---

## 4. 代码文件约定

```python
"""
LeetCode <N>. <中文标题>
<English Title>

<复杂度>

题意：...
思路：...
边界：...
"""


class Solution:
    """一句话说明这个类是什么。"""

    def <LeetCode 上的方法名>(self, ...) -> ...:
        ...


class SolutionXxx:          # 对照写法（另一种解法），命名带语义
    """❌/对照：说明它为什么行或不行。"""


def trace(...):             # 主轨道的轨迹函数
    """产出动画帧：yield 一个 dict 就是一帧。"""
    yield {...}


def trace_xxx(...):         # 其它轨道的轨迹函数
    ...


def _self_test() -> None:
    ...


if __name__ == "__main__":
    _self_test()
```

**硬性要求**

- 类名 `Solution` + 与 LeetCode **完全一致**的方法名；第二种写法另起 `SolutionXxx`，别把两个解法塞进一个类。
- **保留用户自己的原写法**做对照是本仓库的传统（第 118、121 题都这么做的）。原写法有 bug 就在 docstring 里写清楚 bug 在哪，并在 `snippets` 里保留它。
- 模块 docstring、类 docstring、行内注释**全部用中文**；注释讲「为什么」，不写「做了什么」。
- 轨迹函数的**参数必须和 `demo.args` 对得上**（`args: [7]` → `def trace(n)`；`args: ["abc","ahbgdc"]` → `def trace(s, t)`）。
- **轨迹函数必须能终止**。要展示的写法本身会死循环/超时，就照第 121 题那样在轨迹里加「卡死检测」，把卡住的那一刻画出来（`while` 一圈没推进就停帧并说明原因），**不要**把会挂起的代码直接放进轨迹。
- `_self_test()` 里至少要有这三样：
  1. **边界用例**（空、单元素、全相同、答案不唯一……）
  2. **与独立的暴力解对拍**（暴力解要另写一份，不能调用被测函数）
  3. **动图终点 == 代码答案**（遍历若干组输入，断言轨迹最后一帧给出的答案和解题程序的输出一致）
- 代码里不要留 `print` 调试语句；自测的 `print` 用 `[ok] ...` 前缀。

---

## 5. 题目配置约定（`problems/*.json`）

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 4 位零填充题号 |
| `slug` | ✅ | `<id>-<英文短名>` |
| `title` / `title_en` | ✅ | 中文名 / 英文名 |
| `difficulty` | ✅ | 只能是 `简单` / `中等` / `困难`（页面上要靠它上色） |
| `tags` | ✅ | 数组。**优先复用现有词**：动态规划、数组、双指针、贪心、字符串、哈希表、滑动窗口、位运算、链表、数学、模拟、中心扩展、递归……标签会在目录页汇总成标签云 |
| `summary` | ✅ | 一句话 |
| `statement` | ✅ | **题面**（不含解法提示），盲写模式和 `mock.py` 只显示它 |
| `notes` | ✅ | 讲解正文（markdown）。见 §5.1 |
| `code` | ✅ | 指向 `code/` 下的 py 文件 |
| `snippets` | ✅ | 页面上要展示的 class 名列表，必须在代码文件里真实存在 |
| `complexity` | ✅ | 二维数组，第一行是表头 |
| `interview` | ✅ | 「面试官视角」：3 分钟话术 + 高频坑 + 追问链。见 §5.3 |
| `demo` | ✅ | 见 §5.2 |

### 5.1 `notes` 支持的 markdown
段落、`- ` 列表、`> ` 引用、` ``` ` 围栏代码块、`` `行内代码` ``、`**加粗**`、以及 **markdown 表格**（必须有 `|---|---|` 分隔行）。

不要用：标题层级 `#`（会原样显示成正文，不会变成标题）、HTML、图片、列表编号 `1.`（不渲染，序号会原样显示）。

### 5.2 `demo` 结构

```jsonc
"demo": {
  "type": "array",              // 渲染器，见 §6
  "args": [7],                  // 传给轨迹函数的实参（数组）
  "compareArgs": ["cbbd"],      // 可选：横向对比区用的另一组实参（同一批轨道函数）
  "compareTitle": "换个输入 …", // 对比区的标题，要说明这次换输入是为了看什么
  "lanes": [
    {
      "name": "中心扩展（推荐提交）",
      "badge": "O(n²) / O(1)",  // 右上角小徽章
      "variant": "good",        // good / warn / neutral —— 决定徽章配色
      "code": "Solution",       // 页面上展示这个 class 的代码（也是 codeLine 高亮的范围）
      "trace": "trace",         // 代码文件里的轨迹函数名
      "tokens": ["a","b"],       // 可选：array 渲染器的格子内容（默认从 args[0] 推）
      "showCode": true          // 是否在下方显示代码面板（只有第一条轨道有效）
    }
  ]
}
```

- `lanes` 建议 **2 条**：一条推荐解法（`variant: good`），一条对照写法（`variant: warn`）。
- 轨道数 ≥ 2 时页面自动多出「横向对比」区块，把所有轨道并排播放，并自动算出步数差异。
- **两条轨道给的输入可以不同**（对比区用 `compareArgs`），但要在 `compareTitle` 里说清楚换输入是为了看什么。

### 5.3 `statement` 与 `interview`（面试准备用）

```jsonc
"statement": "给定一个整数数组 nums 和一个整数 target……",   // 题面，不含解法提示

"interview": {
  "minutes": 15,                 // 建议用时（分钟），盲写模式的计时器会显示
  "pitch": "3 分钟怎么讲……",     // markdown，同 notes 的子集
  "pitfalls": ["最容易踩的坑……"], // 字符串数组
  "followups": [                // 追问链：页面上折叠，点开才看答案
    { "q": "面试官会追问什么？", "a": "怎么答（markdown）" }
  ]
}
```

**`statement` 的规矩**

- 只写**题目本身**（输入、输出、约束），**不要写解法** —— `summary` 已经是解法摘要了。
- 盲写模式（页面上）和 `tools/mock.py` 只显示 `statement`，所以它就是「闭卷时看到的全部信息」。
- 别把 LeetCode 原题抄进来，用自己的话概括即可。

**`interview` 的规矩**

- `pitch` 写**能直接说出口的话**：「这题考的是什么 → 为什么用这个结构 → 复杂度多少 → 会被追问什么」。
  不是复述 `notes`，是换个「面试时怎么说」的口气。
- `pitfalls` 写**最容易踩的坑**（和 `notes` 末尾的「边界」呼应），别写泛泛的注意事项。
- `followups` 按**追问的先后顺序**排，从最容易被问的开始；`a` 要给出「面试官口吻」的答案。
- `minutes` 按难度给：简单 12–15、中等 20–25、困难 25–30。

**校验**：`tools/build.py --check` 会检查这几个字段的类型（`pitch` 必须是字符串、`pitfalls` 必须是字符串数组、`followups` 每项必须含 `q`），格式错了当场报错。

---

## 6. 动图帧约定

一帧就是一个 dict。**通用字段**（所有渲染器都认）：

| 字段 | 作用 |
|---|---|
| `label` | 画面下方的主说明文字（会出现在每一步） |
| `note` | 补充说明（灰色小字） |
| `vars` | 状态面板 `{"变量名": 值}`，值只能是标量 |
| `codeLine` | **源码片段**，用来高亮代码面板的某一行 |

**`codeLine` 规则**：必须是**该轨道 `code` 指向的那个 class 里、某一行的原文片段**（构建时会逐行匹配）。写 `"profit = price - min_price"` 这种；写成 `"profit = price - minPrice"` 就匹配不上（静默不高亮）。

各渲染器的专属字段：

| `demo.type` | 画什么 | 帧字段 |
|---|---|---|
| `array` | 一排格子 + 指针 + 区间 | `i` 当前指针、`j` 次指针、`window:[a,b]` 区间托架、`bracketLabels` 托架两端文字、`marks` 描边标记、`dropped` 虚线丢弃、`jump:{from,to,label}` 跳跃、`backLabel` 指针回退时的说明 |
| `cells` | 一排表格单元（DP 表格） | `values` 单元格文字数组、`col` 当前格、`from` 来源格下标数组、`caption` 浮标 |
| `triangle` | 居中三角形 | `rows` 二维数组、`row`/`col` 当前格、`from` 来源格 `[[r,c],...]`、`caption` |
| `row` | 横向多条带（最后一条是当前行） | `rows` 带数组、`labels` 每条带的标题、`row` 当前带、`col` 当前列、`from` 来源格 `[[带,列],...]` |
| `digits` | 竖式加法 | `col` 当前列（从右数）、`digit` 本位、`carry` 进位、`result` 已产出的位 |

**帧的硬要求**

- 帧里出现的**任何下标都不能越界**，否则前端直接报错、整页动画卡住。
- 每帧要能**独立看懂**：观众可能只看到这一帧。
- `window` / `marks` / `dropped` 表达不同含义，别混用：区间=当前工作范围，描边=重点/已找到，虚线=被淘汰。
- `i` 单调递增时不会有箭头；一旦回退，渲染器会画一条弧线并写「回退」，这时用 `backLabel` 换成真实含义（如「换行：i ←」）。

---

## 7. 硬门槛（CI 会卡住你）

推 `main` 后 CI 依次跑：

1. `for f in code/*.py; do python3 "$f"; done` —— **每一道题的自测都必须全绿**，包括你新加的
2. `python3 tools/build.py --check` —— 配置必须合法：代码文件存在、轨迹函数存在、`code` 指向的 class 存在、`snippets` 里的 class 存在；并且**所有轨道的轨迹函数会被真实执行一遍**
3. `python3 tools/build.py` —— 页面必须能渲染出来

任何一步挂掉，CI 红，站点不会更新。

---

## 8. 提交与发布

- **一题一个 commit**，消息用中文：`feat: 加入 LeetCode <N> <标题>`；改动文案用 `docs:`；修 bug 用 `fix:`。
- 提交前确认 `git status` 里**没有** `docs/index.html`、`docs/problems/`（它们已被忽略）。
- 推 `main` = 发布。推之前本地过一遍 §3 Step 6。
- 站点地址：<https://qingniufly.github.io/leetcode-learn/>

---

## 9. 常见坑

| 现象 | 原因 |
|---|---|
| 构建报「找不到 class X」 | `snippets` 或轨道 `code` 里的类名与 py 文件不一致 |
| 动画不播放 / 页面报错 | 帧里的下标越界，或轨迹函数抛异常 |
| 代码面板不高亮 | `codeLine` 不是该 class 某一行的原文 |
| 轨迹函数把构建卡死 | 轨迹里跑了会死循环的代码 → 参照第 121 题加「卡死检测」 |
| 表格/列表显示成一坨 | `notes` 里用了不支持的 markdown（`#` 标题、编号列表、图片） |
| 改了 `docs/` 里的 html 但线上没变 | 生成物不入库，推 `main` 让 CI 重新构建 |
| 目录页顺序错乱 | 题号 id 没做 4 位零填充 |
| 盲写模式没生效 | `site.js` 里 `initBlind()` 没被 `boot()` 调用，或 CSS 少了 `body.is-blind` 那条规则 |
| `mock.py --check` 说找不到 class | 你的文件里类名要叫 `Solution`（或仓库 `snippets[0]` 那个名字），方法名要和仓库一致 |

---

## 10. 闭卷默写与面试模式

这个仓库不只用来「看题解」，还用来**准备面试**。三条路径：

### 10.1 网页盲写模式

每道题页面顶部有一条「闭卷默写」工具条：

- 点「进入盲写」→ **题面之外的内容全部隐藏**（动图、讲解、代码、复杂度、面试官视角），只留题面 + 计时器
- 计时器按 `interview.minutes` 倒数，超时会标红；「重置计时」可以重新开始
- 点「解除盲写」→ 全部内容回来，计时归零
- 状态存在 `sessionStorage`，翻到下一题仍是盲写；也可以用 `?blind=1` 直接进入

目录页有「随机盲写一题」按钮，直接随机进一题的盲写模式。

> 盲写模式是 `site.js` 里 `initBlind()` 干的活，靠给 `<body>` 加 `is-blind` 类 + CSS 隐藏
> `main > section:not(#blind)` 实现。**播放器里不允许出现任何题目相关逻辑**，这条规则同样适用。

### 10.2 命令行闭卷默写 `tools/mock.py`

```bash
python3 tools/mock.py                              # 随机抽一题，只给题面，开始计时
python3 tools/mock.py --list                       # 列出全部题目
python3 tools/mock.py --id 0121                    # 指定题号
python3 tools/mock.py --tag 动态规划,哈希表          # 按标签抽
python3 tools/mock.py --difficulty 简单             # 按难度抽
python3 tools/mock.py --id 0121 --reveal           # 直接看讲解 + 复杂度表
python3 tools/mock.py --id 0001 --check mine.py    # 把你写的解和仓库解对拍
python3 tools/mock.py --id 0001 --check mine.py --case '[[3,3],6]'   # 加自定义用例
```

- 题面只来自 `statement` + `demo.args`，**不泄露** `summary`（那是解法摘要）、`notes` 和代码
- 计时结束会报用时，并对照 `interview.minutes` 给评价
- `--check` 会导入你的文件和仓库的标准解，用 `demo.args` / `demo.compareArgs` / `--case` 逐个对拍，
  答案是一组下标时**顺序不同也算对**
- 对拍标准解 = 仓库里 `snippets[0]` 那个 class 的第一个方法

### 10.3 「面试官视角」区块

每道题页面上的「面试官视角」来自 `interview` 字段（§5.3）：3 分钟话术、高频坑、追问链（折叠）。
**写的时候按「面试时怎么说」来写**，不要复述 `notes`。

---

## 11. 参考

- `README.md` —— 目录结构、动图原理、每种可视化类型的用途、题目列表、要点回顾
- `docs/assets/site.js` —— 播放器和全部渲染器的实现（帧字段以它为准）
- `tools/build.py` —— 生成器（配置字段以它为准）
- `tools/mock.py` —— 闭卷默写 CLI（抽题 / 计时 / 对拍）
