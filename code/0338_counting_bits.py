"""
LeetCode 338. 比特位计数
Counting Bits

时间复杂度 O(n)，空间复杂度 O(n)（答案数组本身）。

题意：给一个整数 n，返回长度 n+1 的数组 answer，
      其中 answer[i] = i 的二进制表示里「1」的个数。

        n = 2  →  [0, 1, 1]          0=0b0 → 0 个；1=0b1 → 1 个；2=0b10 → 1 个
        n = 5  →  [0, 1, 1, 2, 1, 2]

思路
    关键恒等式：把 i 的二进制**右移一位**（丢掉最低位）之后，
    「1 的个数」只比 i 少一个 —— 而少的那一个，取决于 i 的最低位是不是 1。

        answer[i] = answer[i >> 1] + (i & 1)

    · i >> 1 —— 右移一位，丢掉最低位
    · i & 1   —— 取出最低位（0 或 1）

    举例 i = 5（101₂）：5 >> 1 = 2（10₂），answer[2] = 1；最低位是 1，
    所以 answer[5] = 1 + 1 = 2。

    因为 i >> 1 一定小于 i，从小到大遍历时 answer[i >> 1] 必然已经算好，
    所以**一趟遍历**就能填完整个数组 —— 每个数只算一次。

两种写法
    · Solution         —— DP 右移递推，O(n)，推荐提交
    · SolutionBitByBit —— 每个数都把二进制从头数一遍，O(n log n)，只作对照
"""


class Solution:
    """DP 版：answer[i] = answer[i >> 1] + (i & 1)，一趟遍历 O(n)。"""

    def countBits(self, n: int) -> list[int]:
        ans = [0] * (n + 1)
        for i in range(1, n + 1):
            ans[i] = ans[i >> 1] + (i & 1)
        return ans


class SolutionBitByBit:
    """逐位版：每个数都把二进制从头数一遍，O(n log n)。"""

    def countBits(self, n: int) -> list[int]:
        ans = [0] * (n + 1)
        for i in range(n + 1):
            x = i
            while x:
                ans[i] += x & 1
                x >>= 1
        return ans


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(n):
    """DP 版：逐帧展示 answer[i] 是怎么由 answer[i >> 1] 推出来的。"""
    ans = [0] * (n + 1)

    yield {
        "i": 0,
        "marks": [0],
        "window": [0, 0],
        "bracketLabels": ["起点", "i = 0"],
        "label": "answer[0] = 0 —— 0 的二进制是 0b0，里面一个 1 也没有。",
        "note": "整道题就是一句话：右移一位能复用前一个答案。",
        "vars": {"answer[0]": 0},
        "codeLine": "ans = [0] * (n + 1)",
    }

    for i in range(1, n + 1):
        parent = i >> 1
        bit = i & 1
        ans[i] = ans[parent] + bit
        yield {
            "i": i,
            "marks": [parent],
            "window": [parent, i],
            "bracketLabels": ["i >> 1 = %d" % parent, "i = %d" % i],
            "label": "i = %d（二进制 %s）：右移一位是 %d（二进制 %s），answer[%d] = %d；"
                     "最低位是 %d，所以 answer[%d] = %d + %d = %d。"
                     % (i, bin(i)[2:], parent, bin(parent)[2:], parent, ans[parent],
                        bit, i, ans[parent], bit, ans[i]),
            "note": "左移一位 = 去掉最低位；最低位是 1 就多算一个，是 0 就照抄前面那个。"
                    if bit else "左移一位 = 去掉最低位；最低位是 0，1 的个数和前面那个一样。",
            "vars": {"i": i, "i >> 1": parent, "answer[i >> 1]": ans[parent],
                     "i & 1": bit, "answer[i]": ans[i]},
            "codeLine": "ans[i] = ans[i >> 1] + (i & 1)",
        }

    yield {
        "i": n,
        "window": [0, n],
        "bracketLabels": ["answer[0]", "answer[%d]" % n],
        "label": "答案：%s" % (ans,),
        "note": "每个 i 只用到一个已经算好的答案[i >> 1]，所以是一趟 O(n)。",
        "vars": {"n": n, "用到的答案个数": n},
        "codeLine": "return ans",
    }


