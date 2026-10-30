/* ==================================================================
   LeetCode Learn · 通用动图播放器
   ------------------------------------------------------------------
   页面本身不含任何「题目相关」逻辑：题目数据全部由 tools/build.py
   从 Python 轨迹函数导出，注入 #problem-data，前端只负责播放。
   新增一种可视化 = 在 RENDERERS 里注册一个渲染函数。
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

  /* ---------------- 窗口型渲染器 ---------------- */

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

  function geom(stage, slots, i) {
    if (!slots[i]) return null;
    var sr = stage.getBoundingClientRect();
    var r = slots[i].box.getBoundingClientRect();
    return {
      left: r.left - sr.left, right: r.right - sr.left,
      top: r.top - sr.top, bottom: r.bottom - sr.top,
      cx: (r.left + r.right) / 2 - sr.left
    };
  }

  function paintBoxes(slots, frame, n) {
    for (var k = 0; k < n; k++) {
      var cls = 'v-box';
      if (k === frame.i) cls += ' is-cur';
      else if (frame.dropped && frame.dropped.indexOf(k) >= 0) cls += ' is-drop';
      else if (frame.window && k >= frame.window[0] && k <= frame.window[1]) cls += ' is-win';
      else if (k < frame.j) cls += ' is-out';
      else if (k > frame.i) cls += ' is-future';
      slots[k].box.className = cls;
      slots[k].idx.className = 'v-idx' + (k === frame.i ? ' is-cur' : '');
    }
  }

  function drawOverlay(stage, ov, slots, frame, prev) {
    clear(ov);
    var sr = stage.getBoundingClientRect();
    ov.setAttribute('width', sr.width);
    ov.setAttribute('height', sr.height);

    // 窗口区间托架
    if (frame.window) {
      var a = geom(stage, slots, frame.window[0]);
      var b = geom(stage, slots, frame.window[1]);
      if (a && b) {
        var idxBottom = slots[frame.i].idx.getBoundingClientRect().bottom - sr.top;
        var my = idxBottom + 9;
        ov.appendChild(svgEl('path', {
          d: 'M ' + a.left + ' ' + my + ' L ' + a.left + ' ' + (my + 4) +
             ' L ' + b.right + ' ' + (my + 4) + ' L ' + b.right + ' ' + my,
          fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '1.5', 'stroke-linecap': 'round'
        }));
        var t1 = svgEl('text', { x: a.left, y: my + 18, fill: 'var(--muted-foreground)', 'font-size': '11' });
        t1.textContent = 'start';
        ov.appendChild(t1);
        var narrow = (b.right - a.left) < 46;
        var t2 = svgEl('text', {
          x: b.right, y: my + (narrow ? 31 : 18), fill: 'var(--muted-foreground)',
          'font-size': '11', 'text-anchor': 'end'
        });
        t2.textContent = 'i = ' + frame.i;
        ov.appendChild(t2);
      }
    }

    // 左端向前跳
    if (frame.jump) {
      var from = geom(stage, slots, frame.jump.from);
      var to = geom(stage, slots, frame.jump.to);
      if (from && to) {
        var x1 = from.cx, x2 = to.cx, y0 = from.top;
        ov.appendChild(svgEl('path', {
          d: 'M ' + x1 + ' ' + y0 + ' C ' + x1 + ' ' + (y0 - 34) + ', ' + x2 + ' ' + (y0 - 34) + ', ' + x2 + ' ' + y0,
          fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2', 'stroke-linecap': 'round'
        }));
        ov.appendChild(svgEl('path', {
          d: 'M ' + (x2 - 4.5) + ' ' + (y0 - 7) + ' L ' + x2 + ' ' + y0 + ' L ' + (x2 + 4.5) + ' ' + (y0 - 7),
          fill: 'none', stroke: 'var(--viz-series-1)', 'stroke-width': '2',
          'stroke-linecap': 'round', 'stroke-linejoin': 'round'
        }));
        var lbl = svgEl('text', {
          x: (x1 + x2) / 2, y: y0 - 22, fill: 'var(--foreground)', 'font-size': '11.5',
          'text-anchor': 'middle', 'paint-order': 'stroke', stroke: 'var(--background)',
          'stroke-width': '4', 'stroke-linejoin': 'round'
        });
        lbl.textContent = frame.jump.label;
        ov.appendChild(lbl);
      }
    }

    // 指针回退
    if (prev && frame.i < prev.i) {
      var bf = geom(stage, slots, prev.i);
      var bt = geom(stage, slots, frame.i);
      if (bf && bt) {
        var bx1 = bf.cx, bx2 = bt.cx, by0 = bf.bottom;
        ov.appendChild(svgEl('path', {
          d: 'M ' + bx1 + ' ' + by0 + ' C ' + bx1 + ' ' + (by0 + 26) + ', ' + bx2 + ' ' + (by0 + 26) + ', ' + bx2 + ' ' + by0,
          fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '2', 'stroke-linecap': 'round'
        }));
        ov.appendChild(svgEl('path', {
          d: 'M ' + (bx2 - 4.5) + ' ' + (by0 + 7) + ' L ' + bx2 + ' ' + by0 + ' L ' + (bx2 + 4.5) + ' ' + (by0 + 7),
          fill: 'none', stroke: 'var(--viz-series-2)', 'stroke-width': '2',
          'stroke-linecap': 'round', 'stroke-linejoin': 'round'
        }));
        var bl = svgEl('text', {
          x: (bx1 + bx2) / 2, y: by0 + 30, fill: 'var(--foreground)', 'font-size': '11',
          'text-anchor': 'middle', 'paint-order': 'stroke', stroke: 'var(--background)',
          'stroke-width': '4', 'stroke-linejoin': 'round'
        });
        bl.textContent = frame.backLabel || '回退';
        ov.appendChild(bl);
      }
    }
  }

  function renderVars(container, vars) {
    clear(container);
    if (!vars) return;
    var keys = Object.keys(vars);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i], v = vars[k];
      var label = el('span', 'var-label', k);
      container.appendChild(label);
      if (v && typeof v === 'object') {
        var ks = Object.keys(v);
        for (var j = 0; j < ks.length; j++) {
          var chip = el('span', 'v-chip');
          chip.appendChild(el('b', '', "'" + ks[j] + "'"));
          chip.appendChild(el('span', 'arrow', '→'));
          chip.appendChild(el('span', '', String(v[ks[j]])));
          container.appendChild(chip);
        }
      } else {
        container.appendChild(el('span', 'v-chip', k + ' = ' + v));
      }
    }
  }

  /* ---------------- 单条轨道 ---------------- */

  function LaneView(lane, opts) {
    this.lane = lane;
    this.opts = opts || {};
    this.frames = (this.opts.frames && this.opts.frames(lane)) || lane.frames;
    this.idx = 0;
    this.root = el('div', 'lane' + (this.opts.compact ? ' lane-compact' : ''));
    this.root.innerHTML =
      '<div class="cmp-head">' +
        '<span class="name"></span>' +
        '<span class="badge"></span>' +
        '<span class="counter"></span>' +
      '</div>' +
      '<div class="v-status"></div>' +
      '<div class="v-stage"><svg class="v-ov" aria-hidden="true"></svg><div class="v-slots"></div></div>' +
      '<div class="v-chips"></div>' +
      '<div class="v-detail"></div>';
    this.headName = this.root.querySelector('.name');
    this.headBadge = this.root.querySelector('.badge');
    this.headCounter = this.root.querySelector('.counter');
    this.statusEl = this.root.querySelector('.v-status');
    this.stageEl = this.root.querySelector('.v-stage');
    this.ovEl = this.root.querySelector('svg.v-ov');
    this.slotsEl = this.root.querySelector('.v-slots');
    this.chipsEl = this.root.querySelector('.v-chips');
    this.detailEl = this.root.querySelector('.v-detail');
    this.slots = buildSlots(this.slotsEl, (this.opts.input || lane.input || '').split(''));
    this.headName.textContent = lane.name || '';
    this.headBadge.textContent = lane.badge || '';
    this.headBadge.className = 'badge' + (lane.variant && lane.variant !== 'neutral' ? ' ' + lane.variant : '');
    if (!lane.badge) this.headBadge.style.display = 'none';
  }

  LaneView.prototype.setFrame = function (i) {
    this.idx = Math.max(0, Math.min(i, this.frames.length - 1));
    var frame = this.frames[this.idx];
    var prev = this.idx > 0 ? this.frames[this.idx - 1] : null;
    paintBoxes(this.slots, frame, this.slots.length);

    clear(this.statusEl);
    var statusEl = this.statusEl;
    function stat(k, v) {
      var s = el('span');
      s.appendChild(el('span', 'k', k + ' '));
      s.appendChild(el('span', 'v', v));
      statusEl.appendChild(s);
    }
    stat('i', '= ' + frame.i);
    if (frame.j !== undefined && frame.j !== null) stat('j', '= ' + frame.j);
    if (frame.window) {
      var txt = (this.opts.input || this.lane.input || '').slice(frame.window[0], frame.window[1] + 1);
      stat('窗口', '[' + frame.window[0] + ', ' + frame.window[1] + '] = "' + txt + '"');
    }
    renderVars(this.chipsEl, frame.vars);

    clear(this.detailEl);
    if (frame.label) this.detailEl.appendChild(el('span', '', frame.label));
    if (frame.note) this.detailEl.appendChild(el('span', 'v-note', '  ' + frame.note));

    this.headCounter.innerHTML = '第 <b>' + (this.idx + 1) + '</b> / ' + this.frames.length + ' 帧';
    drawOverlay(this.stageEl, this.ovEl, this.slots, frame, prev);
    return frame;
  };

  /* ---------------- 播放器（可管理多条轨道） ---------------- */

  function Player(container, lanes, opts) {
    this.opts = opts || {};
    this.lanes = lanes.map(function (l) { return new LaneView(l, opts.laneOpts); });
    this.pos = 0;
    this.timer = null;
    this.maxLen = Math.max(1, Math.max.apply(null, this.lanes.map(function (l) { return l.frames.length; })));

    var self = this;
    var bar = el('div', 'v-bar');
    var title = el('span', 'v-title', this.opts.title || '');
    var pos = el('span', 'v-pos');
    var btns = el('div', 'v-btns');
    var bPlay = el('button', 'v-btn primary', '播放');
    var bStep = el('button', 'v-btn', '单步');
    var bReset = el('button', 'v-btn', '重置');
    btns.appendChild(bPlay); btns.appendChild(bStep); btns.appendChild(bReset);
    bar.appendChild(title); bar.appendChild(pos); bar.appendChild(btns);

    this.lanesEl = el('div', 'lanes');
    this.lanes.forEach(function (l) { self.lanesEl.appendChild(l.root); });

    this.resultEl = el('div', 'cmp-result');
    this.posEl = pos;
    this.bPlay = bPlay; this.bStep = bStep;

    container.appendChild(bar);
    container.appendChild(this.lanesEl);
    if (this.opts.showResult) container.appendChild(this.resultEl);

    bPlay.addEventListener('click', function () { self.toggle(); });
    bStep.addEventListener('click', function () { self.stop(); self.advance(); });
    bReset.addEventListener('click', function () { self.stop(); self.seek(0); });
    this.onKey = function (e) {
      if (e.key === 'ArrowRight') { self.stop(); self.advance(); }
      if (e.key === 'ArrowLeft') { self.stop(); self.seek(self.pos - 1); }
    };
    document.addEventListener('keydown', this.onKey);
    this.seek(0);
  }

  Player.prototype.seek = function (p) {
    this.pos = Math.max(0, Math.min(p, this.maxLen - 1));
    this.lanes.forEach(function (l) { l.setFrame(Math.min(this.pos, l.frames.length - 1)); }, this);
    this.render();
  };
  Player.prototype.advance = function () { this.seek(this.pos + 1); };
  Player.prototype.toggle = function () {
    var self = this;
    if (this.timer) { this.stop(); return; }
    if (this.pos >= this.maxLen - 1) this.seek(0);
    this.timer = setInterval(function () {
      if (self.pos >= self.maxLen - 1) { self.stop(); return; }
      self.advance();
    }, this.opts.interval || 850);
    this.render();
  };
  Player.prototype.stop = function () {
    if (this.timer) { clearInterval(this.timer); this.timer = null; }
    this.render();
  };
  Player.prototype.render = function () {
    this.posEl.textContent = '第 ' + (this.pos + 1) + ' / ' + this.maxLen + ' 步';
    this.bPlay.textContent = this.timer ? '暂停' : '播放';
    this.bStep.disabled = !!this.timer;
    if (!this.opts.showResult) return;
    clear(this.resultEl);
    if (this.pos >= this.maxLen - 1) {
      var parts = this.lanes.map(function (l) {
        return l.lane.name + ' 需要 <b>' + l.frames.length + '</b> 步';
      });
      var ratio = '';
      if (this.lanes.length >= 2) {
        var counts = this.lanes.map(function (l) { return l.frames.length; });
        var mx = Math.max.apply(null, counts);
        var mn = Math.min.apply(null, counts);
        if (mn > 0) ratio = '，相差 <b>' + (mx / mn).toFixed(1) + '</b> 倍';
      }
      this.resultEl.appendChild(el('span', '', '同一个输入下，' + parts.join('，') + ratio + '。'));
    } else {
      this.resultEl.appendChild(el('span', '', '播放中…'));
    }
  };

  /* ---------------- 代码标签页 ---------------- */

  function initTabs() {
    var wrap = document.querySelector('[data-tabs]');
    if (!wrap) return;
    var buttons = wrap.querySelectorAll('button');
    Array.prototype.forEach.call(buttons, function (b) {
      b.addEventListener('click', function () {
        var key = b.getAttribute('data-snippet');
        Array.prototype.forEach.call(buttons, function (o) {
          o.setAttribute('aria-selected', String(o === b));
        });
        var panels = document.querySelectorAll('[data-snippet-panel]');
        Array.prototype.forEach.call(panels, function (p) {
          p.hidden = p.getAttribute('data-snippet-panel') !== key;
        });
      });
    });
  }

  /* ---------------- 启动 ---------------- */

  function boot() {
    initTabs();
    var dataEl = document.getElementById('problem-data');
    var host = document.getElementById('player');
    if (!dataEl || !host) return;
    var data;
    try { data = JSON.parse(dataEl.textContent); }
    catch (e) { host.appendChild(el('div', 'note', '轨迹数据解析失败：' + e.message)); return; }

    var lanes = data.lanes || [];
    if (!lanes.length) return;

    // 逐步演示：第一条轨道
    var main = el('div', 'card');
    host.appendChild(main);
    var mainPlayer = new Player(main, [lanes[0]], {
      title: (lanes[0].name || '') + ' · 逐步演示',
      interval: 850
    });

    // 代码面板（挂在主轨道下方）
    if (lanes[0].showCode && lanes[0].codeLines && lanes[0].codeLines.length) {
      var codeCard = el('div', 'card');
      codeCard.style.marginTop = '14px';
      var pre = el('pre', 'v-code');
      lanes[0].codeLines.forEach(function (h, idx) {
        var line = el('span', 'v-cl');
        line.dataset.idx = String(idx);
        line.innerHTML = '<span class="v-num">' + (idx + 1) + '  </span>' + h;
        pre.appendChild(line);
      });
      codeCard.appendChild(pre);
      main.appendChild(codeCard);
      var prevIdx = -1;
      var sync = function () {
        var frame = lanes[0].frames[mainPlayer.pos] || {};
        var want = typeof frame._codeIdx === 'number' ? frame._codeIdx : -1;
        if (want === prevIdx) return;
        Array.prototype.forEach.call(pre.querySelectorAll('.v-cl'), function (n) {
          n.classList.toggle('is-active', Number(n.dataset.idx) === want);
        });
        prevIdx = want;
      };
      var origSetFrame = mainPlayer.lanes[0].setFrame.bind(mainPlayer.lanes[0]);
      mainPlayer.lanes[0].setFrame = function (i) { var f = origSetFrame(i); sync(); return f; };
      sync();
    }

    // 横向对比：所有轨道并行
    if (lanes.length > 1) {
      var cmpCard = el('div', 'card');
      cmpCard.style.marginTop = '16px';
      host.appendChild(cmpCard);
      new Player(cmpCard, lanes, {
        title: data.compareTitle || '同一个输入，两种写法并行跑一遍',
        interval: 130,
        showResult: true,
        laneOpts: {
          compact: true,
          input: (lanes[0].compareInput || lanes[0].input),
          frames: function (lane) { return lane.compareFrames || lane.frames; }
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
