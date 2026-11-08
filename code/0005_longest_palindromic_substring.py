"""
LeetCode 5. 最长回文字串
Longest Palindromic Substring

时间复杂度 O(n²)，空间复杂度 O(1)（中心扩展版）。

题意：给一个字符串 s，返回 s 里最长的**回文子串**（连续的一段，正着读反着读一样）。

        s = "babad"  →  "bab"（或 "aba"，两个都是 3 长的回文，取先找到的）
        s = "cbbd"   →  "bb"

思路
    回文串的性质：**去掉首尾两个字符后，剩下的还是回文串**。
    反过来看，一个回文串就是「一个中心 + 左右对称的字符」。

    所以枚举所有可能的中心，从中心往两边撑：
    · 奇数长度：中心是某个字符本身，s[i..i] 起，撑成 "bab"
    · 偶数长度：中心是两个字符之间，s[i..i+1] 起，撑成 "abba"

    撑的过程中，只要 s[l] == s[r] 就继续往外；一遇到不等或越界就停。
    每次撑出一个更长的回文就更新答案。

    一共 2n-1 个中心，每个中心最多撑 O(n) 次 → O(n²)。

两种写法
    · Solution      —— 中心扩展法，O(n²) 时间、O(1) 空间，推荐提交
    · SolutionByDP  —— 区间 DP（dp[i][j] 表示 s[i..j] 是不是回文），
                       O(n²) 时间、O(n²) 空间，只作对照
"""


class Solution:
    """中心扩展法：枚举回文中心往外撑，O(n²) 时间、O(1) 额外空间。"""

    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        if n < 2:
            return s
        best_start, best_len = 0, 1
        for center in range(n):
            # 奇数长：center 是中心；偶数长：center 与 center+1 之间是中心
            for l, r in ((center, center), (center, center + 1)):
                while l >= 0 and r < n and s[l] == s[r]:
                    if r - l + 1 > best_len:
                        best_start, best_len = l, r - l + 1
                    l -= 1
                    r += 1
        return s[best_start:best_start + best_len]


