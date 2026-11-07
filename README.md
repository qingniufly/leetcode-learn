# leetcode-learn

📚 LeetCode 解题笔记。每道题配一段**可交互的动图讲解**，而且动图不是手画的 —— 它由解题程序本身跑出来的执行轨迹生成，所以图里演示的每一步，都真的是代码在做的事。

🌐 **在线阅读**：<https://qingniufly.github.io/leetcode-learn/>

---

## 目录结构

```
.
├── code/            # 解题程序（按题号命名），自带自测与动画轨迹
│   ├── 0001_two_sum.py
│   ├── 0002_add_two_numbers.py
│   ├── 0003_longest_substring_without_repeating_characters.py
│   ├── 0070_climbing_stairs.py
│   └── 0118_pascals_triangle.py
├── problems/        # ← 每道题一份配置，加新题的主要入口
│   ├── 0001-two-sum.json
│   ├── 0002-add-two-numbers.json
│   ├── 0003-longest-substring.json
│   ├── 0070-climbing-stairs.json
│   └── 0118-pascals-triangle.json
├── tools/
│   └── build.py     # 生成器：problems/*.json + code/*.py ==> docs/
├── docs/            # 站点（index.html 与 problems/ 由生成器产出，勿手改）
│   ├── assets/      #   手写：style.css / site.js（通用播放器）
│   ├── templates/   #   手写：页面骨架
│   ├── index.html   #   生成：题目目录页
│   └── problems/    #   生成：每题一个页面
└── .github/workflows/pages.yml
```

---

## 动图是怎么来的

```
code/xxx.py  ──写一个 yield 轨迹的函数──▶  problems/xxx.json
                                              │
                                     tools/build.py 跑一遍
                                              │
                                   轨迹序列化成 JSON
                                              │
                                     docs/assets/site.js
                                     （通用播放器，只管播放）
```

播放器 `site.js` 里**没有任何题目相关逻辑**，它只认识一种帧格式：

```jsonc
{
  "i": 2,                       // 当前指针位置
  "j": 2,                       // 次指针（可选）
  "window": [2, 2],             // 当前区间（可选，会画托架）
  "bracketLabels": ["i", "j"],  // 可选：托架两端的标注
  "marks": [0, 1],              // 可选：需要特别标记的下标（如找到的答案对）
  "dropped": [0, 1],            // 可选：这一步被丢弃的下标
  "jump":  { "from": 0, "to": 2, "label": "start 0 → 2" },  // 可选：左端向前跳
  "backLabel": "回退重扫",       // 可选：指针向后回退时的标注
  "label": "这一步发生了什么",     // 说明文字
  "note": "补充说明",
  "codeLine": "start = last[ch] + 1",  // 源码片段，自动解析成行号做高亮
  "vars": { "last": {"a": 0}, "maxLen": 2 }  // 状态面板显示的变量
}
```

### 可视化类型（`demo.type`）

播放器把「怎么画」和「画什么」分开了，页面里没有一行题目专属代码：

| type | 画法 | 适合 | 已用于 |
| --- | --- | --- | --- |
| `array` | 一排 token + 当前指针 + 可选区间 / 配对高亮 | 滑动窗口、双指针、哈希表遍历、数组扫描 | 第 1、3 题 |
| `digits` | 两行数字 + 进位箭头 + 结果逐位生成 | 竖式加法 | 第 2 题 |
| `cells` | 一排表格单元 + 来源格高亮 + 浮标公式 | 动态规划表格、递归调用序列 | 第 70 题 |
| `triangle` | 居中的二维三角形 + 来源格高亮 | 杨辉三角这类二维递推结构 | 第 118 题 |

新增一种画法 = 在 `docs/assets/site.js` 的 `RENDERERS` 里注册一个渲染函数，
再把题目配置里的 `demo.type` 指过去。

---

## 如何添加一道新题

**只需要两个文件**，其余（目录页、上下题导航、代码标签页、动图播放器、样式）全自动。

### 1️⃣ 写解题程序 `code/<题号>_<题目名>.py`

里面放 `Solution` 类，再加一个**轨迹函数**，把执行过程 `yield` 出来：

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        ...

