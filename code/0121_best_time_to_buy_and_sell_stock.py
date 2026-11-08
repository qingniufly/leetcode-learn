"""
LeetCode 121. 买卖股票的最佳时机
Best Time to Buy and Sell Stock

时间复杂度 O(n)，空间复杂度 O(1)。

题意：给一个股价数组，只能先买后卖、只能交易一次，问最多能赚多少。
      答不出来（一直跌）就返回 0。

思路
    最优的买入价**不是**全局最低价，而是「卖出价之前那一段里的最低价」。
    因为买入日必须早于卖出日，全局最低价可能出现在卖出之后。

    所以只要从左往右扫一遍，同时记住两件事：
    · min_price —— 到今天为止出现过的最低价（一个「买入候选」）
    · best      —— 到今天为止的最大利润

    每一天做两步，**顺序不能反**：
    1. 先用今天的价格减去历史最低价，更新 best（今天卖出能赚多少）
    2. 再把今天的价格并进 min_price（今天可以当买入候选）

    第 2 步放后面是必须的：先更新最低价的话，`price - min_price` 恒等于 0，
    等于禁止了「当天买当天卖」，最优那一段的利润就丢了。

两种写法
    · Solution       —— 一次遍历，上面这个思路，O(n) / O(1)，推荐提交
    · SolutionTwoEnds —— 原始写法：左右各走一个指针去找最低价 / 最高价。
      ❌ 不可提交：会死循环（LeetCode 上直接 TLE），而且答案也可能错。
      原样保留在这里做对照，动画里能看着它卡住。
"""


class Solution:
    """一次遍历版：维护「历史最低价」和「最大利润」，O(n) 时间、O(1) 空间。"""

    def maxProfit(self, prices: list[int]) -> int:
        if not prices:
            return 0

        min_price = prices[0]      # 到今天为止的最低价 = 买入候选
        best = 0                   # 到今天为止的最大利润

        for i in range(1, len(prices)):
            price = prices[i]
            # 先算利润：今天卖出，配上历史最低价买入
            profit = price - min_price
            if profit > best:
                best = profit
            # 再更新最低价：顺序不能反，否则等于禁止当天买当天卖
            if price < min_price:
                min_price = price

        return best


class SolutionTwoEnds:
    """原始写法（两端扫描）：❌ 不可提交，会死循环、也会算错。

    死循环的原因：
        外层 `while left < right` 只看两个指针的位置；
        内层 1 的条件是 `left + 1 < maxIdx`，所以 left 最多停在 maxIdx - 1；
        内层 2 的条件是 `right - 1 > minIdx`，所以 right 最多停在 minIdx + 1。
        当扫描正好停在「最低价和最高价相邻」的位置上时，
        两个内层循环的条件**同时**不成立，而外层 `left < right` 依然成立，
        于是 left / right 一个格子都挪不动 —— 无限循环。

    答错的原因：
        最低价是用 `<=` 更新的，会把「更早的低价」换成「更晚的低价」；
        而右指针又被 `minIdx` 挡着，扫不到被挡掉的那段，
        于是「低买高卖」的好组合被自己抹掉了。
    """

    def maxProfit(self, prices: list[int]) -> int:
        if len(prices) == 1:
            return 0
        left, right = 0, len(prices) - 1
        minPrice, maxPrice, minIdx, maxIdx = prices[left], prices[right], left, right
        while left < right:
            while left + 1 < maxIdx:
                if prices[left + 1] <= minPrice:
                    minPrice = prices[left + 1]
                    minIdx = left + 1
                left += 1
            while right - 1 > minIdx:
                if prices[right - 1] >= maxPrice:
                    maxPrice = prices[right - 1]
                    maxIdx = right - 1
                right -= 1
        return 0 if minPrice > maxPrice else maxPrice - minPrice


# ======================================================================
# 动画轨迹：tools/build.py 会把它序列化成前端可播放的帧
# ======================================================================


