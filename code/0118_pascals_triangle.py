"""
LeetCode 118. 杨辉三角
Pascal's Triangle

时间复杂度 O(n²)，空间复杂度 O(n²)。

题意：给出 numRows 行，返回杨辉三角的前 numRows 行。
      每个数是它上方两个数之和，两端都是 1。

        1
       1 1
      1 2 1
     1 3 3 1
    1 4 6 4 1

思路
    每一行只依赖**上一行**：第 i 行的第 j 格 = 上一行的第 j-1 格 + 第 j 格。
    所以只要记住上一行，边算边把整行攒进结果里即可。

边界
    • 每行两端的 1 是「边界」，不参与相加，需要单独补；
    • 题目约束 numRows ≥ 1。numRows = 0 时下面的实现会返回 [[1], [1, 1]]
      （不在题目范围内）。
"""


class Solution:
    """推荐提交版本：逐行构建，每一行由上一行的相邻两格相加得到。"""

    def generate(self, numRows: int) -> list[list[int]]:
        if numRows == 1:
            return [[1]]
        if numRows == 2:
            return [[1], [1, 1]]

        tmpResult = [[1], [1, 1]]
        i = 3
        while i <= numRows:
            rowI = [1]                      # 本行开头补一个 1
            prevRow = tmpResult[-1]         # 只需要上一行
            j = 0
            while j < len(prevRow) - 1:
                rowI.append(prevRow[j] + prevRow[j + 1])   # 上一行相邻两格相加
                j += 1
            rowI.append(1)                  # 本行结尾补一个 1
            tmpResult.append(rowI)
            i += 1

        return tmpResult


class SolutionByFormula:
    """另一种写法：每个格子独立用组合数公式 C(n, k) 算，不用上一行。"""

    def generate(self, numRows: int) -> list[list[int]]:
        from math import comb
        # 最精简写法：result = [[comb(i, j) for j in range(i + 1)] for i in range(numRows)]
        result = []
        for i in range(numRows):
            result.append([comb(i, k) for k in range(i + 1)])
        return result


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace_rows(num_rows):
    """逐格推导版：每生成一格就停一下，高亮它上面的两个来源格。"""
    rows = []

    def snapshot(cur=None):
        out = [list(r) for r in rows]
        if cur is not None:
            out.append(list(cur))
        return out

    rows.append([1])
    yield {
        "rows": snapshot(),
        "row": 0, "col": 0, "from": [],
        "caption": "1",
        "label": "第 0 行：只有 1。",
        "codeLine": "if numRows == 1:",
    }
    if num_rows <= 1:
        return

    rows.append([1, 1])
    yield {
        "rows": snapshot(),
        "row": 1, "col": 1, "from": [],
        "caption": "1  1",
        "label": "第 1 行：1 1。",
        "codeLine": "if numRows == 2:",
    }

    for i in range(2, num_rows):
        prev = rows[-1]
        cur = [1]
        yield {
            "rows": snapshot(cur),
            "row": i, "col": 0, "from": [],
            "caption": "1",
            "label": "第 %d 行开头补一个 1（边界不参与相加）。" % i,
            "codeLine": "rowI = [1]",
        }
        for j in range(1, len(prev)):
            value = prev[j - 1] + prev[j]
            cur.append(value)
            yield {
                "rows": snapshot(cur),
                "row": i, "col": j,
                "from": [[i - 1, j - 1], [i - 1, j]],
                "caption": "%d + %d = %d" % (prev[j - 1], prev[j], value),
                "label": "第 %d 行第 %d 格 = %d + %d = %d —— 上一行相邻两格相加。"
                         % (i, j, prev[j - 1], prev[j], value),
                "codeLine": "rowI.append(prevRow[j] + prevRow[j + 1])",
            }
        cur.append(1)
        yield {
            "rows": snapshot(cur),
            "row": i, "col": len(cur) - 1, "from": [],
            "caption": "1",
            "label": "第 %d 行结尾补一个 1，整行完成。" % i,
            "codeLine": "rowI.append(1)",
        }
        rows.append(list(cur))


def trace_formula(num_rows):
    """组合数公式版：每个格子独立算，没有来源格。"""
    from math import comb
    rows = []
    for i in range(num_rows):
        row = [comb(i, k) for k in range(i + 1)]
        for k in range(i + 1):
            yield {
                "rows": [list(r) for r in rows] + [row[:k + 1]],
                "row": i, "col": k, "from": [],
                "caption": "C(%d,%d) = %d" % (i, k, row[k]),
                "label": "第 %d 行第 %d 格：C(%d,%d) = %d —— 每个格子独立用公式算，不依赖上一行，"
                         "两端的 1 也天然包含在内。"
                         % (i, k, i, k, row[k]),
                "codeLine": "comb(i, k)",
            }
        rows.append(list(row))


def _self_test() -> None:
    # 独立实现一份参考解
    def reference(n):
        table = [[1]]
        for _ in range(1, n):
            prev = table[-1]
            table.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
        return table

    s = Solution()
    f = SolutionByFormula()
    for n in range(1, 16):
        expected = reference(n)
        assert s.generate(n) == expected, "n=%d 滚动版结果不对" % n
        assert f.generate(n) == expected, "n=%d 公式版结果不对" % n
    print("[ok] numRows = 1..15 两种写法都与参考解一致")

    # 每一行的两端必须是 1
    for n in range(1, 12):
        tri = s.generate(n)
        for row in tri:
            assert row[0] == 1 and row[-1] == 1
            assert len(row) == len(set(range(len(row))))
    print("[ok] 每一行两端都是 1，且行内无重复元素")

    # 非题目范围：numRows = 0（题面约束为 numRows >= 1）
    print("[note] numRows = 0 时滚动版返回 %r（题目约束 numRows >= 1，不影响提交）"
          % s.generate(0))

    # 动图轨迹的终点必须和解题程序的输出一致
    for n in range(1, 10):
        frames = list(trace_rows(n))
        assert frames[-1]["rows"] == s.generate(n), "动图终点与代码答案不一致"
        frames_f = list(trace_formula(n))
        assert frames_f[-1]["rows"] == f.generate(n), "公式版动图终点与代码答案不一致"
    print("[ok] 9 组用例中，两条动图轨迹的终点都与代码答案一致")


if __name__ == "__main__":
    _self_test()
