"""
LeetCode 1. 两数之和
Two Sum

时间复杂度 O(n)，空间复杂度 O(n)。

思路：一次遍历 + 哈希表。
    对每个下标 i，先算出还差多少 need = target - nums[i]：
    · need 已经在哈希表里 → 找到答案（表里存的是「值 -> 下标」）
    · 否则把 nums[i] -> i 记进哈希表，等后面的数来找它

关键点
    哈希表存的是「值 -> 下标」而不是「值 -> 出现次数」，因为题目要的是下标；
    遍历顺序是「先查表、再入表」，这样同一个元素不会被自己配成一对。
"""

from typing import List


class Solution:
    """推荐提交版本：一次遍历 + 哈希表，O(n)。"""

    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}                      # 值 -> 下标
        for i, x in enumerate(nums):
            need = target - x
            if need in seen:
                return [seen[need], i]
            seen[x] = i
        return []


class SolutionBruteForce:
    """暴力枚举两两配对，O(n^2)。留着做对照。"""

    def twoSum(self, nums: List[int], target: int) -> List[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(nums, target):
    """哈希表版：逐帧展示「查表 -> 入表」的过程。"""
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        hit = need in seen
        if hit:
            yield {
                "i": i,
                "marks": [seen[need], i],
                "vars": {"seen": dict(seen), "need": need},
                "label": ("nums[%d] = %d，还差 %d —— 表里正好有 %d（下标 %d），找到答案 [%d, %d]！"
                          % (i, x, need, need, seen[need], seen[need], i)),
                "codeLine": "return [seen[need], i]",
            }
            return
        seen[x] = i
        yield {
            "i": i,
            "marks": [],
            "vars": {"seen": dict(seen), "need": need},
            "label": ("nums[%d] = %d，还差 %d，表里没有 → 把 %d -> %d 记进哈希表，"
                      "等后面某个数来找它。" % (i, x, need, x, i)),
            "codeLine": "seen[x] = i",
        }


def trace_brute(nums, target):
    """暴力版：逐帧展示两两配对的过程。"""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            total = nums[i] + nums[j]
            hit = total == target
            yield {
                "i": j,
                "j": i,
                "window": [i, j],
                "bracketLabels": ["i", "j"],
                "marks": [i, j] if hit else [],
                "vars": {"total": total},
                "label": ("试 nums[%d] + nums[%d] = %d，等于 target！" % (i, j, total)) if hit else
                         ("试 nums[%d] + nums[%d] = %d，不等，继续。" % (i, j, total)),
                "codeLine": "if nums[i] + nums[j] == target",
            }
            if hit:
                return


def _self_test() -> None:
    import random
    random.seed(0)

    def brute(nums, target):
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []

    def valid(nums, target, pair):
        """题目只要求「存在一组解」，具体是哪一组都可以。"""
        return (isinstance(pair, list) and len(pair) == 2 and pair[0] != pair[1]
                and 0 <= pair[0] < len(nums) and 0 <= pair[1] < len(nums)
                and nums[pair[0]] + nums[pair[1]] == target)

    cases = [[], [1], [2, 7], [3, 3], [3, 2, 4], [1, 2, 3, 4, 5], [0, 4, 3, 0],
             [-1, -2, -3, -4, -5], [5, 5, 5]]
    targets = [0, 5, 6, 9, 10, -7]
    for nums in cases:
        for target in targets:
            expected = brute(nums, target)
            for sol in (Solution(), SolutionBruteForce()):
                got = sol.twoSum(nums, target)
                if expected:
                    assert valid(nums, target, got), \
                        "nums=%r target=%r 得到 %r，不是合法解" % (nums, target, got)
                else:
                    assert got == [], "nums=%r target=%r 本应无解，却得到 %r" % (nums, target, got)
    print("[ok] %d 组边界用例全部通过" % (len(cases) * len(targets)))

    for _ in range(3000):
        nums = [random.randint(-20, 20) for _ in range(random.randint(0, 8))]
        target = random.randint(-20, 20)
        expected = brute(nums, target)
        for sol in (Solution(), SolutionBruteForce()):
            got = sol.twoSum(nums, target)
            if expected:
                assert valid(nums, target, got), \
                    "nums=%r target=%r 得到 %r，不是合法解" % (nums, target, got)
            else:
                assert got == [], "nums=%r target=%r 本应无解，却得到 %r" % (nums, target, got)
    print("[ok] 3000 组随机用例与暴力解结果一致")

    # 动图轨迹的终点必须和解题程序的输出一致（图和代码不能对不上）
    for _ in range(300):
        nums = [random.randint(-20, 20) for _ in range(random.randint(2, 8))]
        target = random.randint(-20, 20)
        frames = list(trace(nums, target))
        assert frames[-1].get("marks") == Solution().twoSum(nums, target), \
            "动图终点 %r 与代码答案 %r 不一致" % (frames[-1].get("marks"),
                                                  Solution().twoSum(nums, target))
    print("[ok] 300 组随机用例中，动图轨迹终点与代码答案一致")


if __name__ == "__main__":
    _self_test()