def trace(prices):
    """一次遍历版：逐帧展示「历史最低价」和「最大利润」是怎么被更新的。"""
    if not prices:
        return

    min_price = prices[0]
    min_idx = 0
    best = 0
    best_buy = -1
    best_sell = -1

    yield {
        "i": 0,
        "marks": [0],
        "window": [0, 0],
        "bracketLabels": ["已扫描 0..0", "第 0 天"],
        "label": "第 0 天：还没有能卖的日子，先把 %d 记成买入候选（历史最低价）。" % min_price,
        "note": "min_price = %d，best = 0" % min_price,
        "vars": {"min_price": min_price, "best": best},
        "codeLine": "min_price = prices[0]",
    }

    for i in range(1, len(prices)):
        price = prices[i]

        # 第 1 步：先算利润
        profit = price - min_price
        improved = profit > best
        if improved:
            best = profit
            best_buy, best_sell = min_idx, i
        marks = [min_idx] + ([best_sell] if best_sell >= 0 else [])
        yield {
            "i": i,
            "marks": marks,
            "window": [0, i],
            "bracketLabels": ["已扫描 0..%d" % i, "第 %d 天" % i],
            "label": "第 %d 天价格 %d：先算利润 %d - %d = %d%s"
                     % (i, price, price, min_price, profit,
                        "，刷新最大利润！" if improved else "，不如已有的 %d，跳过。" % best),
            "note": "第 1 步：先算利润，再更新最低价 —— 顺序反了会把当天买当天卖算成 0。",
            "vars": {"min_price": min_price, "profit": profit, "best": best},
            "codeLine": "profit = price - min_price",
        }

        # 第 2 步：再更新最低价
        if price < min_price:
            min_price = price
            min_idx = i
            yield {
                "i": i,
                "marks": [min_idx] + ([best_sell] if best_sell >= 0 else []),
                "window": [0, i],
                "bracketLabels": ["已扫描 0..%d" % i, "第 %d 天" % i],
                "label": "第 %d 天价格 %d 比历史最低价 %d 还低 —— 买入候选换成它（下标 %d）。"
                         % (i, price, min_price, min_idx),
                "note": "第 2 步：买入候选只认「到今天为止」的最低价，这样才保证买在卖之前。",
                "vars": {"min_price": min_price, "best": best},
                "codeLine": "if price < min_price:",
            }

    if best_sell >= 0:
        tail = "第 %d 天以 %d 买入、第 %d 天以 %d 卖出，赚 %d。" % (
            best_buy, prices[best_buy], best_sell, prices[best_sell], best)
    else:
        tail = "全程没有出现过能赚钱的组合，答案是 0。"
    yield {
        "i": len(prices) - 1,
        "marks": [min_idx] + ([best_sell] if best_sell >= 0 else []),
        "window": [0, len(prices) - 1],
        "bracketLabels": ["已扫描 0..%d" % (len(prices) - 1), "扫完了"],
        "label": "扫完一遍：最大利润 %d —— %s" % (best, tail),
        "note": "答案只跟「卖出价之前的最低价」有关，跟全局最高价无关。",
        "vars": {"min_price": min_price, "best": best},
        "codeLine": "return best",
    }


