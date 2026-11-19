"""
LeetCode 494. 目标和
Target Sum

时间复杂度 O(n·S)，空间复杂度 O(S)，其中 S = (total + target) / 2。

题意：给 nums 里每个数前面加 '+' 或 '-'，使结果等于 target，问有多少种加法方案。
      题目保证 nums 全是非负整数。

思路
    设带 '+' 的那组数的和是 P，带 '-' 的那组数的和是 N：
        P - N = target
        P + N = total            （total = sum(nums)）
    两式相加消掉 N，得到 P = (total + target) / 2。

    于是「每个数取正取负」换成了「**挑一个子集，和等于 need = (total + target) / 2**」：
    挑中的取 '+'，没挑中的取 '-'，两者一一对应。剩下的问题就是 0/1 背包计数。

        dp[s] = 从已处理的数里挑出和为 s 的子集的方案数
        初始 dp[0] = 1（空集），其余为 0
        处理一个数 x 时：dp[s] += dp[s - x]
                        （不选 x 的方案 + 选 x 的方案）

    **必须倒序更新 s**：正序的话 dp[s - x] 里可能已经用上了 x，同一个数会被用很多次。

边界
    • |target| > total：全取正号也到不了，0 种。
    • (total + target) 是奇数：P 必须是整数，无解，0 种。
    • nums 里有 0：'+0' 和 '-0' 是两种写法，每个 0 让方案数翻倍。
      倒序更新时 x = 0 变成 dp[s] += dp[s]，自动翻倍，不用特判。

对照写法（保留原样，见 SolutionByInterval）
    原始写法建了一张 (n+1)×(n+1) 的 sums 表，统计等于 target 的格子。
    但那张表每个格子都只是**两个前缀和之差** prefix[j] - prefix[i]，
    数的是「和为 target 的连续区间有几个」，不是「正负号方案有几个」——
    区间只是 2^n 种方案里极小的一类。
"""

from typing import List


class Solution:
    """推荐提交版：转成子集和之后，用 0/1 背包数方案数。"""

    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        total = sum(nums)
        if abs(target) > total or (total + target) % 2 != 0:
            return 0
        need = (total + target) // 2
        dp = [0] * (need + 1)
        dp[0] = 1
        for x in nums:
            for s in range(need, x - 1, -1):
                dp[s] += dp[s - x]
        return dp[need]


