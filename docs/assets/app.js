/* ==================================================================
   LeetCode Learn · LeetCode 3 交互讲解
   ================================================================== */
(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';

  function svgEl(tag, attrs) {
    var n = document.createElementNS(SVG_NS, tag);
    for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]);
    return n;
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  /* ---------------- 通用：把一串字符画成方块 ---------------- */

  function buildSlots(container, chars) {
    clear(container);
    var boxes = [];
    for (var i = 0; i < chars.length; i++) {
      var slot = el('div', 'v-slot');
      var box = el('div', 'v-box', chars[i]);
      var idx = el('div', 'v-idx', String(i));
      slot.appendChild(box);
      slot.appendChild(idx);
      container.appendChild(slot);
      boxes.push({ box: box, idx: idx });
    }
    return boxes;
  }

  function boxGeom(stage, slots, i) {
    if (!slots[i]) return null;
    var sr = stage.getBoundingClientRect();
    var r = slots[i].box.getBoundingClientRect();
    return {
      left: r.left - sr.left, right: r.right - sr.left,
      top: r.top - sr.top, bottom: r.bottom - sr.top,
      cx: (r.left + r.right) / 2 - sr.left
    };
  }

  /* ==================================================================
     一、逐步演示
     ================================================================== */

  var EX_SRC = 'abba';
  var EX_CHARS = EX_SRC.split('');
  var EX_CODE = [
    'last = {}                       # 字符 -> 上次出现的下标',
    'start = 0                       # 窗口左端，只增不减',
    'maxLen = 0',
    'for i, ch in enumerate(s):',
    '    if ch in last and last[ch] >= start:',
    '        start = last[ch] + 1    # 左端直接跳到冲突字符之后',
    '    last[ch] = i',
    '    maxLen = max(maxLen, i - start + 1)',
    'return maxLen'
  ];

  function buildExplainSteps(src) {
    var chars = src.split('');
    var last = {}, steps = [], start = 0, maxLen = 0;
    for (var i = 0; i < chars.length; i++) {
      var ch = chars[i];
      var has = Object.prototype.hasOwnProperty.call(last, ch);
      var prevLast = has ? last[ch] : null;
      var oldStart = start, jumped = false;
      if (has && prevLast >= start) { start = prevLast + 1; jumped = true; }
      last[ch] = i;
      var winLen = i - start + 1;
      var grew = winLen > maxLen;
      if (grew) maxLen = winLen;
      var dropped = [];
      for (var k = oldStart; k < start; k++) dropped.push(k);
      steps.push({
        i: i, ch: ch, start: start, oldStart: oldStart, maxLen: maxLen, winLen: winLen,
        prevLast: prevLast, jumped: jumped, grew: grew, dropped: dropped,
        last: Object.assign({}, last), windowStr: chars.slice(start, i + 1).join('')
      });
    }
    return { steps: steps, answer: maxLen };
  }

  function initExplain() {
    var slotsEl = document.getElementById('ex-slots');
    if (!slotsEl) return;

    var built = buildExplainSteps(EX_SRC);
    var steps = built.steps, cur = 0, timer = null;

    var stageEl = document.getElementById('ex-stage');
    var ovEl = document.getElementById('ex-ov');
    var statusEl = document.getElementById('ex-status');
    var detailEl = document.getElementById('ex-detail');
    var posEl = document.getElementById('ex-pos');
    var chipsEl = document.getElementById('ex-chips');
    var prevBtn = document.getElementById('ex-prev');
    var nextBtn = document.getElementById('ex-next');
    var playBtn = document.getElementById('ex-play');
    var resetBtn = document.getElementById('ex-reset');

    var slots = buildSlots(slotsEl, EX_CHARS);

    var codeEl = document.getElementById('ex-code');
    clear(codeEl);
    EX_CODE.forEach(function (line, n) {
      var sp = el('span', 'v-cl');
      sp.id = 'ex-cl-' + n;
      var num = el('span', 'v-num', (n + 1) + '  ');
      sp.appendChild(num);
      var cut = line.indexOf('#');
      if (cut >= 0) {
        sp.appendChild(el('span', '', line.slice(0, cut)));
        sp.appendChild(el('span', 'v-cmt', line.slice(cut)));
      } else {
        sp.appendChild(el('span', '', line));
      }
      codeEl.appendChild(sp);
    });

    function drawOverlay(st) {
      clear(ovEl);
      var sr = stageEl.getBoundingClientRect();
      ovEl.setAttribute('width', sr.width);
      ovEl.setAttribute('height', sr.height);

      var a = boxGeom(stageEl, slots, st.start);
      var b = boxGeom(stageEl, slots, st.i);
      if (!a || !b) return;

      var idxBottom = slots[st.i].idx.getBoundingClientRect().bottom - sr.top;
      var midY = idxBottom + 9;

      ovEl.appendChild(svgEl('path', {
        d: 'M ' + a.left + ' ' + midY + ' L ' + a.left + ' ' + (midY + 4) +
           ' L ' + b.right + ' ' + (midY + 4) + ' L ' + b.right + ' ' + midY,
        fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '1.5', 'stroke-linecap': 'round'
      }));
      var t1 = svgEl('text', { x: a.left, y: midY + 18, fill: 'var(--muted-foreground)', 'font-size': '11' });
      t1.textContent = 'start';
      ovEl.appendChild(t1);
      var narrow = (b.right - a.left) < 46;
      var t2 = svgEl('text', {
        x: b.right, y: midY + (narrow ? 31 : 18), fill: 'var(--muted-foreground)',
        'font-size': '11', 'text-anchor': 'end'
      });
      t2.textContent = 'i = ' + st.i;
      ovEl.appendChild(t2);

      if (st.jumped && st.dropped.length) {
        var from = boxGeom(stageEl, slots, st.dropped[0]);
        var to = boxGeom(stageEl, slots, st.start);
        if (from && to) {
          var x1 = from.cx, x2 = to.cx, y0 = from.top;
          ovEl.appendChild(svgEl('path', {
            d: 'M ' + x1 + ' ' + y0 + ' C ' + x1 + ' ' + (y0 - 34) + ', ' + x2 + ' ' + (y0 - 34) + ', ' + x2 + ' ' + y0,
            fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2', 'stroke-linecap': 'round'
          }));
          ovEl.appendChild(svgEl('path', {
            d: 'M ' + (x2 - 4.5) + ' ' + (y0 - 7) + ' L ' + x2 + ' ' + y0 + ' L ' + (x2 + 4.5) + ' ' + (y0 - 7),
            fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2',
            'stroke-linecap': 'round', 'stroke-linejoin': 'round'
          }));
          var lbl = svgEl('text', {
            x: (x1 + x2) / 2, y: y0 - 22, fill: 'var(--foreground)', 'font-size': '11.5',
            'text-anchor': 'middle', 'paint-order': 'stroke', stroke: 'var(--background)',
            'stroke-width': '4', 'stroke-linejoin': 'round'
          });
          lbl.textContent = 'start ' + st.oldStart + ' → ' + st.start;
          ovEl.appendChild(lbl);
        }
      }
    }

    function render() {
      var st = steps[cur];
      slots.forEach(function (s, idx) {
        s.box.className = 'v-box';
        s.idx.className = 'v-idx';
        if (idx > st.i) s.box.classList.add('is-future');
        if (idx < st.start) s.box.classList.add('is-out');
        if (idx >= st.start && idx <= st.i) s.box.classList.add('is-win');
        if (st.dropped.indexOf(idx) >= 0) { s.box.classList.remove('is-out'); s.box.classList.add('is-drop'); }
        if (idx === st.i) {
          s.box.classList.remove('is-win');
          s.box.classList.add('is-cur');
          s.idx.classList.add('is-cur');
        }
      });

      clear(chipsEl);
      chipsEl.appendChild(el('span', 'v-title', 'last'));
      Object.keys(st.last).forEach(function (k) {
        var c = el('span', 'v-chip');
        if (k === st.ch) c.classList.add('is-cur');
        c.appendChild(el('b', '', "'" + k + "'"));
        c.appendChild(el('span', 'arrow', '→'));
        c.appendChild(el('span', '', String(st.last[k])));
        chipsEl.appendChild(c);
      });

      clear(statusEl);
      function stat(k, v) {
        var s = el('span');
        s.appendChild(el('span', 'k', k + ' '));
        s.appendChild(el('span', 'v', v));
        statusEl.appendChild(s);
      }
      stat('i', '= ' + st.i);
      stat('ch', "= '" + st.ch + "'");
      stat('窗口', '[' + st.start + ', ' + st.i + '] = "' + st.windowStr + '"');
      stat('长度', '= ' + st.winLen);
      stat('maxLen', '= ' + st.maxLen);

      for (var n = 0; n < EX_CODE.length; n++) {
        document.getElementById('ex-cl-' + n).classList.remove('is-active');
      }
      document.getElementById('ex-cl-' + (st.jumped ? 5 : 4)).classList.add('is-active');

      clear(detailEl);
      var msg;
      if (st.jumped) {
        msg = "'" + st.ch + "' 在窗口内上次出现在 " + st.prevLast + "（≥ start），start 直接跳到 " +
              st.start + "，左端 " + st.dropped.length + " 个字符被丢弃。";
      } else if (st.prevLast !== null) {
        msg = "'" + st.ch + "' 上次出现在 " + st.prevLast + "，但 " + st.prevLast +
              " < start(" + st.start + ")，早已滑出窗口 → start 不动，无须回退。";
      } else {
        msg = "'" + st.ch + "' 首次出现，与窗口内字符都不冲突 → start 保持 " + st.start + "。";
      }
      if (st.grew) msg += '  窗口长度 ' + st.winLen + ' > maxLen，更新为 ' + st.maxLen + '。';
      if (cur === steps.length - 1) msg += '  ✓ 扫描结束，最终答案 = ' + built.answer + '。';
      detailEl.appendChild(el('span', '', msg));

      posEl.textContent = '第 ' + (cur + 1) + ' / ' + steps.length + ' 步';
      prevBtn.disabled = cur === 0;
      nextBtn.disabled = cur === steps.length - 1;
      playBtn.textContent = timer ? '暂停' : '自动播放';
      drawOverlay(st);
    }

    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function togglePlay() {
      if (timer) { stop(); render(); return; }
      if (cur >= steps.length - 1) cur = 0;
      timer = setInterval(function () {
        if (cur >= steps.length - 1) { stop(); render(); return; }
        cur++; render();
      }, 900);
      render();
    }

    prevBtn.addEventListener('click', function () { stop(); if (cur > 0) { cur--; render(); } });
    nextBtn.addEventListener('click', function () { stop(); if (cur < steps.length - 1) { cur++; render(); } });
    playBtn.addEventListener('click', togglePlay);
    resetBtn.addEventListener('click', function () { stop(); cur = 0; render(); });
    window.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') nextBtn.click();
      if (e.key === 'ArrowLeft') prevBtn.click();
    });
    if (window.ResizeObserver) {
      new ResizeObserver(function () { drawOverlay(steps[cur]); }).observe(stageEl);
    }
    render();
  }

  /* ==================================================================
     二、复杂度对比
     ================================================================== */

  var CMP_CHARS = ('abcdefghijkl' + 'l').split('');

  function buildRestartFrames(chars) {
    var frames = [];
    var start = 0, nextI = 0, seen = new Set();
    while (nextI < chars.length) {
      var readIdx = nextI;
      var before = seen.size;
      seen.add(chars[nextI]);
      nextI += 1;
      var dup = seen.size === before;
      if (dup) { start += 1; nextI = start; seen.clear(); }
      frames.push({
        readIdx: readIdx, start: start, dup: dup, ops: frames.length + 1,
        window: chars.slice(start, Math.min(nextI, chars.length)).join('')
      });
    }
    return frames;
  }

  function buildDictFrames(chars) {
    var frames = [];
    var last = {}, start = 0, maxLen = 0;
    for (var i = 0; i < chars.length; i++) {
      var ch = chars[i];
      var has = Object.prototype.hasOwnProperty.call(last, ch);
      var prevLast = has ? last[ch] : null;
      var jumped = false;
      if (has && prevLast >= start) { start = prevLast + 1; jumped = true; }
      last[ch] = i;
      var winLen = i - start + 1;
      if (winLen > maxLen) maxLen = winLen;
      frames.push({
        readIdx: i, start: start, jumped: jumped, prevLast: prevLast, maxLen: maxLen,
        ops: i + 1, window: chars.slice(start, i + 1).join('')
      });
    }
    return frames;
  }

  function initCompare() {
    var aSlotsEl = document.getElementById('cmp-a-slots');
    if (!aSlotsEl) return;

    var bSlotsEl = document.getElementById('cmp-b-slots');
    var aStage = document.getElementById('cmp-a-stage');
    var bStage = document.getElementById('cmp-b-stage');
    var aOv = document.getElementById('cmp-a-ov');
    var bOv = document.getElementById('cmp-b-ov');
    var aNote = document.getElementById('cmp-a-note');
    var bNote = document.getElementById('cmp-b-note');
    var aOps = document.getElementById('cmp-a-ops');
    var bOps = document.getElementById('cmp-b-ops');
    var resultEl = document.getElementById('cmp-result');
    var playBtn = document.getElementById('cmp-play');
    var stepBtn = document.getElementById('cmp-step');
    var resetBtn = document.getElementById('cmp-reset');

    var A = buildRestartFrames(CMP_CHARS);
    var B = buildDictFrames(CMP_CHARS);
    var aCur = 0, bCur = 0, timer = null;

    var aSlots = buildSlots(aSlotsEl, CMP_CHARS);
    var bSlots = buildSlots(bSlotsEl, CMP_CHARS);
    document.getElementById('cmp-input').textContent = CMP_CHARS.join('');

    function paintSlots(slots, frame, kind) {
      slots.forEach(function (s, idx) {
        s.box.className = 'v-box';
        s.idx.className = 'v-idx';
        if (idx > frame.readIdx) s.box.classList.add('is-future');
        if (idx < frame.start) s.box.classList.add('is-out');
        if (idx >= frame.start && idx <= frame.readIdx) s.box.classList.add('is-win');
        if (idx === frame.readIdx) {
          s.box.classList.remove('is-win');
          s.box.classList.add('is-cur');
          s.idx.classList.add('is-cur');
        }
      });
    }

    function drawRestartArrow(stage, ov, slots, prevIdx, curIdx) {
      clear(ov);
      var sr = stage.getBoundingClientRect();
      ov.setAttribute('width', sr.width);
      ov.setAttribute('height', sr.height);
      if (prevIdx < 0 || curIdx > prevIdx) return;
      var from = boxGeom(stage, slots, prevIdx);
      var to = boxGeom(stage, slots, curIdx);
      if (!from || !to) return;
      var x1 = from.cx, x2 = to.cx, y0 = from.bottom;
      ov.appendChild(svgEl('path', {
        d: 'M ' + x1 + ' ' + y0 + ' C ' + x1 + ' ' + (y0 + 26) + ', ' + x2 + ' ' + (y0 + 26) + ', ' + x2 + ' ' + y0,
        fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '2', 'stroke-linecap': 'round'
      }));
      ov.appendChild(svgEl('path', {
        d: 'M ' + (x2 - 4.5) + ' ' + (y0 + 7) + ' L ' + x2 + ' ' + y0 + ' L ' + (x2 + 4.5) + ' ' + (y0 + 7),
        fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '2',
        'stroke-linecap': 'round', 'stroke-linejoin': 'round'
      }));
      var lbl = svgEl('text', {
        x: (x1 + x2) / 2, y: y0 + 30, fill: 'var(--foreground)', 'font-size': '11',
        'text-anchor': 'middle', 'paint-order': 'stroke', stroke: 'var(--background)',
        'stroke-width': '4', 'stroke-linejoin': 'round'
      });
      lbl.textContent = '回退重扫';
      ov.appendChild(lbl);
    }

    function render() {
      var fa = A[aCur], fb = B[bCur];

      paintSlots(aSlots, fa, 'restart');
      paintSlots(bSlots, fb, 'dict');

      aOps.textContent = fa.ops;
      bOps.textContent = fb.ops;

      var prevRead = aCur > 0 ? A[aCur - 1].readIdx : -1;
      if (fa.dup) {
        drawRestartArrow(aStage, aOv, aSlots, prevRead, fa.readIdx);
      } else {
        clear(aOv);
      }

      clear(bOv);
      if (fb.jumped) {
        var sr = bStage.getBoundingClientRect();
        bOv.setAttribute('width', sr.width);
        bOv.setAttribute('height', sr.height);
        var from = boxGeom(bStage, bSlots, fb.prevLast);
        var to = boxGeom(bStage, bSlots, fb.start);
        if (from && to) {
          var x1 = from.cx, x2 = to.cx, y0 = from.top;
          bOv.appendChild(svgEl('path', {
            d: 'M ' + x1 + ' ' + y0 + ' C ' + x1 + ' ' + (y0 - 26) + ', ' + x2 + ' ' + (y0 - 26) + ', ' + x2 + ' ' + y0,
            fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2', 'stroke-linecap': 'round'
          }));
          bOv.appendChild(svgEl('path', {
            d: 'M ' + (x2 - 4.5) + ' ' + (y0 - 6) + ' L ' + x2 + ' ' + y0 + ' L ' + (x2 + 4.5) + ' ' + (y0 - 6),
            fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2',
            'stroke-linecap': 'round', 'stroke-linejoin': 'round'
          }));
          var lbl = svgEl('text', {
            x: (x1 + x2) / 2, y: y0 - 18, fill: 'var(--foreground)', 'font-size': '11',
            'text-anchor': 'middle', 'paint-order': 'stroke', stroke: 'var(--background)',
            'stroke-width': '4', 'stroke-linejoin': 'round'
          });
          lbl.textContent = '直接跳过';
          bOv.appendChild(lbl);
        }
      }

      clear(aNote);
      clear(bNote);
      if (fa.dup) {
        aNote.appendChild(el('span', '', '⚠️ 读到 ' + CMP_CHARS[fa.readIdx] + ' 时发现重复：左端只挪 1 格到 ' +
          fa.start + '，指针将回退到 ' + fa.start + ' 把这段重扫一遍。'));
      } else {
        aNote.appendChild(el('span', '', '正在读下标 ' + fa.readIdx + '（' + CMP_CHARS[fa.readIdx] + '），窗口 = "' + fa.window + '"'));
      }
      if (fb.jumped) {
        bNote.appendChild(el('span', '', '✓ 读到 ' + CMP_CHARS[fb.readIdx] + ' 时发现重复：左端直接跳到 ' +
          fb.start + '，之前那段永远不会再被读第二次。'));
      } else {
        bNote.appendChild(el('span', '', '正在读下标 ' + fb.readIdx + '（' + CMP_CHARS[fb.readIdx] + '），窗口 = "' + fb.window + '"'));
      }

      var aDone = aCur >= A.length - 1, bDone = bCur >= B.length - 1;
      clear(resultEl);
      if (aDone && bDone) {
        var ratio = (A.length / B.length).toFixed(1);
        resultEl.appendChild(el('span', '', '同一个输入（' + CMP_CHARS.length + ' 个字符），'));
        resultEl.appendChild(el('span', 'big', '重启版扫描 ' + A.length + ' 次'));
        resultEl.appendChild(el('span', '', '，'));
        resultEl.appendChild(el('span', 'big', '字典版扫描 ' + B.length + ' 次'));
        resultEl.appendChild(el('span', '', '，相差 ' + ratio + ' 倍。串长 n 时重启版约 n(n+1)/2 次、字典版恒为 n 次，差距随 n 线性放大 —— n = 5×10⁴ 时约 100 秒。'));
      } else {
        resultEl.appendChild(el('span', '', '播放中…'));
      }

      playBtn.textContent = timer ? '暂停' : '播放';
      stepBtn.disabled = !!timer;
    }

    function advance() {
      if (aCur < A.length - 1) aCur++;
      if (bCur < B.length - 1) bCur++;
      render();
    }

    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function toggle() {
      if (timer) { stop(); render(); return; }
      if (aCur >= A.length - 1 && bCur >= B.length - 1) { aCur = 0; bCur = 0; }
      timer = setInterval(function () {
        if (aCur >= A.length - 1 && bCur >= B.length - 1) { stop(); render(); return; }
        advance();
      }, 130);
      render();
    }

    playBtn.addEventListener('click', toggle);
    stepBtn.addEventListener('click', function () { stop(); advance(); });
    resetBtn.addEventListener('click', function () { stop(); aCur = 0; bCur = 0; render(); });
    render();
  }

  /* ==================================================================
     三、代码标签页
     ================================================================== */

  var SNIPPETS = {
    opt: [
      'class Solution:',
      '    """推荐提交版本：字典 + 单趟扫描，O(n)。"""',
      '',
      '    def lengthOfLongestSubstring(self, s: str) -> int:',
      '        last = {}        # 字符 -> 上一次出现的下标',
      '        start = 0        # 窗口左端，只增不减',
      '        max_len = 0',
      '',
      '        for i, ch in enumerate(s):',
      '            if ch in last and last[ch] >= start:',
      '                start = last[ch] + 1     # 左端直接跳到冲突字符之后',
      '            last[ch] = i',
      '            max_len = max(max_len, i - start + 1)',
      '',
      '        return max_len'
    ].join('\n'),
    set: [
      'class Solution:',
      '    """等价写法：双指针 + 集合，O(n)。"""',
      '',
      '    def lengthOfLongestSubstring(self, s: str) -> int:',
      '        seen = set()',
      '        left = 0',
      '        max_len = 0',
      '',
      '        for right, ch in enumerate(s):',
      '            while ch in seen:',
      '                seen.remove(s[left])',
      '                left += 1',
      '            seen.add(ch)',
      '            max_len = max(max_len, right - left + 1)',
      '',
      '        return max_len'
    ].join('\n'),
    restart: [
      'class Solution:',
      '    """初版：发现重复后左端只回退一格并整段重扫。',
      '',
      '    结果正确，但最坏 O(n^2)，会超时。',
      '    """',
      '',
      '    def lengthOfLongestSubstring(self, s: str) -> int:',
      '        if s is None:',
      '            return 0',
      '        if len(s) == 1:',
      '            return 1',
      '',
      '        start, next_i, max_len, chars = 0, 0, 0, set()',
      '        while next_i < len(s):',
      '            before = len(chars)',
      '            chars.add(s[next_i])',
      '            if len(chars) > max_len:',
      '                max_len = len(chars)',
      '            next_i += 1',
      '            if len(chars) == before:      # 出现重复',
      '                start += 1                # ← 问题：只回退一格',
      '                next_i = start',
      '                chars.clear()',
      '        return max_len'
    ].join('\n')
  };

  var PY_KEYWORDS = /^(def|class|return|if|elif|else|for|while|in|not|and|or|import|from|as|None|True|False|lambda|break|continue|pass|raise|with|try|except|finally|yield|global|self)$/;

  function escapeHtml(t) {
    return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function highlightPython(src) {
    var out = '';
    var i = 0, quote = null, buf = '';
    function flushPlain() {
      if (!buf) return;
      var parts = buf.split(/(\b)/);
      parts.forEach(function (p) {
        if (!p) return;
        if (PY_KEYWORDS.test(p)) out += '<span class="k">' + escapeHtml(p) + '</span>';
        else out += escapeHtml(p);
      });
      buf = '';
    }
    while (i < src.length) {
      var c = src[i];
      if (quote) {
        if (c === '\\') { buf += c + (src[i + 1] || ''); i += 2; continue; }
        if (c === quote) { out += '<span class="s">' + escapeHtml(buf + c) + '</span>'; buf = ''; quote = null; i++; continue; }
        buf += c; i++; continue;
      }
      if (c === '"' || c === "'") { flushPlain(); quote = c; buf = c; i++; continue; }
      if (c === '#') {
        flushPlain();
        var nl = src.indexOf('\n', i);
        if (nl < 0) nl = src.length;
        out += '<span class="c">' + escapeHtml(src.slice(i, nl)) + '</span>';
        i = nl; continue;
      }
      buf += c; i++;
    }
    flushPlain();
    return out;
  }

  function initTabs() {
    var tabsEl = document.getElementById('code-tabs');
    if (!tabsEl) return;
    var body = document.getElementById('code-body');
    var buttons = tabsEl.querySelectorAll('button');
    function show(key) {
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute('aria-selected', String(b.getAttribute('data-tab') === key));
      });
      body.innerHTML = highlightPython(SNIPPETS[key]);
    }
    Array.prototype.forEach.call(buttons, function (b) {
      b.addEventListener('click', function () { show(b.getAttribute('data-tab')); });
    });
    show('opt');
  }

  /* ---------------- 启动 ---------------- */
  function boot() {
    initExplain();
    initCompare();
    initTabs();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