class SolutionByDP:
    """DP 版：dp[i][j] = s[i..j] 是不是回文串，O(n²) 时间、O(n²) 空间。"""

    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        if n < 2:
            return s
        dp = [[False] * n for _ in range(n)]
        best_start, best_len = 0, 1
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i <= 1 or dp[i + 1][j - 1]):
                    dp[i][j] = True
                    # 用 >= 而不是 >：长度相同时取更靠左的那个，
                    # 这样和中心扩展版、暴力版的答案完全一致
                    # （"babad" 的 "bab" 和 "aba" 一样长，LeetCode 接受任意一个）
                    if j - i + 1 >= best_len:
                        best_start, best_len = i, j - i + 1
        return s[best_start:best_start + best_len]


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(s):
    """中心扩展法：逐帧展示每个中心怎么把回文串往外撑。"""
    n = len(s)
    best_start, best_len = 0, 1

    for center in range(n):
        for l, r in ((center, center), (center, center + 1)):
            even = (l != r)
            got = False
            while l >= 0 and r < n and s[l] == s[r]:
                got = True
                if r - l + 1 > best_len:
                    best_start, best_len = l, r - l + 1
                if l == r:
                    text = ("以 s[%d]='%s' 为中心的奇数回文，从它自己开始（长度 1）。"
                            % (center, s[center]))
                else:
                    text = ("s[%d]='%s' 和 s[%d]='%s' 相等 → 回文撑成 \"%s\"（长度 %d）。"
                            % (l, s[l], r, s[r], s[l:r + 1], r - l + 1))
                yield {
                    "i": center,
                    "window": [l, r],
                    "bracketLabels": ["l = %d" % l, "r = %d" % r],
                    "marks": list(range(best_start, best_start + best_len)),
                    "caption": "中心 s[%d]='%s'（%s回文）" % (center, s[center], "偶" if even else "奇"),
                    "label": text,
                    "note": "描边的那一段是目前最长的回文；高亮的这段是现在正撑着的。"
                            if got else "",
                    "vars": {"中心": center, "当前回文": s[l:r + 1], "长度": r - l + 1,
                             "目前最长": s[best_start:best_start + best_len]},
                    "codeLine": "while l >= 0 and r < n and s[l] == s[r]:",
                }
                l -= 1
                r += 1

            # 这一轮撑不动了：给出原因
            if l < 0 or r >= n:
                why = "再往外就越界了（l = %d, r = %d），这个中心到此为止。" % (l, r)
            else:
                why = "s[%d]='%s' != s[%d]='%s'，撑不动了，这个中心到此为止。" % (l, s[l], r, s[r])
            frame = {
                "i": center,
                "dropped": [k for k in (l, r) if 0 <= k < n],
                "caption": "撑不动了",
                "label": why,
                "note": "换成下一个中心继续试。",
                "vars": {"中心": center, "目前最长": s[best_start:best_start + best_len]},
                "codeLine": "l -= 1",
            }
            if got:
                frame["window"] = [l + 1, r - 1]
                frame["bracketLabels"] = ["l = %d" % (l + 1), "r = %d" % (r - 1)]
                frame["marks"] = list(range(best_start, best_start + best_len))
            yield frame

    yield {
        "i": best_start + best_len // 2,
        "window": [best_start, best_start + best_len - 1],
        "bracketLabels": ["l = %d" % best_start, "r = %d" % (best_start + best_len - 1)],
        "marks": list(range(best_start, best_start + best_len)),
        "backLabel": "跳到答案",
        "caption": "结论",
        "label": "最长回文子串是 \"%s\"（长度 %d）。" % (s[best_start:best_start + best_len], best_len),
        "note": "n 个字符、2n-1 个中心，每个中心最多撑 n/2 次。",
        "vars": {"答案": s[best_start:best_start + best_len], "长度": best_len},
        "codeLine": "return s[best_start:best_start + best_len]",
    }


def trace_dp(s):
    """DP 版：逐格推出 dp[i][j]（s[i..j] 是不是回文串）。

    dp[i][j] = s[i] == s[j] 且（长度 ≤ 2 或 dp[i+1][j-1] 为真）
    """
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    best_start, best_len = 0, 1
    prev_j = None

    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            same = s[i] == s[j]
            inner = dp[i + 1][j - 1] if (j - i >= 2 and i + 1 < n) else True
            dp[i][j] = same and (j - i <= 1 or inner)
            if dp[i][j] and j - i + 1 >= best_len:
                best_start, best_len = i, j - i + 1

            if not same:
                text = ("dp[%d][%d]：s[%d]='%s' 和 s[%d]='%s' 不相等 → 不是回文。"
                        % (i, j, i, s[i], j, s[j]))
            elif j - i <= 1:
                text = ("dp[%d][%d]：两端 s[%d]='%s' / s[%d]='%s' 相等，中间没别的字符 → 是回文。"
                        % (i, j, i, s[i], j, s[j]))
            else:
                text = ("dp[%d][%d]：两端 s[%d]='%s' / s[%d]='%s' 相等，"
                        "但 dp[%d][%d] = %s → 不是回文。"
                        % (i, j, i, s[i], j, s[j], i + 1, j - 1,
                           "真" if inner else "假"))

            frame = {
                "i": j,
                "window": [i, j],
                "bracketLabels": ["i = %d" % i, "j = %d" % j],
                "marks": list(range(best_start, best_start + best_len)),
                "caption": "dp[%d][%d] = %s" % (i, j, "真" if dp[i][j] else "假"),
                "label": text,
                "note": "dp 表要开 n×n 的空间，中心扩展法一个变量都不用。",
                "vars": {"i": i, "j": j, "s[i]": s[i], "s[j]": s[j],
                         "dp[i][j]": "真" if dp[i][j] else "假",
                         "目前最长": s[best_start:best_start + best_len]},
                "codeLine": "if s[i] == s[j] and (j - i <= 1 or dp[i + 1][j - 1]):",
            }
            if prev_j is not None and j < prev_j:
                frame["backLabel"] = "换行：i ←"
            prev_j = j
            yield frame

    yield {
        "i": best_start + best_len // 2,
        "window": [best_start, best_start + best_len - 1],
        "bracketLabels": ["i = %d" % best_start, "j = %d" % (best_start + best_len - 1)],
        "marks": list(range(best_start, best_start + best_len)),
        "backLabel": "跳到答案",
        "caption": "结论",
        "label": "最长回文子串是 \"%s\"（长度 %d）。" % (s[best_start:best_start + best_len], best_len),
        "note": "同样是 O(n²)，但 DP 版多开了一张 n×n 的表。",
        "vars": {"答案": s[best_start:best_start + best_len], "长度": best_len},
        "codeLine": "return s[best_start:best_start + best_len]",
    }