class SolutionByInterval:
    """原始写法（区间和表）：❌ 不可提交 —— 它数的是「连续区间」，不是「正负号方案」。

    错在哪：
        表里 sums[i][j] 的递推（上面加、下面减）其实是在算
        prefix[j] - prefix[i]，也就是**两个前缀和之差**。
        而 prefix[j] - prefix[i] 恰好是 nums[i..j-1] 这一**段连续区间**的和。
        于是 result 数的是「和为 target 的连续区间有几个」，
        跟题目要的「给每个数独立取正负号」完全是两回事 —— 区间只是 2^n 种方案里
        极小的一类，连交错取号的方案都表达不出来。

    另外 target = 0 时每个零和区间会被数两遍（上三角一遍、下三角一遍），
    nums 里的 0 也丢掉了「+0 / -0 是两种写法」的语义。
    """

    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        result = 0
        size = len(nums) + 1
        sums = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if i == j:
                    continue
                if i < j:
                    sums[i][j] = sums[i][j-1] + nums[j-1]
                    result += 1 if sums[i][j] == target else 0
                else:
                    sums[i][j] = sums[i-1][j] - nums[i-1]
                    result += 1 if sums[i][j] == target else 0
        return result


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace_dp(nums, target):
    """子集和 DP（推荐解法）：逐帧展示 dp[s] 的方案数是怎么累出来的。"""
    total = sum(nums)
    if abs(target) > total or (total + target) % 2 != 0:
        if abs(target) > total:
            reason = "|target| = %d 超过了 total = %d，全取 '+' 号也到不了" % (abs(target), total)
        else:
            reason = "total + target = %d 是奇数，P = (total + target) / 2 不是整数" % (total + target)
        yield {
            "rows": [[0]],
            "labels": ["无解"],
            "row": 0, "col": 0, "from": [],
            "caption": "0 种",
            "label": "无解：%s，直接返回 0 种。" % reason,
            "note": "先把不可能的情况判掉，再开 DP 表。",
            "vars": {"答案": 0, "total": total, "target": target},
            "codeLine": "if abs(target) > total or (total + target) % 2 != 0:",
        }
        return

    need = (total + target) // 2
    dp = [0] * (need + 1)
    dp[0] = 1
    yield {
        "rows": [list(dp)],
        "labels": ["初始 dp[s]（s = 0..%d）" % need],
        "row": 0, "col": 0, "from": [],
        "caption": "dp[0] = 1",
        "label": "要数的是「挑出和为 need = (total + target) / 2 = %d 的子集」有多少个。"
                 "dp[s] = 已处理的数里挑出和为 s 的子集的方案数，初始只有空集一种：dp[0] = 1。"
                 % need,
        "note": "total = %d，target = %d，所以 need = %d" % (total, target, need),
        "vars": {"total": total, "target": target, "need": need},
        "codeLine": "dp[0] = 1",
    }

    for k, x in enumerate(nums):
        prev = list(dp)
        skipped = []          # 来源为 0 的 s：加了也不变，攒进说明里，不单独出重复画面
        emitted = False
        for s in range(need, x - 1, -1):
            if dp[s - x] == 0:
                skipped.append(s)
                continue
            dp[s] += dp[s - x]
            note = "倒着扫 s：此刻 dp[%d] 还是上一轮的 %d，x 只会被用一次。" % (s - x, prev[s - x])
            if skipped and not emitted:
                note = "s = %s 的来源都是 0，加了也不变，跳过不出帧。%s" % (
                    "、".join(str(v) for v in skipped), note)
            yield {
                "rows": [list(prev), list(dp)],
                "labels": ["上一轮（还没算 nums[%d]）" % k, "本轮 dp[0..%d]" % need],
                "row": 1, "col": s, "from": [[0, s], [0, s - x]],
                "caption": "dp[%d] += dp[%d] = %d" % (s, s - x, dp[s]),
                "label": "处理 nums[%d] = %d：dp[%d] += dp[%d]，从 %d 变成 %d。"
                         "不选 x 的方案有 %d 种，选 x 的方案有 %d 种。"
                         % (k, x, s, s - x, prev[s], dp[s], prev[s], prev[s - x]),
                "note": note,
                "vars": {"x": x, "s": s, "need": need, "total": total},
                "codeLine": "dp[s] += dp[s - x]",
            }
            emitted = True
        if not emitted:
            # x > need：选它必然超和，内层循环一格都扫不到；两条带相同，如实展示「本轮没变」
            yield {
                "rows": [list(prev), list(dp)],
                "labels": ["上一轮（还没算 nums[%d]）" % k, "本轮 dp[0..%d]（不变）" % need],
                "row": 1, "col": 0, "from": [],
                "caption": "x = %d > need = %d" % (x, need),
                "label": "处理 nums[%d] = %d：它比 need = %d 还大，选进子集必然超和，"
                         "这一轮没有格子可更新。" % (k, x, need),
                "note": "range(need, x - 1, -1) 是空的，直接看下一个数。",
                "vars": {"x": x, "need": need, "total": total},
                "codeLine": "for s in range(need, x - 1, -1):",
            }

    yield {
        "rows": [list(dp)],
        "labels": ["最终 dp[s]"],
        "row": 0, "col": need, "from": [],
        "caption": "答案 = dp[%d] = %d" % (need, dp[need]),
        "label": "答案 = dp[%d] = %d 种符号分配方案。" % (need, dp[need]),
        "note": "nums 全是 1 时这一行正好是组合数 C(n, s)：挑 %d 个取 '+' 号。" % need,
        "vars": {"答案": dp[need], "need": need, "total": total, "target": target},
        "codeLine": "return dp[need]",
    }


def trace_interval(nums, target):
    """对照写法（原始代码）：逐帧展示 sums[i][j] 表是怎么被填满的。"""
    size = len(nums) + 1
    sums = [[0] * size for _ in range(size)]
    result = 0

    def strip(row, upto):
        """第 row 行里，尚未填到的格子用 None 占位（渲染成问号）。"""
        return [0 if c == row else (sums[row][c] if c <= upto else None)
                for c in range(size)]

    yield {
        "rows": [[0] * size],
        "labels": ["第 0 行（全是 0）"],
        "row": 0, "col": 0, "from": [],
        "caption": "%d×%d 的表" % (size, size),
        "label": "原始写法开了一张 %d×%d 的 sums 表，接下来逐格填，"
                 "并把等于 target 的格子计进答案。" % (size, size),
        "note": "对角线 i == j 被 continue 跳过，恒为 0。",
        "vars": {"result": 0, "target": target},
        "codeLine": "sums = [[0] * size for _ in range(size)]",
    }

    for i in range(size):
        for j in range(size):
            if i == j:
                continue
            if i < j:
                sums[i][j] = sums[i][j-1] + nums[j-1]
            else:
                sums[i][j] = sums[i-1][j] - nums[i-1]
            hit = sums[i][j] == target
            if hit:
                result += 1

            strips = []
            labels = []
            if i > 0:
                strips.append(strip(i - 1, size - 1))
                labels.append("第 %d 行" % (i - 1))
            strips.append(strip(i, j))
            labels.append("第 %d 行" % i)
            cur = len(strips) - 1

            if i < j:
                src = [[cur, j - 1]]
                code_line = "sums[i][j] = sums[i][j-1] + nums[j-1]"
                meaning = "这格其实是 nums[%d..%d] 这一段连续区间的和 = %d" % (i, j - 1, sums[i][j])
            else:
                src = [[0, j]]
                code_line = "sums[i][j] = sums[i-1][j] - nums[i-1]"
                meaning = "这格其实是 nums[%d..%d] 这一段连续区间的和取反 = %d" % (j, i - 1, sums[i][j])

            yield {
                "rows": strips,
                "labels": labels,
                "row": cur, "col": j, "from": src,
                "caption": "sums[%d][%d] = %d" % (i, j, sums[i][j]),
                "label": "填 sums[%d][%d]：%s%s。"
                         % (i, j, meaning,
                            "等于 target，result += 1（累计 %d）。" % result if hit else "不等于 target，不计数。"),
                "note": "整张表都是前缀和的两两之差，所以它数的始终是「连续区间」，"
                        "而不是「每个数取正还是取负」。",
                "vars": {"result": result, "i": i, "j": j, "target": target},
                "codeLine": "result += 1 if sums[i][j] == target else 0" if hit else code_line,
            }

    yield {
        "rows": [[sums[size - 1][c] for c in range(size)]],
        "labels": ["最后一行"],
        "row": 0, "col": 0, "from": [],
        "caption": "result = %d" % result,
        "label": "数完了，result = %d。但这张表统计的是「和为 target 的连续区间有几个」，"
                 "不是「正负号方案有几个」—— 区间只是 2^n 种方案里的一小类。" % result,
        "note": "正确答案见上面那条轨道。",
        "vars": {"result": result, "target": target},
        "codeLine": "return result",
    }


