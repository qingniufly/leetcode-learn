"""
LeetCode 392. 判断子序列
Is Subsequence

时间复杂度 O(|t|)，空间复杂度 O(1)。

题意：给两个字符串 s 和 t，判断 s 是不是 t 的**子序列**
      （子序列 = 可以跳过若干字符，但不能改变相对顺序）。

        s = "abc"，t = "ahbgdc"  →  True   （a…b…c 依次都在）
        s = "axc"，t = "ahbgdc"  →  False  （x 在 t 里根本没出现）

思路
    双指针 / 贪心：用指针 i 指向 s 里「下一个要配的字符」，
    从左往右扫 t，遇到能配的就配上一个、i 往后挪一格。
    扫完整个 t 之后，i 走完了 s，就说明 s 是 t 的子序列。

    为什么这样贪心是对的？
    同一个字符，**越早配上去，留给后面的字符就越多** ——
    任何「晚一点配」的方案都不会更好，所以能配就配，不必犹豫。

两种写法
    · Solution      —— 双指针 / 贪心，O(|t|) 时间、O(1) 空间，推荐提交
    · SolutionByDP  —— DP（就是 1143 最长公共子序列的思路），
                       O(|s|·|t|) 时间、O(|s|·|t|) 空间，只作对照
"""


class Solution:
    """双指针 / 贪心版：扫一遍 t，一个指针指向 s 里下一个要配的字符。"""

    def isSubsequence(self, s: str, t: str) -> bool:
        i = 0
        for j, ch in enumerate(t):
            if i < len(s) and s[i] == ch:
                i += 1
        return i == len(s)


class SolutionByDP:
    """DP 版：dp[i][j] = s[:i] 是不是 t[:j] 的子序列。

    转移：要么跳过 t[j-1]（dp[i][j-1]），
          要么把 t[j-1] 配给 s[i-1]（要求字符相同，且 dp[i-1][j-1] 为真）。
    """

    def isSubsequence(self, s: str, t: str) -> bool:
        m, n = len(s), len(t)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        for j in range(n + 1):
            dp[0][j] = True              # 空串是任何串的子序列
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                dp[i][j] = dp[i][j - 1] or (s[i - 1] == t[j - 1] and dp[i - 1][j - 1])
        return dp[m][n]


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(s, t):
    """双指针版：逐帧展示 t 的扫描过程，s 的字符是怎么一个个配上号的。"""
    i = 0
    matched_s = []
    matched_t = []

    for j, ch in enumerate(t):
        hit = i < len(s) and s[i] == ch
        if hit:
            matched_s.append(i)
            matched_t.append(j)
            i += 1
        want = s[i] if i < len(s) else "（s 已全部配完）"

        yield {
            "rows": [list(s), list(t)],
            "labels": ['s = "%s"' % s, 't = "%s"' % t],
            "row": 1,
            "col": j,
            "from": [[0, k] for k in matched_s] + [[1, k] for k in matched_t],
            "caption": "t[%d] = '%s'" % (j, ch),
            "label": ("t[%d] = '%s' 正是 s[%d] 要的 '%s' —— 配上了！s 指针移到 s[%d] = '%s'。"
                      % (j, ch, i - 1, ch, i, want)) if hit else
                     ("t[%d] = '%s'，现在要的是 s[%d] = '%s'，对不上 —— 跳过，继续往右找。"
                      % (j, ch, i, want)),
            "note": "贪心：能配就配，配得越早，留给后面的字符越多。",
            "vars": {"t 位置": j, "s 位置": i, "已配对": len(matched_s)},
            "codeLine": "if i < len(s) and s[i] == ch:",
        }

    ok = i == len(s)
    yield {
        "rows": [list(s), list(t)],
        "labels": ['s = "%s"' % s, 't = "%s"' % t],
        "row": 1,
        "col": len(t) - 1,
        "from": [[0, k] for k in matched_s] + [[1, k] for k in matched_t],
        "caption": "结论",
        "label": "扫完整个 t：s 配上了 %d / %d 个字符 → %s"
                 % (len(matched_s), len(s), "s 是 t 的子序列 ✅" if ok else "s 不是 t 的子序列 ❌"),
        "note": "整个过程只把 t 扫了一遍，额外空间 O(1)。",
        "vars": {"s 位置": i, "已配对": len(matched_s)},
        "codeLine": "return i == len(s)",
    }


