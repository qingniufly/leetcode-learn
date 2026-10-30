"""
LeetCode 2. 两数相加
Add Two Numbers

时间复杂度 O(n)，空间复杂度 O(n)。

题意：两个非负数字用链表表示，每个节点存一位数字，且数字是「逆序」存储的
      （所以链表头是最低位）。返回两数相加后的链表，同样逆序。

思路：模拟竖式加法，从最低位往最高位逐位相加。
    每一位：v1 + v2 + carry
      · 本位写下的数字是 (v1 + v2 + carry) % 10
      · 往高位的进位是 (v1 + v2 + carry) // 10
    循环条件要带上 carry —— 最高位还可能再进一位（如 5 + 5 = 10）。
"""

from typing import Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


class Solution:
    """推荐提交版本：链表逐位相加。"""

    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        cur = dummy
        carry = 0
        while l1 or l2 or carry:
            v1 = l1.val if l1 else 0
            v2 = l2.val if l2 else 0
            total = v1 + v2 + carry
            carry, digit = divmod(total, 10)
            cur.next = ListNode(digit)
            cur = cur.next
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        return dummy.next


class SolutionAsList:
    """先转成列表再算，思路一样但更好读。"""

    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        a, b = [], []
        while l1:
            a.append(l1.val)
            l1 = l1.next
        while l2:
            b.append(l2.val)
            l2 = l2.next
        carry, out = 0, []
        for i in range(max(len(a), len(b))):
            v1 = a[i] if i < len(a) else 0
            v2 = b[i] if i < len(b) else 0
            carry, digit = divmod(v1 + v2 + carry, 10)
            out.append(digit)
        if carry:
            out.append(carry)
        head = None
        for digit in reversed(out):
            head = ListNode(digit, head)
        return head


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(l1, l2):
    """竖式加法：l1 / l2 与 LeetCode 的链表顺序一致 —— 头是最低位。

    帧里的列号 col 从最低位开始数（0 = 最低位），前端据此把两行右对齐。
    """
    i = j = 0
    carry = 0
    result = []           # 已产出的结果位，从低位到高位

    while i < len(l1) or j < len(l2) or carry:
        v1 = l1[i] if i < len(l1) else 0
        v2 = l2[j] if j < len(l2) else 0
        total = v1 + v2 + carry
        carry, digit = divmod(total, 10)
        result.append(digit)

        if i < len(l1) and j < len(l2):
            detail = "%d + %d + %d = %d" % (v1, v2, carry, total)
        elif i < len(l1):
            detail = "%d + 0 + %d = %d" % (v1, carry, total)
        elif j < len(l2):
            detail = "0 + %d + %d = %d" % (v2, carry, total)
        else:
            detail = "0 + 0 + %d = %d" % (carry, total)

        yield {
            "col": len(result) - 1,
            "digit": digit,
            "carry": carry,
            "result": list(result),
            "vars": {"v1": v1, "v2": v2, "carryIn": carry},
            "label": "%s，本位写 %d%s。" % (detail, digit,
                                          "，往高位进 1" if carry else "，不进位"),
            "codeLine": "carry, digit = divmod(total, 10)",
        }
        i += 1
        j += 1


def _self_test() -> None:
    import random
    random.seed(0)

    def build(vals):
        head = None
        for v in reversed(vals):
            head = ListNode(v, head)
        return head

    def flat(node):
        out = []
        while node:
            out.append(node.val)
            node = node.next
        return out

    def to_num(a):
        return int("".join(map(str, reversed(a)))) if a else 0

    def brute(a, b):
        s = str(to_num(a) + to_num(b))
        return [int(c) for c in reversed(s)]

    # 注：LeetCode 约束保证两条链表都非空，且数字没有前导零（0 本身除外）
    cases = [([0], [0]), ([1, 2], [3, 4]), ([9, 9, 9], [1]), ([5], [5]),
             ([1, 2], [0, 3]), ([1], [9, 9, 9, 9, 9, 9, 9]), ([7, 0, 8], [8, 0, 7])]
    for a, b in cases:
        expected = brute(a, b)
        for sol in (Solution(), SolutionAsList()):
            got = flat(sol.addTwoNumbers(build(a), build(b)))
            assert got == expected, "a=%r b=%r 得到 %r，期望 %r" % (a, b, got, expected)
    print("[ok] %d 组边界用例全部通过" % len(cases))

    def rand_chain(max_len):
        """随机生成一条合法的链表：无前导零（最高位非零，0 本身除外）。"""
        n = random.randint(1, max_len)
        digits = [random.randint(0, 9) for _ in range(n)]
        if n > 1 and digits[-1] == 0:
            digits[-1] = random.randint(1, 9)
        return digits

    for _ in range(2000):
        a = rand_chain(6)
        b = rand_chain(6)
        expected = brute(a, b)
        for sol in (Solution(), SolutionAsList()):
            got = flat(sol.addTwoNumbers(build(a), build(b)))
            assert got == expected, "a=%r b=%r 得到 %r，期望 %r" % (a, b, got, expected)
    print("[ok] 2000 组随机用例结果一致")

    # 动图轨迹的终点必须和解题程序的输出一致（图和代码不能对不上）
    for _ in range(300):
        a = rand_chain(6)
        b = rand_chain(6)
        frames = list(trace(a, b))
        # trace 的 result 与 brute 都是「低位在前」，直接比
        assert frames[-1]["result"] == brute(a, b), \
            "动图终点 %r 与代码答案 %r 不一致" % (frames[-1]["result"], brute(a, b))
    print("[ok] 300 组随机用例中，动图轨迹终点与代码答案一致")


if __name__ == "__main__":
    _self_test()
