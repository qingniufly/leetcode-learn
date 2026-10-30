# leetcode-learn

📚 LeetCode 解题笔记。

每道题分两处存放：

| 位置 | 内容 |
| --- | --- |
| [`code/`](code/) | 可直接提交的解题程序，附带自测脚本 |
| [`docs/`](docs/) | 动图讲解，通过 GitHub Pages 发布 |

🌐 **在线阅读**：<https://qingniufly.github.io/leetcode-learn/>

---

## 本期题目

| # | 题目 | 难度 | 核心解法 | 动图讲解 |
| --- | --- | --- | --- | --- |
| 3 | 无重复字符的最长子串 | 中等 | 滑动窗口 + 字典记录上次出现位置 | [逐步演示 + 复杂度对比](https://qingniufly.github.io/leetcode-learn/) |

### 题目回顾

给定字符串 `s`，找出不含重复字符的最长**连续**子串的长度。

```
输入: "abba"      输出: 2      （"ab" 或 "ba"）
输入: "abcabcbb"  输出: 3      （"abc"）
输入: "pwwkew"    输出: 3      （"wke"）
```

### 解法要点

用字典 `last` 记录每个字符**上一次出现的位置**，右指针 `i` 从左到右推进：

- 若 `last[ch] >= start`，说明 `ch` 在当前窗口内重复，把左端 `start` **直接跳到** `last[ch] + 1`；
- 若 `last[ch] < start`，说明那次出现早已滑出窗口，**左端不动**；
- 以 `i` 结尾的最长无重复子串长度就是 `i - start + 1`，取全程最大值。

两个容易踩的坑：

1. **`>= start` 不能省。** 否则左端会倒退，已经淘汰的重复字符会重新进入窗口（`"abba"` 会错成 3）。
2. **不要「左端只回退一格再重扫」。** 结果虽然正确，但最坏复杂度是 `O(n²)` —— 串长 `n` 时内层循环要跑约 `n(n+1)/2` 次，`n = 5×10⁴` 时约需 100 秒，必定超时。

---

## 运行代码

```bash
# 运行自测：边界用例 + 3000 组随机对拍 + 最坏用例耗时对比
python3 code/0003_longest_substring_without_repeating_characters.py
```

输出示例：

```
[ok] 15 个边界用例全部通过
[ok] 3000 组随机串与暴力解结果一致

最坏用例（m 个互不相同字符 + 末尾重复最后一个字符）
      n |          重启版扫描次数 |          字典版扫描次数 |       倍数
     11 |               66 |               11 |     6.0x
    101 |             5151 |              101 |    51.0x
   1001 |           501501 |             1001 |   501.0x
```

## 本地预览动图讲解

```bash
cd docs && python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 目录结构

```
.
├── code/                                  # 解题程序
│   └── 0003_longest_substring_without_repeating_characters.py
├── docs/                                  # GitHub Pages 站点
│   ├── index.html                         # 动图讲解页面
│   └── assets/
│       ├── style.css
│       └── app.js
└── .github/workflows/pages.yml            # Pages 自动部署
```

## 贡献新题目

1. 在 `code/` 下新增 `<题号>_<题目名>.py`，保留 `Solution` 类为提交版本，并在 `__main__` 里加自测；
2. 在 `docs/` 里加对应的讲解页面，并在 `index.html` 的题目表格里登记；
3. 推送到 `main`，Pages 会自动重新部署。