def trace_bit_by_bit(n):
    """逐位版：每个数都把二进制从头数一遍，看看比 DP 版多花多少步。"""
    ans = [0] * (n + 1)

    for i in range(n + 1):
        x = i
        cnt = 0
        bits = bin(i)[2:] if i else "0"
        if i == 0:
            yield {
                "i": 0,
                "marks": [0],
                "label": "i = 0（二进制 0）：一位都不用数，answer[0] = 0。",
                "note": "0 没有二进制位要扫。",
                "vars": {"i": 0, "已数出": 0},
                "codeLine": "while x:",
            }
            continue
        for pos in range(len(bits) - 1, -1, -1):
            bit = x & 1
            cnt += bit
            x >>= 1
            ans[i] = cnt
            yield {
                "i": i,
                "marks": [i],
                "label": "i = %d（二进制 %s）：从最低位开始数，第 %d 位是 %d，累计 %d 个 1。"
                         % (i, bits, pos, bit, cnt),
                "note": "这个数之前算过的答案一点也用不上，每个数都得从头数一遍。",
                "vars": {"i": i, "当前位": pos, "已数出": cnt},
                "codeLine": "ans[i] += x & 1",
            }

    yield {
        "i": n,
        "window": [0, n],
        "bracketLabels": ["answer[0]", "answer[%d]" % n],
        "label": "答案：%s" % (ans,),
        "note": "结果一样，但步数是 DP 版的好几倍 —— 每个数的每一位都重新扫了一遍。",
        "vars": {"n": n},
        "codeLine": "return ans",
    }


def _self_test() -> None:
    # 独立实现一份参考解：直接数二进制里的 1
    def reference(n):
        return [bin(i).count("1") for i in range(n + 1)]

    s = Solution()
    b = SolutionBitByBit()
    assert s.countBits(0) == [0]
    assert s.countBits(2) == [0, 1, 1]
    assert s.countBits(5) == [0, 1, 1, 2, 1, 2]
    assert s.countBits(17) == [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2]
    print("[ok] 边界用例：n = 0 / 2 / 5 / 17 都正确")

    for n in range(0, 200):
        expected = reference(n)
        assert s.countBits(n) == expected, "n=%d DP 版结果不对" % n
        assert b.countBits(n) == expected, "n=%d 逐位版结果不对" % n
    print("[ok] n = 0..199 两种写法都与「直接数二进制里的 1」一致")

    # 递推式本身要成立：answer[i] == answer[i >> 1] + (i & 1)
    for i in range(1, 1000):
        assert s.countBits(i)[i] == s.countBits(i)[i >> 1] + (i & 1), "递推式在 i=%d 上不成立" % i
    print("[ok] 递推式 answer[i] = answer[i >> 1] + (i & 1) 对 i = 1..999 都成立")

    # 动图轨迹的终点必须和解题程序的输出一致
    for n in (0, 3, 7, 15):
        frames = list(trace(n))
        assert frames[-1]["label"] == "答案：%s" % (reference(n),), "动图终点答案不对"
        assert frames[-1]["vars"]["n"] == n
        bit_frames = list(trace_bit_by_bit(n))
        assert bit_frames[-1]["label"] == frames[-1]["label"], "两条动图终点不一致"
    print("[ok] 4 组用例中，两条动图轨迹的终点都给出了完整答案")

    # 步数对比：DP 版一趟，逐位版要按位数重扫
    dp_steps = len(list(trace(7)))
    bit_steps = len(list(trace_bit_by_bit(7)))
    assert bit_steps > dp_steps * 2, "逐位版的步数优势没有体现出来"
    print("[ok] n = 7 时：DP 版 %d 步，逐位版 %d 步（相差 %.1f 倍）"
          % (dp_steps, bit_steps, bit_steps / dp_steps))


if __name__ == "__main__":
    _self_test()
