"""
LeetCode 377. 组合总和 Ⅳ
Combination Sum IV

时间复杂度 O(target·n)，空间复杂度 O(target)。

题意：给一个**互不相同的正整数**数组 nums，问有多少个**有序序列**（元素可无限重复使用）
      的和恰好等于 target。注意题目名叫「组合」，要的却是**排列**：(1,2) 和 (2,1) 算两种。

思路
    dp[i] = 和为 i 的有序序列个数。枚举序列的**最后一个数** num：
        去掉末尾的 num，前面是一个和为 i-num 的有序序列，接法唯一。
        所以 dp[i] = 所有 num ≤ i 的 dp[i-num] 之和。
    初始 dp[0] = 1（空序列，作为递推的「种子」）。

    **外层必须是容量 i、内层是 nums**：每个 i 都把「谁当最后一个数」完整枚举一遍，
    不同的结尾顺序各自计数，(1,2) 和 (2,1) 才会被分开数。

边界
    • target = 0：空序列算一种，答案 1。
    • 所有数都比 target 大：一个都接不上，答案 0。
    • 题目保证 nums 是正整数：若有 0，序列可以无限插 0，方案数无穷，DP 也会失控。

对照写法（保留原样，见 SolutionCombination）
    原始写法把 nums 放外层、容量放内层。那是完全背包**组合计数**（LeetCode 518）
    的标准循环顺序：同一组数只按 nums 的先后次序排一次，数出来的是「多重集」个数，
    顺序不同的方案被合并掉了，答案必然偏小。
"""

from typing import List


class Solution:
    """推荐提交版：外层枚举容量、内层枚举「最后一个数」，数的是有序序列。"""

    def combinationSum4(self, nums: List[int], target: int) -> int:
        dp = [0] * (target + 1)
        dp[0] = 1
        for i in range(1, target + 1):
            for num in nums:
                if num <= i:
                    dp[i] += dp[i - num]
        return dp[target]


class SolutionCombination:
    """原始写法（外层遍历数字）：❌ 不可提交 —— 它数的是「组合」，不是「有序序列」。

    错在哪：
        nums 在外层、容量在内层，是完全背包**组合计数**（LeetCode 518 零钱兑换 II）
        的标准循环顺序：处理到 num 时，dp 里的序列都默认「按 nums 的次序排列」，
        同一组数（多重集）只会被数一次 —— (1,2) 和 (2,1) 被合并成一种。
        而本题顺序不同算不同方案，所以答案总是偏小。
        比如 [1,2,3], target=4：正确答案 7，它返回 4 ——
        只数了 {1,1,1,1}、{1,1,2}、{2,2}、{1,3} 这 4 个多重集，
        漏掉了 121/211、31 这些换序方案。

    内层正序本身没错：本题数字可以无限重复使用，正序正是完全背包的写法。
    错的是外层 —— 数排列必须让容量在外层，对每个容量枚举所有可能的「最后一个数」。
    """

    def combinationSum4(self, nums: List[int], target: int) -> int:
        dp = [0] * (target + 1)
        dp[0] = 1
        for num in nums:
            for i in range(num, target + 1, 1):
                dp[i] += dp[i - num]
        return dp[target]


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def _fmt_run(run):
    """把连续下标列表压成「a..b」或「a、b」的形式，供跳过帧说明用。"""
    if len(run) > 2 and run == list(range(run[0], run[-1] + 1)):
        return "%d..%d" % (run[0], run[-1])
    return "、".join(str(v) for v in run)