def _self_test() -> None:
    # 独立写一份暴力解：枚举每个数取正取负的全部 2^n 种组合
    def brute(nums, target):
        n = len(nums)
        count = 0
        for mask in range(1 << n):
            s = 0
            for k in range(n):
                if (mask >> k) & 1:
                    s += nums[k]
                else:
                    s -= nums[k]
            if s == target:
                count += 1
        return count

    s = Solution()

    # 边界用例
    assert s.findTargetSumWays([], 0) == 1
    assert s.findTargetSumWays([0], 0) == 2
    assert s.findTargetSumWays([0, 0, 0], 0) == 8
    assert s.findTargetSumWays([1], 1) == 1
    assert s.findTargetSumWays([1], 2) == 0          # |target| > total
    assert s.findTargetSumWays([1, 1], 1) == 0      # total + target 是奇数
    assert s.findTargetSumWays([1, 1], 0) == 2
    assert s.findTargetSumWays([1, 1], -2) == 1
    assert s.findTargetSumWays([1, 1, 1, 1, 1], 3) == 5
    print("[ok] 边界用例：空数组、单个 0、全 0、奇偶不匹配、|target| > total 都对")

    # 与暴力解对拍
    import random
    random.seed(7)
    for _ in range(2000):
        n = random.randint(1, 9)
        nums = [random.randint(0, 6) for _ in range(n)]
        t = random.randint(-12, 12)
        assert s.findTargetSumWays(nums, t) == brute(nums, t), \
            "nums=%r target=%d 得到 %d，期望 %d" % (nums, t, s.findTargetSumWays(nums, t), brute(nums, t))
    print("[ok] 2000 组随机输入与暴力解一致")

    # 对照写法：确认它数的确实是「连续区间」，且和正确答案对不上
    c = SolutionByInterval()
    assert c.findTargetSumWays([1, 1, 1, 1, 1], 3) == 3
    assert c.findTargetSumWays([1, 1, 1, 1, 1], 3) != brute([1, 1, 1, 1, 1], 3)
    assert c.findTargetSumWays([0, 0, 0], 0) == 12
    print("[ok] 对照写法复现了 bug：它数出的是区间个数（target=0 时还数了两遍）")

    # 动图终点必须和解题程序的输出一致
    for nums, t in [([1, 1, 1, 1, 1], 3), ([1, 0, 1, 1, 0], 1), ([1], 1), ([0, 0, 0], 0), ([1], 5)]:
        frames = list(trace_dp(nums, t))
        assert frames[-1]["vars"]["答案"] == s.findTargetSumWays(nums, t), \
            "动图终点 %r 与代码答案不一致" % frames[-1]["vars"]["答案"]
        bad = list(trace_interval(nums, t))
        assert bad[-1]["vars"]["result"] == c.findTargetSumWays(nums, t), \
            "对照轨道终点 %r 与对照代码答案不一致" % bad[-1]["vars"]["result"]
    print("[ok] 动图轨迹终点与代码答案一致（推荐解与对照写法都是）")

    # 画面不重复：相邻帧的 rows 不能一模一样（0+=0 的空转已合并进说明）
    for nums, t in [([1, 1, 1, 1, 1], 3), ([1, 0, 1, 1, 0], 1), ([0, 0, 0], 0), ([5, 1], 0)]:
        fs = list(trace_dp(nums, t))
        for a, b in zip(fs, fs[1:]):
            assert a["rows"] != b["rows"], "nums=%r 出现画面完全相同的相邻帧" % nums
    print("[ok] 推荐轨道没有画面重复的相邻帧（含 x > need 的跳过帧）")


if __name__ == "__main__":
    _self_test()