def trace_dp(s, t):
    """DP 版：逐格推出 dp[i][j]（s[:i] 是不是 t[:j] 的子序列）。

    表按行滚动：上面一条是 dp[i-1][*]，下面一条是正在算的 dp[i][*]。
    """
    m, n = len(s), len(t)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    for j in range(n + 1):
        dp[0][j] = True

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = s[i - 1] == t[j - 1]
            dp[i][j] = dp[i][j - 1] or (match and dp[i - 1][j - 1])

            prev_row = ["T" if dp[i - 1][k] else "F" for k in range(n + 1)]
            cur_row = [("T" if dp[i][k] else "F") if k <= j else None for k in range(n + 1)]

            src = [[1, j - 1], [0, j - 1]]          # dp[i][j-1] 与 dp[i-1][j-1]
            if match:
                src.append([0, j])                # 字符相同，还要看 dp[i-1][j]

            if match:
                text = ("dp[%d][%d]：s[%d]='%s' 和 t[%d]='%s' 相同，"
                        "而 dp[%d][%d] = %s → dp[%d][%d] = True"
                        % (i, j, i - 1, s[i - 1], j - 1, t[j - 1],
                           i - 1, j - 1, "真" if dp[i - 1][j - 1] else "假", i, j))
            else:
                text = ("dp[%d][%d]：s[%d]='%s' 和 t[%d]='%s' 不同，配不上，"
                        "只能跳过 t[%d] → dp[%d][%d] = dp[%d][%d] = %s"
                        % (i, j, i - 1, s[i - 1], j - 1, t[j - 1], j - 1,
                           i, j, i, j - 1, "真" if dp[i][j - 1] else "假"))

            yield {
                "rows": [prev_row, cur_row],
                "labels": ["dp[%d][*]" % (i - 1), "dp[%d][*]" % i],
                "row": 1,
                "col": j,
                "from": src,
                "caption": "dp[%d][%d] = %s" % (i, j, "T" if dp[i][j] else "F"),
                "label": text,
                "note": "T = s 的前 i 个字是 t 的前 j 个字的子序列；F = 不是。",
                "vars": {"i": i, "j": j, "s[i-1]": s[i - 1], "t[j-1]": t[j - 1],
                         "dp[i][j]": "T" if dp[i][j] else "F"},
                "codeLine": "dp[i][j] = dp[i][j - 1] or (s[i - 1] == t[j - 1] and dp[i - 1][j - 1])",
            }

    yield {
        "rows": [["T" if dp[m - 1][k] else "F" for k in range(n + 1)],
                 ["T" if dp[m][k] else "F" for k in range(n + 1)]],
        "labels": ["dp[%d][*]" % (m - 1), "dp[%d][*]" % m],
        "row": 1,
        "col": n,
        "from": [[1, n - 1], [0, n - 1]],
        "caption": "结论",
        "label": "结论：dp[%d][%d] = %s → %s"
                 % (m, n, "T" if dp[m][n] else "F",
                    "s 是 t 的子序列 ✅" if dp[m][n] else "s 不是 t 的子序列 ❌"),
        "note": "为了算这一个格子，DP 版把 |s|×|t| 个格子全推了一遍。",
        "vars": {"dp[%d][%d]" % (m, n): "T" if dp[m][n] else "F"},
        "codeLine": "return dp[m][n]",
    }


def _self_test() -> None:
    s = Solution()
    d = SolutionByDP()

    assert s.isSubsequence("abc", "ahbgdc") is True
    assert s.isSubsequence("axc", "ahbgdc") is False
    assert s.isSubsequence("", "ahbgdc") is True
    assert s.isSubsequence("abc", "") is False
    assert s.isSubsequence("a", "a") is True
    print("[ok] 边界用例：True / False / 空串 / 单字符 都正确")

    # 独立实现一份参考解：贪心双指针（另一种写法）
    def reference(a, b):
        k = 0
        for ch in b:
            if k < len(a) and a[k] == ch:
                k += 1
        return k == len(a)

    import itertools
    import random
    random.seed(11)
    checked = 0
    for _ in range(400):
        a = "".join(random.choice("ab") for _ in range(random.randint(0, 5)))
        b = "".join(random.choice("ab") for _ in range(random.randint(0, 7)))
        assert s.isSubsequence(a, b) == reference(a, b), "a=%r b=%r 不一致" % (a, b)
        assert d.isSubsequence(a, b) == reference(a, b), "DP 版 a=%r b=%r 不一致" % (a, b)
        checked += 1
    # 再把所有长度为 3 的 s 和长度为 4 的 t 全枚举一遍
    for a in ("".join(p) for p in itertools.product("ab", repeat=3)):
        for b in ("".join(p) for p in itertools.product("ab", repeat=4)):
            assert s.isSubsequence(a, b) == reference(a, b), "a=%r b=%r 不一致" % (a, b)
            assert d.isSubsequence(a, b) == reference(a, b), "DP 版 a=%r b=%r 不一致" % (a, b)
            checked += 1
    print("[ok] %d 组随机 + 穷举用例，两种写法都与参考解一致" % checked)

    # 动图轨迹的终点必须和解题程序的输出一致
    for a, b in (("abc", "ahbgdc"), ("axc", "ahbgdc"), ("", "abc"), ("a", "a")):
        frames = list(trace(a, b))
        want = "✅" if s.isSubsequence(a, b) else "❌"
        assert frames[-1]["label"].strip().endswith(want), \
            "双指针动图终点结论不对：%r" % frames[-1]["label"]
        dp_frames = list(trace_dp(a, b))
        assert dp_frames[-1]["label"].strip().endswith(want), \
            "DP 动图终点结论不对：%r" % dp_frames[-1]["label"]
    print("[ok] 4 组用例中，两条动图轨迹的终点结论一致")

    # 步数对比：双指针只扫一遍 t，DP 版要推 |s|×|t| 个格子
    greedy_steps = len(list(trace("abc", "ahbgdc")))
    dp_steps = len(list(trace_dp("abc", "ahbgdc")))
    assert dp_steps > greedy_steps * 2, "DP 版的步数优势没有体现出来"
    print("[ok] s=\"abc\", t=\"ahbgdc\"：双指针 %d 步，DP 版 %d 步（相差 %.1f 倍）"
          % (greedy_steps, dp_steps, dp_steps / greedy_steps))


if __name__ == "__main__":
    _self_test()
