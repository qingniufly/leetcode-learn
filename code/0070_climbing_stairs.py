"""
LeetCode 70. 爬楼梯
Climbing Stairs

时间复杂度 O(n)，空间复杂度 O(1)（迭代版）。

题意：每次可以爬 1 级或 2 级，问爬到第 n 级共有多少种不同的走法。

思路
    设 f(i) = 爬到第 i 级的走法数。到达第 i 级的最后一步只有两种可能：
    · 从第 i-1 级爬 1 步上来
    · 从第 i-2 级爬 2 步上来
    所以 f(i) = f(i-1) + f(i-2)，本质就是斐波那契数列。

    初始条件：f(0) = 1（一步都不爬，算一种走法）、f(1) = 1。

    · climbStairs0 —— 直接递归，把同一段子问题反复算，是指数级
    · climbStairs  —— 迭代 + 滚动变量，把每个子问题只算一次，是线性级

注意
    递归版不是「慢一点」，而是会爆栈：n = 45 时调用次数是十亿量级。
    本题 n ≤ 45，递归版直接超时。
"""


class Solution:
    """两个版本都保留：climbStairs0 是递归（对照用），climbStairs 是迭代（推荐提交）。"""

    def climbStairs0(self, n: int) -> int:
        """递归版：T(n) = T(n-1) + T(n-2) + 1，指数级，n 大了必超时。"""
        if n <= 2:
            return n
        return self.climbStairs0(n - 1) + self.climbStairs0(n - 2)

    def climbStairs(self, n: int) -> int:
        """迭代版：滚动变量，O(n) 时间 O(1) 空间。"""
        if n <= 2:
            return n
        step_p1, step_p2, i = 1, 2, 3
        while i <= n:
            step_pi = step_p1 + step_p2
            step_p1 = step_p2
            step_p2 = step_pi
            i += 1

        return step_p2


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace_dp(n):
    """迭代 DP 版：逐帧展示 f(i) = f(i-1) + f(i-2) 的推导表格。"""
    nums = [1, 1]                       # f(0) = 1, f(1) = 1
    cells = ["f(0)=1", "f(1)=1"]

    yield {
        "values": cells[:1],
        "col": 0,
        "from": [],
        "caption": "f(0) = 1",
        "label": "f(0) = 1：0 级台阶有 1 种走法（一步都不爬）。",
        "note": "初始条件：f(0) = f(1) = 1",
        "codeLine": "step_p1, step_p2, i = 1, 2, 3",
    }
    yield {
        "values": list(cells),
        "col": 1,
        "from": [],
        "caption": "f(1) = 1",
        "label": "f(1) = 1：只有 1 级台阶，只能爬 1 步。",
        "note": "初始条件：f(0) = f(1) = 1",
        "codeLine": "step_p1, step_p2, i = 1, 2, 3",
    }

    for i in range(2, n + 1):
        value = nums[i - 1] + nums[i - 2]
        nums.append(value)
        cells.append("f(%d)=%d" % (i, value))
        yield {
            "values": list(cells),
            "col": i,
            "from": [i - 1, i - 2],
            "caption": "f(%d) = f(%d) + f(%d) = %d" % (i, i - 1, i - 2, value),
            "label": "f(%d) = f(%d) + f(%d) = %d —— 最后一步要么从第 %d 级迈 1 步，要么从第 %d 级迈 2 步。"
                     % (i, i - 1, i - 2, value, i - 1, i - 2),
            "codeLine": "step_pi = step_p1 + step_p2",
        }


def trace_recursive(n):
    """递归版：逐帧展示每一次函数调用，直接暴露指数级膨胀。"""
    calls = []
    stack = []

    def walk(k):
        stack.append(k)
        calls.append((k, len(stack)))
        if k > 2:
            walk(k - 1)
            walk(k - 2)
        stack.pop()

    walk(n)

    seq = []
    for idx, (k, depth) in enumerate(calls):
        seq.append(str(k))
        yield {
            "values": list(seq),
            "col": idx,
            "from": [],
            "caption": "第 %d 次" % (idx + 1),
            "label": "第 %d 次调用 f(%d)，当前递归深度 %d。" % (idx + 1, k, depth),
            "note": "同一个 f(k) 会被反复重算",
            "vars": {"calls": idx + 1, "depth": depth},
            "codeLine": "return self.climbStairs0(n - 1) + self.climbStairs0(n - 2)",
        }


def _self_test() -> None:
    # 与独立的斐波那契递推对拍
    def fib(n):
        f = [0] * (n + 2)
        f[0], f[1] = 1, 1
        for i in range(2, n + 1):
            f[i] = f[i - 1] + f[i - 2]
        return f[n]

    s = Solution()
    for n in range(1, 21):
        expected = fib(n)
        assert s.climbStairs(n) == expected, "n=%d 迭代得 %d，期望 %d" % (n, s.climbStairs(n), expected)
        assert s.climbStairs0(n) == expected, "n=%d 递归得 %d，期望 %d" % (n, s.climbStairs0(n), expected)
    print("[ok] n = 1..20 迭代版与递归版都与斐波那契一致")

    # 递归版的调用次数增长（指数级）
    def count_calls(k, box):
        box[0] += 1
        if k <= 2:
            return k
        return count_calls(k - 1, box) + count_calls(k - 2, box)

    growth = []
    for n in (10, 15, 20):
        box = [0]
        count_calls(n, box)
        growth.append((n, box[0]))
    assert growth[1][1] > growth[0][1] * 10, "递归调用次数没有呈指数增长"
    print("[ok] 递归调用次数确实指数增长: " +
          "，".join("n=%d -> %d 次" % g for g in growth))

    # 动图轨迹的终点必须和解题程序的输出一致
    for n in range(1, 13):
        frames = list(trace_dp(n))
        last = frames[-1]
        assert last["values"][-1] == "f(%d)=%d" % (n, s.climbStairs(n)), \
            "动图终点 %r 与代码答案不一致" % last["values"][-1]
        rec = list(trace_recursive(n))
        assert rec[-1]["vars"]["calls"] > 0
    print("[ok] 12 组用例中，动图轨迹终点与代码答案一致")


if __name__ == "__main__":
    _self_test()