def trace_dp(nums, target):
    """排列计数 DP（推荐解法）：逐帧展示每个 dp[i] 是怎么按「最后一个数」累出来的。"""
    dp = [0] * (target + 1)
    dp[0] = 1
    if target == 0:
        yield {
            "rows": [list(dp)],
            "labels": ["dp[0]"],
            "row": 0, "col": 0, "from": [],
            "caption": "答案 = dp[0] = 1",
            "label": "target = 0：什么都不选的空序列就算一种，直接返回 1。",
            "note": "dp[0]=1 同时也是递推的种子：任何 num 接在空序列后面都是合法序列。",
            "vars": {"答案": 1, "target": target},
            "codeLine": "dp[0] = 1",
        }
        return

    yield {
        "rows": [list(dp)],
        "labels": ["初始 dp[i]（i = 0..%d）" % target],
        "row": 0, "col": 0, "from": [],
        "caption": "dp[0] = 1",
        "label": "dp[i] = 和为 i 的**有序序列**个数。初始只有空序列一种：dp[0] = 1，"
                 "其余都是 0，接下来从小到大把每个 dp[i] 填出来。",
        "note": "顺序不同算不同方案：(1,2) 和 (2,1) 要分开数。",
        "vars": {"target": target},
        "codeLine": "dp[0] = 1",
    }

    empty_run = []          # 连续「没有数可接」的容量，攒成一帧说明，不出重复画面
    for i in range(1, target + 1):
        prev = list(dp)
        # i-num < i，来源格在上一轮之前就已定格，可以提前判断哪些 num 有效
        usable = [num for num in nums if num <= i and prev[i - num] > 0]
        if not usable:
            empty_run.append(i)
            continue
        if empty_run:
            yield {
                "rows": [list(dp), list(dp)],
                "labels": ["i = %s 没有更新" % _fmt_run(empty_run), "dp 不变"],
                "row": 1, "col": empty_run[-1], "from": [],
                "caption": "没有数可接",
                "label": "i = %s：每个 num 要么比 i 大、要么 dp[i-num] 还是 0，"
                         "没有数能当最后一个数，dp 不变。" % _fmt_run(empty_run),
                "note": "这些容量暂时凑不出序列，等更大的容量把它们带起来。",
                "vars": {"i": empty_run[-1], "target": target},
                "codeLine": "for num in nums:",
            }
            empty_run = []
        skipped = [num for num in nums if num not in usable]
        for k, num in enumerate(usable):
            old = dp[i]
            dp[i] += dp[i - num]
            note = "dp[%d] 已经定格（和为 %d 的序列都数完了），把 num = %d 接在每条末尾，" \
                   "就得到 dp[%d] 新增的 %d 条序列。" % (i - num, i - num, num, i, prev[i - num])
            if k == 0 and skipped:
                note = "nums 里的 %s 此刻接不上（比 i 大或来源为 0），并入说明不单独出帧。%s" % (
                    "、".join(str(v) for v in skipped), note)
            yield {
                "rows": [list(prev), list(dp)],
                "labels": ["本轮开始前（dp[%d] 还没填）" % i, "本轮 dp[0..%d]" % target],
                "row": 1, "col": i, "from": [[0, i - num]],
                "caption": "dp[%d] += dp[%d] = %d" % (i, i - num, dp[i]),
                "label": "填 dp[%d]：枚举最后一个数 num = %d，dp[%d] += dp[%d]，从 %d 变成 %d。"
                         % (i, num, i, i - num, old, dp[i]),
                "note": note,
                "vars": {"i": i, "num": num, "target": target},
                "codeLine": "dp[i] += dp[i - num]",
            }

    if empty_run:
        yield {
            "rows": [list(dp), list(dp)],
            "labels": ["i = %s 没有更新" % _fmt_run(empty_run), "dp 不变"],
            "row": 1, "col": empty_run[-1], "from": [],
            "caption": "没有数可接",
            "label": "i = %s：没有数能当最后一个数（都比 i 大或来源为 0），dp 不变。"
                     % _fmt_run(empty_run),
            "note": "直到 target 都凑不出序列，答案就是 0。",
            "vars": {"i": empty_run[-1], "target": target},
            "codeLine": "for num in nums:",
        }

    yield {
        "rows": [list(dp)],
        "labels": ["最终 dp[i]"],
        "row": 0, "col": target, "from": [],
        "caption": "答案 = dp[%d] = %d" % (target, dp[target]),
        "label": "答案 = dp[%d] = %d 个有序序列。每个容量都把「谁当最后一个数」完整枚举了一遍，"
                 "所以 (1,2) 和 (2,1) 这类换序方案各自计了一次数。" % (target, dp[target]),
        "note": "外层容量、内层数字 —— 这是数「排列」的循环顺序。",
        "vars": {"答案": dp[target], "target": target},
        "codeLine": "return dp[target]",
    }


