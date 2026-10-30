"""
LeetCode 3. 无重复字符的最长子串
Longest Substring Without Repeating Characters

时间复杂度 O(n)，空间复杂度 O(min(n, |Σ|))。

思路：滑动窗口 + 字典
    - 右指针 i 从左到右逐格推进，永不回退；
    - 字典 last 记录每个字符「上一次出现的位置」；
    - 若 last[ch] >= start，说明 ch 在当前窗口内已出现过，出现重复，
      把窗口左端 start 直接跳到 last[ch] + 1；
    - 以 i 结尾的最长无重复子串长度就是 i - start + 1，取全程最大值。

关键细节
    判断条件里的 `>= start` 不能省略。若 last[ch] < start，说明那次出现
    已经被滑出窗口，此时若再把 start 拉回去，会让早已淘汰的重复字符
    重新进入窗口（例如 "abba" 会算出 3 而不是 2）。
"""

import random


class Solution:
    """推荐提交版本：字典 + 单趟扫描，O(n)。"""

    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}        # 字符 -> 上一次出现的下标
        start = 0        # 窗口左端，只增不减
        max_len = 0

        for i, ch in enumerate(s):
            if ch in last and last[ch] >= start:
                start = last[ch] + 1     # 左端直接跳到冲突字符之后
            last[ch] = i
            max_len = max(max_len, i - start + 1)

        return max_len


class SolutionWithSet:
    """等价写法：双指针 + 集合，O(n)。左端用 while 逐格滑出冲突字符。"""

    def lengthOfLongestSubstring(self, s: str) -> int:
        seen = set()
        left = 0
        max_len = 0

        for right, ch in enumerate(s):
            while ch in seen:
                seen.remove(s[left])
                left += 1
            seen.add(ch)
            max_len = max(max_len, right - left + 1)

        return max_len


class SolutionRestart:
    """初版写法：发现重复后左端只回退一格，并把整段重新扫一遍。

    结果是正确的（窗口内字符始终互不相同，且不会漏掉最优解），
    但最坏复杂度是 O(n^2) —— 每次重复都要重扫已确认无重复的前缀。
    典型触发场景：前面一段字符互不相同，末尾再重复一次最后一个字符，
    此时内层循环执行次数约等于 n(n+1)/2。
    """

    def lengthOfLongestSubstring(self, s: str) -> int:
        if s is None:
            return 0
        if len(s) == 1:
            return 1

        start, next_i, max_len, chars = 0, 0, 0, set()
        while next_i < len(s):
            before = len(chars)
            chars.add(s[next_i])
            if len(chars) > max_len:
                max_len = len(chars)
            next_i += 1
            if len(chars) == before:      # s[next_i-1] 与窗口内字符重复
                start += 1                # ← 问题在这里：只回退一格
                next_i = start
                chars.clear()
        return max_len


# ======================================================================
# 动画轨迹：让 tools/build.py 把「执行过程」导出成前端可播放的帧。
# 每加一道新题，只需在本文件里写一个 yield 轨迹的函数，
# 前端播放器就会自动把它渲染成动图，无需改任何 JS。
# ======================================================================


def trace(s: str):
    """字典版：产出逐帧轨迹。"""
    last = {}
    start = 0
    max_len = 0

    for i, ch in enumerate(s):
        prev_last = last.get(ch)
        jumped = prev_last is not None and prev_last >= start
        old_start = start
        if jumped:
            start = prev_last + 1
        last[ch] = i
        win_len = i - start + 1
        max_len = max(max_len, win_len)

        if jumped:
            label = (f"'{ch}' 在窗口内上次出现在 {prev_last}（≥ start），"
                     f"start 直接跳到 {start}，左端 {start - old_start} 个字符被丢弃。")
            code_line = "start = last[ch] + 1"
        elif prev_last is not None:
            label = (f"'{ch}' 上次出现在 {prev_last}，但 {prev_last} < start({start})，"
                     "早已滑出窗口 → start 不动，无须回退。")
            code_line = "if ch in last and last[ch] >= start:"
        else:
            label = f"'{ch}' 首次出现，与窗口内字符都不冲突 → start 保持 {start}。"
            code_line = "if ch in last and last[ch] >= start:"

        yield {
            "i": i,
            "j": start,
            "window": [start, i],
            "dropped": list(range(old_start, start)),
            "jump": {"from": old_start, "to": start, "label": f"start {old_start} → {start}"} if jumped else None,
            "label": label,
            "note": f'窗口 = "{s[start:i + 1]}"，长度 {win_len}',
            "codeLine": code_line,
            "vars": {"last": dict(last), "maxLen": max_len},
        }