def trace(s: str):
    """产出动画帧：tools/build.py 会把它变成前端可播放的轨迹。"""
    for i, ch in enumerate(s):
        yield {
            "i": i, "j": 0, "window": [0, i], "dropped": [],
            "jump": None,
            "label": f"读到 '{ch}'",
            "note": f"第 {i + 1} 步",
            "codeLine": "return len(s)",     # 会自动匹配到源码行并高亮
            "vars": {"ch": ch},
        }
```

`codeLine` 写**源码片段**即可，生成器会自动在代码块里找到对应行。

### 2️⃣ 写题目配置 `problems/<题号>-<slug>.json`

```jsonc
{
  "id": "0011",
  "slug": "0011-container-with-most-water",
  "title": "盛最多水的容器",
  "title_en": "Container With Most Water",
  "difficulty": "中等",                     // 简单 / 中等 / 困难
  "tags": ["双指针", "贪心"],
  "summary": "一句话说清这题在干嘛。",
  "notes": "讲解文案，支持段落、- 列表、> 引用、`行内代码`、**加粗**。",
  "code": "code/0011_container_with_most_water.py",
  "snippets": ["Solution"],                 // 要在页面上展示的 class
  "complexity": [["写法", "时间", "空间"], ["双指针", "O(n)", "O(1)"]],
  "demo": {
    "type": "array",                        // 用哪种画法：array / digits
    "args": [[1, 8, 6, 2], 9],              // 传给轨迹函数的参数（任意个数）
    "compareArgs": [[...], 9],              // 可选：横向对比用的另一组参数
    "lanes": [                              // 一条轨道 = 一种写法
      { "name": "双指针版", "badge": "O(n)", "variant": "good",
        "code": "Solution", "trace": "trace", "showCode": true }
    ]
  }
}
```

> `args` 就是传给 Python 轨迹函数的实参，轨迹函数返回什么，页面上就画什么。
> 页面上的元素（方块里的数字、竖式加法的两行）会**自动从 `args` 推导**，不用重复写。
```

> `lanes` 有 **2 条以上**时，页面会自动多出一个「横向对比」区块，把它们并排播放，
> 并自动算出各自的步数与倍数差。

### 3️⃣ 构建 & 预览

```bash
python3 tools/build.py      # 生成 docs/index.html 与 docs/problems/*.html
cd docs && python3 -m http.server 8000
```

推送 `main` 后，CI 会自动跑每道题的自测 → 校验配置 → 构建 → 部署 Pages。

---

## 题目列表

| # | 题目 | 难度 | 核心解法 | 可视化 |
| --- | --- | --- | --- | --- |
| 1 | 两数之和 | 简单 | 哈希表一次遍历 | `array` + 配对高亮 |
| 2 | 两数相加 | 中等 | 链表模拟竖式加法 | `digits` 竖式加法 |
| 3 | 无重复字符的最长子串 | 中等 | 滑动窗口 + 字典记录上次出现位置 | `array` + 区间托架 |
| 70 | 爬楼梯 | 简单 | 动态规划 / 斐波那契（滚动变量） | `cells` + DP 表格 |
| 118 | 杨辉三角 | 简单 | 逐行推导（上一行相邻两格相加） | `triangle` + 来源格高亮 |

🌐 [在线阅读](https://qingniufly.github.io/leetcode-learn/)

### 本期要点回顾（LeetCode 3）

> 最容易写错的一行是 `if ch in last and last[ch] >= start:` —— 这个 `>= start` 不能省。
> 否则左端会倒退，已淘汰的重复字符会重新进入窗口（`"abba"` 会错成 3）。

> 也不要「左端只回退一格再重扫」：结果虽然对，但最坏 `O(n²)`，串长 `n` 时内层循环跑约 `n(n+1)/2` 次，
> `n = 5×10⁴` 时约需 100 秒，必定超时。

---

## 运行代码

```bash
python3 code/0003_longest_substring_without_repeating_characters.py
```

输出：

```
[ok] 15 个边界用例全部通过
[ok] 3000 组随机串与暴力解结果一致

最坏用例（m 个互不相同字符 + 末尾重复最后一个字符）
      n |          重启版扫描次数 |          字典版扫描次数 |       倍数
     11 |               66 |               11 |     6.0x
    101 |             5151 |              101 |    51.0x
   1001 |           501501 |             1001 |   501.0x
```

## 校验配置

```bash
python3 tools/build.py --check     # 只校验 problems/*.json 与轨迹函数对不对得上
```