def trace_combination(nums, target):
    """对照写法（原始代码）：逐帧展示外层遍历数字时，dp 是怎么被填成「组合数」的。"""
    dp = [0] * (target + 1)
    dp[0] = 1
    if target == 0:
        yield {
            "rows": [list(dp)],
            "labels": ["dp[0]"],
            "row": 0, "col": 0, "from": [],
            "caption": "dp[0] = 1",
            "label": "target = 0：空序列算一种，返回 1。这一种情况两种写法恰好一致。",
            "note": "target > 0 时差异才会显现。",
            "vars": {"答案": 1, "target": target},
            "codeLine": "dp[0] = 1",
        }
        return

    yield {
        "rows": [list(dp)],
        "labels": ["初始 dp[i]（i = 0..%d）" % target],
        "row": 0, "col": 0, "from": [],
        "caption": "dp[0] = 1",
        "label": "原始写法同样从 dp[0] = 1 出发，但接下来**先固定数字 num**，"
                 "再正序扫容量 —— 这是完全背包「组合计数」的循环顺序。",
        "note": "处理 num 时，dp 里的序列默认按 nums 的次序排列，换序方案不会被数到。",
        "vars": {"target": target},
        "codeLine": "dp[0] = 1",
    }

    empty_run = []          # 连续「一轮没更新」的数字，攒成一帧说明
    for num in nums:
        prev = list(dp)
        skipped = []        # 来源为 0 的容量：加了也不变，攒进说明里
        round_frames = []   # 先攒本轮的帧：整轮空转时不出重复画面
        for i in range(num, target + 1, 1):
            if dp[i - num] == 0:
                skipped.append(i)
                continue
            old = dp[i]
            dp[i] += dp[i - num]
            # 来源格若已被本轮动过（下标 ≥ num），箭头画在当前带上，直观展示「重复使用」
            src_row = 1 if i - num >= num else 0
            note = "正序扫容量：dp[%d] 可能已经加过 num 本身 —— 数字可以无限重复使用，" \
                   "这正是完全背包的写法，本身没错。" % (i - num)
            if skipped and not round_frames:
                note = "i = %s 的来源都是 0，加了也不变，跳过不出帧。%s" % (
                    _fmt_run(skipped), note)
            round_frames.append({
                "rows": [list(prev), list(dp)],
                "labels": ["处理 num = %d 之前" % num, "本轮 dp[0..%d]" % target],
                "row": 1, "col": i, "from": [[src_row, i - num]],
                "caption": "dp[%d] += dp[%d] = %d" % (i, i - num, dp[i]),
                "label": "固定 num = %d：dp[%d] += dp[%d]，从 %d 变成 %d。"
                         "新增的序列都以 num 结尾、且前面的数不超过 num 在 nums 里的位置。"
                         % (num, i, i - num, old, dp[i]),
                "note": note,
                "vars": {"num": num, "i": i, "target": target},
                "codeLine": "dp[i] += dp[i - num]",
            })
        if not round_frames:
            empty_run.append(num)
            continue
        if empty_run:
            # 空转轮没动过 dp，所以空转期间的画面就是本轮开始前的 prev
            yield {
                "rows": [list(prev), list(prev)],
                "labels": ["num = %s 整轮没更新" % _fmt_run(empty_run), "dp 不变"],
                "row": 1, "col": target, "from": [],
                "caption": "没有格子可更新",
                "label": "num = %s：要么比 target 还大、要么每个来源 dp[i-num] 都是 0，"
                         "这一轮没有格子可更新。" % _fmt_run(empty_run),
                "note": "range(num, target + 1) 扫了个空（或全是 0 += 0），直接看下一个数。",
                "vars": {"num": empty_run[-1], "target": target},
                "codeLine": "for i in range(num, target + 1, 1):",
            }
            empty_run = []
        for frame in round_frames:
            yield frame

    if empty_run:
        yield {
            "rows": [list(dp), list(dp)],
            "labels": ["num = %s 整轮没更新" % _fmt_run(empty_run), "dp 不变"],
            "row": 1, "col": target, "from": [],
            "caption": "没有格子可更新",
            "label": "num = %s：这一轮没有格子可更新，dp 不变。" % _fmt_run(empty_run),
            "note": "直到最后一个数都扫完，dp 不会再变。",
            "vars": {"num": empty_run[-1], "target": target},
            "codeLine": "for i in range(num, target + 1, 1):",
        }

    yield {
        "rows": [list(dp)],
        "labels": ["最终 dp[i]"],
        "row": 0, "col": target, "from": [],
        "caption": "dp[%d] = %d（偏小）" % (target, dp[target]),
        "label": "数完了，dp[%d] = %d —— 但这是「组合」数：每组数只按 nums 的次序排一次，"
                 "(1,2) 和 (2,1) 被合并成一种，换序方案全漏掉了。" % (target, dp[target]),
        "note": "外层数字、内层容量 —— 这是数「组合」的循环顺序（LeetCode 518）。正确答案见上面那条轨道。",
        "vars": {"答案": dp[target], "target": target},
        "codeLine": "return dp[target]",
    }


