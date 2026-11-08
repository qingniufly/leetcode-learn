"""
LeetCode 119. 杨辉三角 II
Pascal's Triangle II

时间复杂度 O(rowIndex)，额外空间 O(1)（不含返回的答案数组）。

题意：给出 rowIndex，返回杨辉三角的**第 rowIndex 行**（下标从 0 开始），用一维列表返回。

        rowIndex = 0  ->  [1]
        rowIndex = 3  ->  [1, 3, 3, 1]
        rowIndex = 4  ->  [1, 4, 6, 4, 1]

和 118 的区别
    118 要「前 numRows 行」，整张三角都得留着 -> O(n²) 空间。
    119 只要「一行」，所以整张三角一次都不用建。

三种写法
    · 乘法公式：C(n, j) = C(n, j-1) × (n-j+1) ÷ j
      每格由同一行的前一格推出，严格 O(n) 时间、O(1) 额外空间，不依赖任何运行时的内部实现。
    · 组合数公式：math.comb(n, j)
      每格独立算，一行代码；CPython 对 n ≤ 67 有预计算表，单次调用 O(1)。
    · 滚动上一行：把 118 的思路搬过来，只留上一行
      O(n²) 时间、O(n) 空间，能看懂「行与行的关系」，但比公式慢。

乘法公式 C(n, j) = C(n, j-1) × (n-j+1) ÷ j 的来历
    推导一（代数）：组合数定义式是 C(n, j) = n! / (j! × (n-j)!)
        C(n, j)   = n! / (j! × (n-j)!)
        C(n, j-1) = n! / ((j-1)! × (n-j+1)!)
      两式相除，约掉 n!：
        C(n, j) / C(n, j-1) = ((j-1)! × (n-j+1)!) / (j! × (n-j)!)
                            = (n-j+1) / j
      移项即得 C(n, j) = C(n, j-1) × (n-j+1) ÷ j

    推导二（双计数，更直观）：从 n 个里选 j 个，选出的「集合」算一种，共 C(n, j) 种。
      换个数法：先选 j-1 个有 C(n, j-1) 种，再从剩下的 n-(j-1) = n-j+1 个里补 1 个。
      这样数出的是「有顺序的选法」，比 C(n, j) 多了 j 倍 ——
      因为同一个集合被重复数了 j 遍：集合里 j 个元素，任何一个都可以是「最后补上的那个」。
      例如 {a, b, c} 可以被数成：先选 {a,b} 补 c、先选 {a,c} 补 b、先选 {b,c} 补 a，共 3 遍。
      所以要除以 j。

    为什么这个递推式好使：C(n, j-1) 是**同一行**的前一格，
    第 0 格恒为 1，每一格都能从左边推出来，整行一趟从左往右推完 —— 不需要上一行。

常见错误（最初的写法）
    return [comb(i, j) for i in range(rowIndex) for j in range(i + 1)]
    双重循环 -> 把**前 rowIndex 行**的所有数字摊平成一个列表返回，
    既不是第 rowIndex 行，还因为 range(rowIndex) 少算了一行。
    正确：只取一行 -> [comb(rowIndex, j) for j in range(rowIndex + 1)]
"""


class Solution:
    """推荐提交版本：乘法公式逐格推，严格 O(rowIndex) 时间、O(1) 额外空间。"""

    def getRow(self, rowIndex: int) -> list[int]:
        row = [1] * (rowIndex + 1)
        for j in range(1, rowIndex + 1):
            row[j] = row[j - 1] * (rowIndex - j + 1) // j
        return row


class SolutionByComb:
    """组合数公式版（最初的想法，修正后）：每格独立算 C(rowIndex, j)。"""

    def getRow(self, rowIndex: int) -> list[int]:
        from math import comb
        # 最精简写法：[comb(rowIndex, j) for j in range(rowIndex + 1)]
        return [comb(rowIndex, j) for j in range(rowIndex + 1)]


class SolutionByRow:
    """滚动上一行版（118 的思路搬过来）：只留上一行，逐行滚到目标行。"""

    def getRow(self, rowIndex: int) -> list[int]:
        prev = [1]
        for _ in range(rowIndex):
            cur = [1]
            for j in range(1, len(prev)):
                cur.append(prev[j - 1] + prev[j])
            cur.append(1)
            prev = cur
        return prev


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace_mul(row_index: int):
    """乘法公式版：整行占位，从左往右一格一格填，每格由前一格推出。"""
    row = [None] * (row_index + 1)
    row[0] = 1
    yield {
        "rows": [list(row)],
        "labels": ["第 %d 行" % row_index],
        "row": 0, "col": 0, "from": [],
        "caption": "C(%d, 0) = 1" % row_index,
        "label": "第 0 格恒为 1：C(n, 0) = 1。先把整行占位，再从左往右逐格填。",
        "codeLine": "row = [1] * (rowIndex + 1)",
    }
    for j in range(1, row_index + 1):
        row[j] = row[j - 1] * (row_index - j + 1) // j
        yield {
            "rows": [list(row)],
            "labels": ["第 %d 行" % row_index],
            "row": 0, "col": j,
            "from": [[0, j - 1]],
            "caption": "%d × %d ÷ %d = %d" % (row[j - 1], row_index - j + 1, j, row[j]),
            "label": "第 %d 格 = 第 %d 格(%d) × %d ÷ %d = %d —— 用的是 C(n, j) = C(n, j-1) × (n-j+1) ÷ j。"
                     % (j, j - 1, row[j - 1], row_index - j + 1, j, row[j]),
            "codeLine": "row[j] = row[j - 1] * (rowIndex - j + 1) // j",
        }