def trace_two_ends(prices):
    """原始写法（两端扫描）：把它怎么卡死的一步步画出来。

    和 SolutionTwoEnds.maxProfit 是同一套逻辑，只是加了「死循环检测」：
    只要一轮外层循环里两个指针和两个下标都没动，就判定卡死并停帧。
    """
    if len(prices) <= 1:
        yield {
            "i": 0,
            "marks": [],
            "label": "只有一天，没有可卖的组合，返回 0。",
            "note": "n = 1 直接返回 0。",
            "vars": {"left": 0, "right": 0},
            "codeLine": "if len(prices) == 1:",
        }
        return

    left, right = 0, len(prices) - 1
    minPrice, maxPrice = prices[left], prices[right]
    minIdx, maxIdx = left, right
    state = (left, right, minIdx, maxIdx)

    yield {
        "i": left,
        "marks": [minIdx, maxIdx],
        "label": "初始化：left = %d，right = %d；最低价候选 %d（下标 %d），最高价候选 %d（下标 %d）。"
                 % (left, right, minPrice, minIdx, maxPrice, maxIdx),
        "note": "想法是：从左端找最低价、从右端找最高价，只要最低价在最高价左边就能配对。",
        "vars": {"left": left, "right": right, "minPrice": minPrice, "maxPrice": maxPrice},
        "codeLine": "minPrice, maxPrice, minIdx, maxIdx = prices[left], prices[right], left, right",
    }

    while left < right:
        # ---- 内层 1：左指针往右找更低的价 ----
        while left + 1 < maxIdx:
            nxt = left + 1
            if prices[nxt] <= minPrice:
                minPrice, minIdx = prices[nxt], nxt
                yield {
                    "i": nxt,
                    "marks": [minIdx, maxIdx],
                    "label": "左指针走到下标 %d：价格 %d ≤ 当前最低价 %d，最低价更新为 %d（下标 %d）。"
                             % (nxt, prices[nxt], minPrice, minPrice, minIdx),
                    "note": "内层循环 1：`while left + 1 < maxIdx` —— 只能在最高价左边找买入价。",
                    "vars": {"left": left + 1, "right": right, "minPrice": minPrice, "maxPrice": maxPrice},
                    "codeLine": "if prices[left + 1] <= minPrice:",
                }
            else:
                yield {
                    "i": nxt,
                    "marks": [minIdx, maxIdx],
                    "label": "左指针走到下标 %d：价格 %d > 当前最低价 %d，不是更低的买入价，继续。"
                             % (nxt, prices[nxt], minPrice),
                    "note": "内层循环 1：`while left + 1 < maxIdx`。",
                    "vars": {"left": left + 1, "right": right, "minPrice": minPrice, "maxPrice": maxPrice},
                    "codeLine": "left += 1",
                }
            left += 1

        yield {
            "i": left,
            "marks": [minIdx, maxIdx],
            "label": "内层循环 1 停下：left = %d，此时 left + 1 = %d 已经不小于 maxIdx = %d，没法再往前。"
                     % (left, left + 1, maxIdx),
            "note": "左指针最多只能走到 maxIdx - 1，这是原写法的硬约束。",
            "vars": {"left": left, "right": right, "minPrice": minPrice, "maxPrice": maxPrice},
            "codeLine": "while left + 1 < maxIdx:",
        }

        # ---- 内层 2：右指针往左找更高的价 ----
        while right - 1 > minIdx:
            nxt = right - 1
            if prices[nxt] >= maxPrice:
                maxPrice, maxIdx = prices[nxt], nxt
                yield {
                    "i": nxt,
                    "marks": [minIdx, maxIdx],
                    "backLabel": "右指针 ←",
                    "label": "右指针走到下标 %d：价格 %d ≥ 当前最高价 %d，最高价更新为 %d（下标 %d）。"
                             % (nxt, prices[nxt], maxPrice, maxPrice, maxIdx),
                    "note": "内层循环 2：`while right - 1 > minIdx` —— 只能在最低价右边找卖出价。",
                    "vars": {"left": left, "right": right - 1, "minPrice": minPrice, "maxPrice": maxPrice},
                    "codeLine": "if prices[right - 1] >= maxPrice:",
                }
            else:
                yield {
                    "i": nxt,
                    "marks": [minIdx, maxIdx],
                    "backLabel": "右指针 ←",
                    "label": "右指针走到下标 %d：价格 %d < 当前最高价 %d，不是更高的卖出价，继续。"
                             % (nxt, prices[nxt], maxPrice),
                    "note": "内层循环 2：`while right - 1 > minIdx`。",
                    "vars": {"left": left, "right": right - 1, "minPrice": minPrice, "maxPrice": maxPrice},
                    "codeLine": "right -= 1",
                }
            right -= 1

        yield {
            "i": right,
            "marks": [minIdx, maxIdx],
            "backLabel": "右指针 ←",
            "label": "内层循环 2 停下：right = %d，此时 right - 1 = %d 已经不大于 minIdx = %d，没法再往前。"
                     % (right, right - 1, minIdx),
            "note": "右指针最多只能走到 minIdx + 1，这是原写法的硬约束。",
            "vars": {"left": left, "right": right, "minPrice": minPrice, "maxPrice": maxPrice},
            "codeLine": "while right - 1 > minIdx:",
        }

        new_state = (left, right, minIdx, maxIdx)
        if new_state == state:
            yield {
                "i": left,
                "marks": [minIdx, maxIdx],
                "label": "💥 死循环：外层 `while left < right` 还成立（%d < %d），"
                         "但两个内层循环的条件同时不成立，left / right 一个格子都挪不动。"
                         % (left, right),
                "note": "两个内层循环都要求「指针再往里一格」，可这一格正好被对方挡住了 —— 永远转下去。",
                "vars": {"left": left, "right": right},
                "codeLine": "while left < right:",
            }
            return
        state = new_state

    answer = 0 if minPrice > maxPrice else maxPrice - minPrice
    yield {
        "i": left,
        "marks": [minIdx, maxIdx],
        "label": "这次侥幸没卡死，返回 %d（最低价 %d 在下标 %d，最高价 %d 在下标 %d）。"
                 % (answer, minPrice, minIdx, maxPrice, maxIdx),
        "note": "但就算能跑完，答案也未必对 —— 最低价用 `<=` 更新，会用更晚的低价盖掉更早的低价。",
        "vars": {"left": left, "right": right},
        "codeLine": "return 0 if minPrice > maxPrice else maxPrice - minPrice",
    }