def _self_test() -> None:
    # 独立写一份暴力解：DFS 枚举所有有序序列（不带记忆化，和 DP 完全独立）
    def brute_perm(nums, target):
        count = 0

        def dfs(rest):
            nonlocal count
            if rest == 0:
                count += 1
                return
            for x in nums:
                if x <= rest:
                    dfs(rest - x)

        dfs(target)
        return count

    # 再写一份「组合」暴力解：只按不降顺序挑数，每个多重集只数一次
    def brute_comb(nums, target):
        ordered = sorted(nums)
        count = 0

        def dfs(rest, start):
            nonlocal count
            if rest == 0:
                count += 1
                return
            for k in range(start, len(ordered)):
                if ordered[k] <= rest:
                    dfs(rest - ordered[k], k)

        dfs(target, 0)
        return count

    s = Solution()

    # 边界用例
    assert s.combinationSum4([1, 2, 3], 4) == 7
    assert s.combinationSum4([2, 1, 3], 4) == 7      # nums 顺序不影响答案
    assert s.combinationSum4([3, 2, 1], 4) == 7
    assert s.combinationSum4([9], 3) == 0            # 所有数都比 target 大
    assert s.combinationSum4([1], 1) == 1
    assert s.combinationSum4([1], 0) == 1            # 空序列算一种
    assert s.combinationSum4([2], 4) == 1            # 只有 2+2
    assert s.combinationSum4([1, 2], 3) == 3         # 111、12、21
    print("[ok] 边界用例：target=0、全比 target 大、单元素、nums 换序都对")

    # 与暴力解对拍
    import random
    random.seed(377)
    for _ in range(500):
        nums = random.sample(range(1, 7), random.randint(1, 4))
        t = random.randint(0, 10)
        assert s.combinationSum4(nums, t) == brute_perm(nums, t), \
            "nums=%r target=%d 得到 %d，期望 %d" % (
                nums, t, s.combinationSum4(nums, t), brute_perm(nums, t))
    print("[ok] 500 组随机输入与有序序列暴力解一致")

    # 对照写法：确认它数的确实是「组合」，且和正确答案对不上
    c = SolutionCombination()
    assert c.combinationSum4([1, 2, 3], 4) == 4
    assert c.combinationSum4([1, 2, 3], 4) != brute_perm([1, 2, 3], 4)
    for _ in range(300):
        nums = random.sample(range(1, 7), random.randint(1, 4))
        t = random.randint(0, 10)
        assert c.combinationSum4(nums, t) == brute_comb(nums, t), \
            "nums=%r target=%d 对照写法 %d != 组合暴力 %d" % (
                nums, t, c.combinationSum4(nums, t), brute_comb(nums, t))
    print("[ok] 对照写法复现了 bug：它数出的是组合数（[1,2,3]/4 得 4 而非 7），与组合暴力解逐组一致")

    # 动图终点必须和解题程序的输出一致
    cases = [([1, 2, 3], 4), ([1, 2], 3), ([9], 3), ([1], 0), ([2], 4), ([1], 1)]
    for nums, t in cases:
        frames = list(trace_dp(nums, t))
        assert frames[-1]["vars"]["答案"] == s.combinationSum4(nums, t), \
            "动图终点 %r 与代码答案不一致" % frames[-1]["vars"]["答案"]
        bad = list(trace_combination(nums, t))
        assert bad[-1]["vars"]["答案"] == c.combinationSum4(nums, t), \
            "对照轨道终点 %r 与对照代码答案不一致" % bad[-1]["vars"]["答案"]
    print("[ok] 动图轨迹终点与代码答案一致（推荐解与对照写法都是）")

    # 画面不重复：相邻帧的 rows 不能一模一样（空转已合并进说明 / 跳过帧）
    for nums, t in cases + [([5], 4), ([2, 4], 3)]:
        for fn in (trace_dp, trace_combination):
            fs = list(fn(nums, t))
            for a, b in zip(fs, fs[1:]):
                assert a["rows"] != b["rows"], \
                    "%s nums=%r target=%d 出现画面完全相同的相邻帧" % (fn.__name__, nums, t)
            for f in fs:
                for strip in f["rows"]:
                    assert 0 <= f["col"] < len(strip)
                    for r, cc in f["from"]:
                        assert 0 <= r < len(f["rows"]) and 0 <= cc < len(f["rows"][r])
    print("[ok] 两条轨道都没有画面重复的相邻帧，且所有下标不越界")


if __name__ == "__main__":
    _self_test()