def trace_restart(s: str):
    """重启版：产出逐帧轨迹，用来直观展示「指针回退重扫」的浪费。"""
    start, next_i, max_len, chars = 0, 0, 0, set()
    ops = 0

    while next_i < len(s):
        ops += 1
        read_idx = next_i
        before = len(chars)
        chars.add(s[next_i])
        next_i += 1
        dup = len(chars) == before
        old_start = start
        if dup:
            start += 1
            next_i = start
            chars.clear()

        if dup:
            label = (f"读到 '{s[read_idx]}' 时发现重复：左端只挪 1 格到 {start}，"
                     f"指针将从 {read_idx} 回退到 {start} 重扫这一段。")
        else:
            label = f"读到 '{s[read_idx]}'，无冲突，窗口 = '{s[old_start:read_idx + 1]}'。"

        yield {
            "i": read_idx,
            "j": start,
            "window": [old_start, read_idx],
            "dropped": [old_start] if dup else [],
            "jump": None,
            "backLabel": "回退重扫" if dup else None,
            "label": label,
            "note": f"已扫描 {ops} 次",
            "codeLine": "start += 1" if dup else "chars.add(s[next_i])",
            "vars": {"ops": ops, "maxLen": max_len},
        }


def brute_force(s: str) -> int:
    """O(n^3) 暴力解，仅用于测试对拍。"""
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if len(set(s[i:j])) == j - i:
                best = max(best, j - i)
    return best


def count_scan_operations(s: str) -> int:
    """统计「重启版」的内层循环执行次数，用于直观感受 O(n^2)。"""
    start, next_i, ops, chars = 0, 0, 0, set()
    while next_i < len(s):
        ops += 1
        before = len(chars)
        chars.add(s[next_i])
        next_i += 1
        if len(chars) == before:
            start += 1
            next_i = start
            chars.clear()
    return ops


def _self_test() -> None:
    random.seed(0)
    solutions = [Solution(), SolutionWithSet(), SolutionRestart()]

    # 1) 边界用例
    edge_cases = [
        "", "a", "aa", "ab", "abc", "aaa", "abba", "dvdf", "tmmzuxt",
        "pwwkew", "abcabcbb", "bbbbb", "  ", "aA", "ab ba",
    ]
    for s in edge_cases:
        expected = brute_force(s)
        for sol in solutions:
            got = sol.lengthOfLongestSubstring(s)
            assert got == expected, f"{type(sol).__name__}({s!r}) = {got}, 期望 {expected}"
    print(f"[ok] {len(edge_cases)} 个边界用例全部通过")

    # 2) 随机对拍（与暴力解逐个比较）
    for _ in range(3000):
        s = "".join(random.choice("abc") for _ in range(random.randint(0, 9)))
        expected = brute_force(s)
        for sol in solutions:
            got = sol.lengthOfLongestSubstring(s)
            assert got == expected, f"{type(sol).__name__}({s!r}) = {got}, 期望 {expected}"
    print("[ok] 3000 组随机串与暴力解结果一致")

    # 3) 最坏用例下的扫描次数对比
    print("\n最坏用例（m 个互不相同字符 + 末尾重复最后一个字符）")
    print(f"{'n':>7} | {'重启版扫描次数':>16} | {'字典版扫描次数':>16} | {'倍数':>8}")
    for m in (10, 100, 1000):
        s = "".join(chr(0x4E00 + i) for i in range(m))   # m 个互不相同的字符
        s += s[-1]                                       # 末尾再重复最后一个
        restart_ops = count_scan_operations(s)
        dict_ops = len(s)
        print(f"{len(s):>7} | {restart_ops:>16} | {dict_ops:>16} | {restart_ops / dict_ops:>7.1f}x")


if __name__ == "__main__":
    _self_test()
