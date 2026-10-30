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