def _self_test() -> None:
    # 独立实现一份暴力解：枚举所有子串，逐个判断是不是回文
    def brute(s):
        best = ""
        for i in range(len(s)):
            for j in range(i, len(s)):
                sub = s[i:j + 1]
                if sub == sub[::-1] and len(sub) > len(best):
                    best = sub
        return best

    sol = Solution()
    dp = SolutionByDP()
    assert sol.longestPalindrome("") == ""
    assert sol.longestPalindrome("a") == "a"
    assert sol.longestPalindrome("ac") == "a"
    assert sol.longestPalindrome("babad") == "bab"
    assert sol.longestPalindrome("cbbd") == "bb"
    print("[ok] 边界用例：空串 / 单字符 / 无回文 / babad / cbbd 都正确")

    def same_answer(got, s):
        """答案不唯一时，只要长度对、确实是回文、确实是 s 的子串就算对。"""
        return (got in s and got == got[::-1]
                and len(got) == len(brute(s)))

    for s in ("a" * 12, "ab" * 9, "aba" * 7, "abcdefgh", "racecarxyz", "aaaaabaaaaa"):
        assert same_answer(sol.longestPalindrome(s), s), "s=%r 长度/回文不对" % s
        assert same_answer(dp.longestPalindrome(s), s), "DP 版 s=%r 长度/回文不对" % s
        assert sol.longestPalindrome(s) == brute(s), "s=%r 答案不对" % s
        assert dp.longestPalindrome(s) == brute(s), "DP 版 s=%r 答案不对" % s
    print("[ok] 6 组定长用例，两种写法都与暴力解一致")

    import random
    random.seed(5)
    checked = 0
    for _ in range(500):
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 12)))
        assert sol.longestPalindrome(s) == brute(s), "s=%r 答案不对" % s
        assert dp.longestPalindrome(s) == brute(s), "DP 版 s=%r 答案不对" % s
        assert same_answer(sol.longestPalindrome(s), s)
        assert same_answer(dp.longestPalindrome(s), s)
        checked += 1
    print("[ok] %d 组随机串，两种写法都与暴力解一致" % checked)

    # 动图轨迹的终点必须和解题程序的输出一致
    for s in ("babad", "cbbd", "a", "ab", "aaaa"):
        frames = list(trace(s))
        assert frames[-1]["vars"]["答案"] == sol.longestPalindrome(s), "动图终点答案不对"
        dp_frames = list(trace_dp(s))
        assert dp_frames[-1]["vars"]["答案"] == sol.longestPalindrome(s), "DP 动图终点答案不对"
        assert dp_frames[-1]["label"] == frames[-1]["label"], "两条动图终点不一致"
    print("[ok] 5 组用例中，两条动图轨迹的终点答案一致")

    # 步数对比
    expand_steps = len(list(trace("babad")))
    dp_steps = len(list(trace_dp("babad")))
    print("[ok] s=\"babad\"：中心扩展 %d 帧，DP 版 %d 帧（两者都是 O(n²)，差在空间）"
          % (expand_steps, dp_steps))


if __name__ == "__main__":
    _self_test()