def _self_test() -> None:
    # 独立实现一份暴力解当标准答案
    def brute(prices):
        best = 0
        for i in range(len(prices)):
            for j in range(i + 1, len(prices)):
                best = max(best, prices[j] - prices[i])
        return best

    s = Solution()
    assert s.maxProfit([]) == 0
    assert s.maxProfit([5]) == 0
    assert s.maxProfit([1, 2]) == 1
    assert s.maxProfit([7, 2, 9, 0, 2]) == 7
    print("[ok] 边界用例：空数组、单元素、单调上涨都正确")

    for n in range(1, 12):
        for i in range(30):
            prices = [(i * 7 + k * 13) % 21 for k in range(n)]
            assert s.maxProfit(prices) == brute(prices), \
                "prices=%r 得到 %d，期望 %d" % (prices, s.maxProfit(prices), brute(prices))
    print("[ok] 300 组随机数组与暴力解结果一致")

    # 原写法：会死循环吗？用 SIGALRM 掐表，实测它确实停不下来
    import signal

    class _Timeout(Exception):
        pass

    def _on_alarm(signum, frame):
        raise _Timeout()

    signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(1)
    try:
        SolutionTwoEnds().maxProfit([1, 2])
        hung = False
    except _Timeout:
        hung = True
    finally:
        signal.alarm(0)
    assert hung, "原写法居然没卡死？"
    print("[ok] 原写法在 [1, 2] 上跑 1 秒仍未结束 —— 死循环实锤")

    # 原写法即使不死循环也会算错
    assert SolutionTwoEnds().maxProfit([0, 3, 0, 1, 0]) == 1, "原写法在这组上不该算对"
    assert s.maxProfit([0, 3, 0, 1, 0]) == 3, "正确解法这组应该是 3"
    print("[ok] 原写法在 [0, 3, 0, 1, 0] 上得 1（正确答案 3），确实会算错")

    # 动图轨迹的终点必须和解题程序的输出一致
    for prices in ([7, 2, 9, 0, 2], [1, 2], [3, 3, 8, 7, 5, 0, 0], [5, 4, 3, 2, 1]):
        frames = list(trace(prices))
        assert frames[-1]["vars"]["best"] == s.maxProfit(prices), \
            "动图终点 %r 与代码答案不一致" % frames[-1]["vars"]
        two = list(trace_two_ends(prices))
        assert two[-1]["label"], "两端扫描轨迹不能为空"
    print("[ok] 4 组用例中，动图轨迹终点与代码答案一致")

    # 两端扫描轨迹要能抓住死循环
    dead = list(trace_two_ends([7, 2, 9, 0, 2]))
    assert "死循环" in dead[-1]["label"], "两端扫描轨迹没有报告死循环"
    print("[ok] 两端扫描轨迹在 [7, 2, 9, 0, 2] 上如实报告了死循环")


if __name__ == "__main__":
    _self_test()