def trace_comb(row_index: int):
    """组合数公式版：每格独立算，没有来源格。"""
    from math import comb
    row = [None] * (row_index + 1)
    for j in range(row_index + 1):
        row[j] = comb(row_index, j)
        yield {
            "rows": [list(row)],
            "labels": ["第 %d 行" % row_index],
            "row": 0, "col": j, "from": [],
            "caption": "C(%d, %d) = %d" % (row_index, j, row[j]),
            "label": "第 %d 格独立算出 C(%d, %d) = %d —— 这一格不依赖别的格子，所以没有来源格。"
                     % (j, row_index, j, row[j]),
            "codeLine": "comb(rowIndex, j)",
        }


def trace_roll(row_index: int):
    """滚动上一行版：上一行 + 当前行，每格由上一行相邻两格相加。"""
    prev = [1]
    yield {
        "rows": [list(prev)],
        "labels": ["第 0 行"],
        "row": 0, "col": 0, "from": [],
        "caption": "第 0 行 = [1]",
        "label": "从第 0 行开始：[1]。整道题只会出现这一行和它的下一行。",
        "codeLine": "prev = [1]",
    }
    for i in range(1, row_index + 1):
        cur = [1]
        for j in range(1, i):
            value = prev[j - 1] + prev[j]
            cur.append(value)
            yield {
                "rows": [list(prev), list(cur)],
                "labels": ["第 %d 行" % (i - 1), "第 %d 行" % i],
                "row": 1, "col": j,
                "from": [[0, j - 1], [0, j]],
                "caption": "%d + %d = %d" % (prev[j - 1], prev[j], value),
                "label": "第 %d 行第 %d 格 = 上一行第 %d 格(%d) + 上一行第 %d 格(%d) = %d。"
                         % (i, j, j - 1, prev[j - 1], j, prev[j], value),
                "codeLine": "cur.append(prev[j - 1] + prev[j])",
            }
        cur.append(1)
        yield {
            "rows": [list(prev), list(cur)],
            "labels": ["第 %d 行" % (i - 1), "第 %d 行" % i],
            "row": 1, "col": i, "from": [],
            "caption": "1",
            "label": "第 %d 行结尾补 1，整行完成 —— 这就是第 %d 行。" % (i, i),
            "codeLine": "cur.append(1)",
        }
        prev = list(cur)


def _self_test() -> None:
    # 独立实现一份参考解：逐行递推整张三角
    def reference(n):
        table = [[1]]
        for _ in range(1, n + 1):
            prev = table[-1]
            table.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
        return table[n]

    s = Solution()
    c = SolutionByComb()
    r = SolutionByRow()
    for n in range(0, 31):
        expected = reference(n)
        assert s.getRow(n) == expected, "n=%d 乘法公式版结果不对" % n
        assert c.getRow(n) == expected, "n=%d 组合数版结果不对" % n
        assert r.getRow(n) == expected, "n=%d 滚动版结果不对" % n
    print("[ok] rowIndex = 0..30 三种写法都与参考解一致")

    # 返回长度恒为 rowIndex + 1（rowIndex 从 0 开始）
    for n in range(0, 31):
        assert len(s.getRow(n)) == n + 1, "n=%d 长度不对" % n
    print("[ok] 返回长度恒为 rowIndex + 1")

    # 每行首尾都是 1
    for n in range(0, 31):
        row = s.getRow(n)
        assert row[0] == 1 and row[-1] == 1, "n=%d 首尾不是 1" % n
    print("[ok] 每行首尾都是 1")

    # 记录最初那个错误写法：它返回的是整张三角，不是第 rowIndex 行
    from math import comb as _comb

    def original(n):
        return [_comb(i, j) for i in range(n) for j in range(i + 1)]

    assert original(4) != s.getRow(4)
    assert len(original(4)) != len(s.getRow(4))
    print("[note] 最初的双重循环写法 rowIndex=4 时返回 %d 个数（正确答案是 %d 个），"
          "确认它给的是整张三角而不是第 4 行"
          % (len(original(4)), len(s.getRow(4))))

    # 动图轨迹的终点必须和解题程序的输出一致
    for n in range(0, 9):
        for trace, sol in ((trace_mul, s), (trace_comb, c), (trace_roll, r)):
            frames = list(trace(n))
            assert frames[-1]["rows"][-1] == sol.getRow(n), "动图终点与代码答案不一致"
    print("[ok] 9 组用例中，三条动图轨迹的终点都与代码答案一致")


if __name__ == "__main__":
    _self_test()
