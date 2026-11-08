/* ==================================================================
   LeetCode Learn · 通用动图播放器
   ------------------------------------------------------------------
   页面不含任何「题目相关」逻辑：题目数据由 tools/build.py 从 Python
   轨迹函数导出，注入 #problem-data，前端只负责播放。

   新增一种可视化 = 在 RENDERERS 里注册一个渲染函数，
   再在 problems/*.json 里把 demo.type 指过去即可。
   ================================================================== */
(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var RENDERERS = {};          // 可视化类型注册表：新增一种画法 = 注册一个渲染器

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

  /* ==================================================================
     渲染器 1：array —— 一排 token + 当前指针 + 可选区间 / 配对
     适用于：滑动窗口、双指针、哈希表遍历、数组扫描……
     ================================================================== */

  function buildSlots(container, tokens) {
    clear(container);
    var boxes = [];
    for (var i = 0; i < tokens.length; i++) {
      var slot = el('div', 'v-slot');
      var box = el('div', 'v-box', tokens[i]);
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
      else if (frame.marks && frame.marks.indexOf(k) >= 0) cls += ' is-mark';
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

    // 区间托架
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
        var labels = frame.bracketLabels || ['start', 'i = ' + frame.i];
        var t1 = svgEl('text', { x: a.left, y: my + 18, fill: 'var(--muted-foreground)', 'font-size': '11' });
        t1.textContent = labels[0];
        ov.appendChild(t1);
        var narrow = (b.right - a.left) < 46;
        var t2 = svgEl('text', {
          x: b.right, y: my + (narrow ? 31 : 18), fill: 'var(--muted-foreground)',
          'font-size': '11', 'text-anchor': 'end'
        });
        t2.textContent = labels[1];
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

  /* ==================================================================
     渲染器 2：digits —— 竖式加法（两行数字 + 进位 + 结果）
     帧字段：col（从最低位数的列号）digit carry result
     ================================================================== */

  RENDERERS.array = {
    build: function (view, lane) {
      view.tokens = view.tokens || lane.tokens || (lane.input || '').split('');
      view.ovEl = svgEl('svg', { class: 'v-ov' });
      view.slotsEl = el('div', 'v-slots');
      view.stageEl.appendChild(view.ovEl);
      view.stageEl.appendChild(view.slotsEl);
      view.slots = buildSlots(view.slotsEl, view.tokens);
    },
    update: function (view, frame, prev) {
      paintBoxes(view.slots, frame, view.slots.length);
      drawOverlay(view.stageEl, view.ovEl, view.slots, frame, prev);
    }
  };

  RENDERERS.digits = {
    status: function (frame) {
      var out = [];
      if (frame.col !== undefined && frame.col !== null) out.push(['列', '= ' + frame.col + '（从右数）']);
      if (frame.digit !== undefined && frame.digit !== null) out.push(['本位', '= ' + frame.digit]);
      return out;
    },
    build: function (view, lane) {
      view.rows = view.rows || lane.rows || [[]];
      var maxLen = 0;
      view.rows.forEach(function (r) { maxLen = Math.max(maxLen, r.length); });
      view.ncols = maxLen + 1;                 // 多留一列给最高位的进位
      view.ovEl = svgEl('svg', { class: 'v-ov' });
      view.gridEl = el('div', 'dgrid');
      view.stageEl.appendChild(view.ovEl);
      view.stageEl.appendChild(view.gridEl);
    },
    update: function (view, frame) {
      clear(view.gridEl);
      var n = view.ncols;
      var absCol = n - 1 - (frame.col || 0);   // 显示列（从左数）
      var result = frame.result || [];

      // 两个（或多个）加数行，右对齐
      view.rows.forEach(function (row) {
        var r = el('div', 'drow');
        for (var c = 0; c < n; c++) {
          var k = c - (n - row.length);
          var tok = k >= 0 ? row[k] : '';
          var box = el('div', 'd-box' + (tok === '' ? ' is-empty' : ''), tok);
          if (c === absCol) box.classList.add('is-cur');
          r.appendChild(box);
        }
        view.gridEl.appendChild(r);
      });

      // 进位行：进位流向左边一列
      var cr = el('div', 'drow dcarry');
      for (var c2 = 0; c2 < n; c2++) {
        var cell = el('div', 'dcell');
        if (c2 === absCol - 1 && frame.carry) cell.appendChild(el('div', 'd-carry', '←1'));
        cr.appendChild(cell);
      }
      view.gridEl.appendChild(cr);

      // 结果行：result[k] 是第 k 个产出的位（从低位起），显示在从右数第 k 列
      var rr = el('div', 'drow dresult');
      for (var c3 = 0; c3 < n; c3++) {
        var kk = n - 1 - c3;
        var digit = (kk >= 0 && kk < result.length) ? String(result[kk]) : '';
        var rb = el('div', 'd-box d-res' + (digit === '' ? ' is-empty' : ''), digit);
        if (kk === result.length - 1) rb.classList.add('is-new');
        rr.appendChild(rb);
      }
      view.gridEl.appendChild(rr);
    }
  };

  /* ==================================================================
     渲染器 3：cells —— 一排表格单元（DP 表格 / 调用序列）
     帧字段：values（单元格文本）col（当前格）from（来源格）caption（浮标）
     ================================================================== */

  RENDERERS.cells = {
    status: function (frame) {
      var out = [];
      if (frame.values) out.push(['已算出', '= ' + frame.values.length + ' 格']);
      if (frame.from && frame.from.length) {
        out.push(['取自', '= ' + frame.from.map(function (x) { return 'f(' + x + ')'; }).join(' + ')]);
      }
      return out;
    },
    build: function (view, lane) {
      view.stageEl.classList.add('stage-cells');
      view.ovEl = svgEl('svg', { class: 'v-ov' });
      view.cellsEl = el('div', 'cells');
      view.capEl = el('div', 'cell-cap-layer');
      view.stageEl.appendChild(view.ovEl);
      view.stageEl.appendChild(view.cellsEl);
      view.stageEl.appendChild(view.capEl);
    },
    update: function (view, frame) {
      clear(view.cellsEl);
      clear(view.capEl);
      var values = frame.values || [];
      var curCell = null;
      for (var i = 0; i < values.length; i++) {
        var cell = el('div', 'cell');
        if (frame.from && frame.from.indexOf(i) >= 0) cell.classList.add('is-from');
        if (i === frame.col) { cell.classList.add('is-cur'); curCell = cell; }
        cell.appendChild(el('span', 'cell-v', values[i]));
        view.cellsEl.appendChild(cell);
      }
      // 浮标：定位到当前格子上方，并夹在容器内，避免溢出边界
      if (curCell && frame.caption) {
        var cap = el('div', 'cell-cap', frame.caption);
        view.capEl.appendChild(cap);
        var sr = view.stageEl.getBoundingClientRect();
        var cr = curCell.getBoundingClientRect();
        var pr = cap.getBoundingClientRect();
        var left = cr.left - sr.left + cr.width / 2 - pr.width / 2;
        left = Math.max(0, Math.min(left, sr.width - pr.width));
        var top = cr.top - sr.top - pr.height - 6;
        cap.style.left = left + 'px';
        cap.style.top = Math.max(0, top) + 'px';
      }
    }
  };

  /* ==================================================================
     渲染器 4：triangle —— 居中的三角形（杨辉三角这类二维递推结构）
     帧字段：rows（二维数组）row col from（[[r,c],...]）caption
     ================================================================== */

  RENDERERS.triangle = {
    status: function (frame) {
      var out = [];
      if (frame.caption) out.push(['当前', '= ' + frame.caption]);
      if (frame.row !== undefined && frame.row !== null) out.push(['当前行', '= 第 ' + frame.row + ' 行']);
      if (frame.rows) out.push(['已生成', '= ' + frame.rows.length + ' 行']);
      return out;
    },
    build: function (view, lane) {
      view.stageEl.classList.add('stage-triangle');
      view.triEl = el('div', 'tri');
      view.stageEl.appendChild(view.triEl);
    },
    update: function (view, frame) {
      clear(view.triEl);
      var rows = frame.rows || [];
      var sources = frame.from || [];
      var curCell = null;

      rows.forEach(function (row, ri) {
        var rowEl = el('div', 'tri-row');
        row.forEach(function (v, ci) {
          var cell = el('div', 'cell');
          var isSrc = sources.some(function (p) { return p[0] === ri && p[1] === ci; });
          if (isSrc) cell.classList.add('is-from');
          if (ri === frame.row && ci === frame.col) { cell.classList.add('is-cur'); curCell = cell; }
          cell.appendChild(el('span', 'cell-v', String(v)));
          rowEl.appendChild(cell);
        });
        view.triEl.appendChild(rowEl);
      });
    }
  };

  /* ==================================================================
     渲染器 5：row —— 横向的一行（119 只要一行，不是整张三角）
     帧字段：rows（二维数组，每个元素是一条横向带）labels（每条带的标题）
             row（当前所在的带）col（当前列）from（来源格 [[带,列],...]）
     ================================================================== */

  RENDERERS.row = {
    status: function (frame) {
      var out = [];
      if (frame.caption) out.push(['当前', '= ' + frame.caption]);
      if (frame.row !== undefined && frame.row !== null && frame.col !== undefined && frame.col !== null) {
        out.push(['算到', '= 第 ' + frame.col + ' 格']);
      }
      if (frame.rows && frame.rows.length) {
        // 目标行 = 最后一条带
        out.push(['格子数', '= ' + (frame.rows[frame.rows.length - 1] || []).length]);
      }
      return out;
    },
    build: function (view, lane) {
      view.stageEl.classList.add('stage-row');
      view.rowWrapEl = el('div', 'rwrap');
      view.stageEl.appendChild(view.rowWrapEl);
    },
    update: function (view, frame) {
      clear(view.rowWrapEl);
      var rows = frame.rows || [];
      var labels = frame.labels || [];
      var sources = frame.from || [];

      rows.forEach(function (strip, ri) {
        // 最后一条带 = 正在算的那一行；更早的带 = 上一行（来源，压暗）
        var stripEl = el('div', 'rstrip' + (ri === rows.length - 1 ? ' is-target' : ' is-prev'));
        if (labels[ri]) stripEl.appendChild(el('div', 'rstrip-label', labels[ri]));
        var cellsEl = el('div', 'rcells');
        (strip || []).forEach(function (v, ci) {
          var cell = el('div', 'cell');
          if (v === null || v === undefined) {
            cell.classList.add('is-empty');
          } else {
            cell.appendChild(el('span', 'cell-v', String(v)));
          }
          var isSrc = sources.some(function (p) { return p[0] === ri && p[1] === ci; });
          if (isSrc) cell.classList.add('is-from');
          if (ri === frame.row && ci === frame.col) cell.classList.add('is-cur');
          cellsEl.appendChild(cell);
        });
        stripEl.appendChild(cellsEl);
        view.rowWrapEl.appendChild(stripEl);
      });
    }
  };

  /* ==================================================================
     轨道视图
     ================================================================== */

  function renderVars(container, vars) {
    clear(container);
    if (!vars) return;
    var keys = Object.keys(vars);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i], v = vars[k];
      container.appendChild(el('span', 'var-label', k));
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
        container.appendChild(el('span', 'v-chip', String(v)));
      }
    }
  }

  function LaneView(lane, opts) {
    this.lane = lane;
    this.opts = opts || {};
    this.frames = (this.opts.frames && this.opts.frames(lane)) || lane.frames || [];
    this.root = el('div', 'lane' + (this.opts.compact ? ' lane-compact' : ''));
    this.root.innerHTML =
      '<div class="cmp-head">' +
        '<span class="name"></span>' +
        '<span class="badge"></span>' +
        '<span class="counter"></span>' +
      '</div>' +
      '<div class="v-status"></div>' +
      '<div class="v-stage"></div>' +
      '<div class="v-chips"></div>' +
      '<div class="v-detail"></div>';
    this.headName = this.root.querySelector('.name');
    this.headBadge = this.root.querySelector('.badge');
    this.headCounter = this.root.querySelector('.counter');
    this.statusEl = this.root.querySelector('.v-status');
    this.stageEl = this.root.querySelector('.v-stage');
    this.chipsEl = this.root.querySelector('.v-chips');
    this.detailEl = this.root.querySelector('.v-detail');

    var type = this.opts.type || lane.type || 'array';
    this.renderer = RENDERERS[type] || RENDERERS.array;

    function resolve(defaults, override) {
      var v = (typeof override === 'function') ? override(lane) : override;
      return (v === undefined || v === null || (Array.isArray(v) && !v.length)) ? defaults : v;
    }
    this.tokens = resolve(lane.tokens, this.opts.tokens);
    this.rows = resolve(lane.rows, this.opts.rows);

    this.renderer.build(this, lane, this.opts);

    this.headName.textContent = lane.name || '';
    this.headBadge.textContent = lane.badge || '';
    this.headBadge.className = 'badge' + (lane.variant && lane.variant !== 'neutral' ? ' ' + lane.variant : '');
    if (!lane.badge) this.headBadge.style.display = 'none';
  }

  LaneView.prototype.setFrame = function (i) {
    this.idx = Math.max(0, Math.min(i, this.frames.length - 1));
    var frame = this.frames[this.idx];
    var prev = this.idx > 0 ? this.frames[this.idx - 1] : null;
    this.renderer.update(this, frame, prev);

    clear(this.statusEl);
    var statusEl = this.statusEl;
    function stat(k, v) {
      var s = el('span');
      s.appendChild(el('span', 'k', k + ' '));
      s.appendChild(el('span', 'v', v));
      statusEl.appendChild(s);
    }
    var stats = this.renderer.status ? this.renderer.status(frame, this) : null;
    if (!stats) {
      stats = [];
      if (frame.i !== undefined && frame.i !== null) stats.push(['i', '= ' + frame.i]);
      if (frame.j !== undefined && frame.j !== null) stats.push(['j', '= ' + frame.j]);
      if (frame.window) {
        var toks = this.tokens || (this.lane.input || '').split('');
        var txt = toks.slice(frame.window[0], frame.window[1] + 1).join(' ');
        stats.push(['区间', '[' + frame.window[0] + ', ' + frame.window[1] + '] = ' + txt]);
      }
    }
    stats.forEach(function (pair) { stat(pair[0], pair[1]); });
    renderVars(this.chipsEl, frame.vars);

    clear(this.detailEl);
    if (frame.label) this.detailEl.appendChild(el('span', '', frame.label));
    if (frame.note) this.detailEl.appendChild(el('span', 'v-note', '  ' + frame.note));

    this.headCounter.innerHTML = '第 <b>' + (this.idx + 1) + '</b> / ' + this.frames.length + ' 帧';
    return frame;
  };

  /* ==================================================================
     播放器
     ================================================================== */

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

  /* ==================================================================
     目录页：按标签筛选
     ================================================================== */

  function initFilter() {
    var bar = document.querySelector('[data-tag-filter]');
    if (!bar) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll('.pcard'));
    var buttons = Array.prototype.slice.call(bar.querySelectorAll('.tag-btn'));
    var countEl = document.querySelector('[data-filter-count]');
    var listCountEl = document.querySelector('[data-list-count]');
    var total = cards.length;

    function apply(tag, pushHash) {
      var shown = 0;
      cards.forEach(function (c) {
        var tags = (c.getAttribute('data-tags') || '').split('|');
        var match = !tag || tags.indexOf(tag) >= 0;
        c.hidden = !match;
        if (match) shown++;
      });
      buttons.forEach(function (b) {
        var on = (b.getAttribute('data-tag') || '') === (tag || '');
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', String(on));
      });
      if (countEl) {
        countEl.textContent = shown === total
          ? ''
          : ('已筛选 ' + shown + ' / ' + total + ' 题');
      }
      if (listCountEl) {
        listCountEl.textContent = shown === total ? ('（' + total + '）') : ('（' + shown + ' / ' + total + '）');
      }
      if (pushHash) {
        var hash = tag ? ('#tag=' + encodeURIComponent(tag)) : '';
        if (location.hash !== hash) {
          if (hash) { history.replaceState(null, '', hash); }
          else { history.replaceState(null, '', location.pathname + location.search); }
        }
      }
    }

    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        var tag = b.getAttribute('data-tag') || '';
        // 再点一次当前选中的标签就取消筛选
        var current = buttons.filter(function (o) { return o.classList.contains('is-active'); })[0];
        var cur = current ? (current.getAttribute('data-tag') || '') : '';
        apply(tag === cur && tag ? '' : tag, true);
      });
    });

    // 卡片里的标签也可以点（它是 <a> 里的 span，所以要阻止默认跳转）
    Array.prototype.forEach.call(document.querySelectorAll('.pcard .tag-card'), function (t) {
      t.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        apply(t.getAttribute('data-tag') || '', true);
      });
    });

    // 支持分享链接：#tag=xxx
    var m = /^#tag=(.+)$/.exec(location.hash);
    if (m) {
      var tag = decodeURIComponent(m[1]);
      var known = buttons.some(function (b) { return (b.getAttribute('data-tag') || '') === tag; });
      if (known) apply(tag, false);
    }
    window.addEventListener('hashchange', function () {
      var mm = /^#tag=(.+)$/.exec(location.hash);
      apply(mm ? decodeURIComponent(mm[1]) : '', false);
    });
  }

  /* ==================================================================
     「杨辉三角 = 路径计数」交互图
     点任意一格，画出通往它的所有路径 —— 路径条数正好是 C(i, j)。
     ================================================================== */

  function initPathFigure() {
    var host = document.querySelector('[data-path-figure]');
    if (!host) return;
    var svg = host.querySelector('.pf-svg');
    var detail = host.querySelector('.pf-detail');
    var ROWS = parseInt(host.getAttribute('data-rows'), 10) || 6;
    var sel = { r: Math.min(4, ROWS - 1), c: 2 };
    if (sel.c > sel.r) sel.c = sel.r;

    function comb(n, k) {
      if (k < 0 || k > n) return 0;
      var v = 1;
      for (var i = 0; i < k; i++) v = v * (n - i) / (i + 1);
      return Math.round(v);
    }
    function triangle() {
      var t = [[1]];
      for (var r = 1; r < ROWS; r++) {
        var prev = t[r - 1], cur = [1];
        for (var j = 1; j < prev.length; j++) cur.push(prev[j - 1] + prev[j]);
        cur.push(1);
        t.push(cur);
      }
      return t;
    }
    function pathsTo(R, C) {
      var out = [];
      (function walk(r, c, path) {
        if (r === R) { if (c === C) out.push(path); return; }
        var needRight = C - c;
        var needLeft = (R - r) - needRight;
        if (needLeft > 0) walk(r + 1, c, path.concat([[r + 1, c]]));
        if (needRight > 0) walk(r + 1, c + 1, path.concat([[r + 1, c + 1]]));
      })(0, 0, [[0, 0]]);
      return out;
    }

    var TABLE = triangle();

    function draw() {
      var W = host.clientWidth || 640;
      var cellW = 46, gap = 8, rowH = 44, top = 10;
      var unit = cellW + gap;
      var H = top + ROWS * rowH + 8;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      svg.setAttribute('width', W);
      svg.setAttribute('height', H);
      clear(svg);

      function cx(r, c) { return W / 2 + (c - r / 2) * unit; }
      function cy(r) { return top + r * rowH + rowH / 2; }

      var paths = pathsTo(sel.r, sel.c);
      var m = paths.length;
      var vx = cx(sel.r, sel.c) - cx(0, 0), vy = cy(sel.r) - cy(0);
      var len = Math.sqrt(vx * vx + vy * vy) || 1;
      var px = -vy / len, py = vx / len;

      paths.forEach(function (path, idx) {
        var off = (idx - (m - 1) / 2) * 1.6;
        var pts = path.map(function (p) {
          return (cx(p[0], p[1]) + px * off).toFixed(1) + ',' + (cy(p[0]) + py * off).toFixed(1);
        }).join(' ');
        ovLine(pts);
      });

      TABLE.forEach(function (row, r) {
        row.forEach(function (v, c) {
          var isSel = (r === sel.r && c === sel.c);
          var g = svgEl('g', {});
          var rect = svgEl('rect', {
            x: cx(r, c) - cellW / 2, y: cy(r) - rowH / 2 + 4,
            width: cellW, height: rowH - 8, rx: 6,
            class: 'pf-cell' + (isSel ? ' is-sel' : '')
          });
          rect.addEventListener('click', function () { sel = { r: r, c: c }; draw(); });
          var title = svgEl('title', {});
          title.textContent = '第 ' + r + ' 行第 ' + c + ' 列 = ' + v + ' = C(' + r + ',' + c + ')';
          rect.appendChild(title);
          g.appendChild(rect);
          var t = svgEl('text', { x: cx(r, c), y: cy(r), class: 'pf-num' + (isSel ? ' is-sel' : '') });
          t.textContent = v;
          g.appendChild(t);
          svg.appendChild(g);
        });
      });

      svg.setAttribute('aria-label',
        '杨辉三角共 ' + ROWS + ' 行。选中第 ' + sel.r + ' 行第 ' + sel.c + ' 列，值为 ' +
        TABLE[sel.r][sel.c] + '，等于 C(' + sel.r + ',' + sel.c + ')，通往它共有 ' + m + ' 条路径。');

      clear(detail);
      var sp = el('span');
      sp.innerHTML = '到第 <b>' + sel.r + '</b> 行第 <b>' + sel.c + '</b> 格要走 <b>' + sel.r +
        '</b> 步，其中 <b>' + sel.c + '</b> 步向右 —— 从 ' + sel.r + ' 个位置里选 ' + sel.c +
        ' 个放「向右」，共 <b>' + m + '</b> 种选法，正是 <b>C(' + sel.r + ',' + sel.c + ') = ' +
        comb(sel.r, sel.c) + '</b>，也正是这个格子里写的数 ' + TABLE[sel.r][sel.c] + '。';
      detail.appendChild(sp);
    }

    function ovLine(points) {
      svg.appendChild(svgEl('polyline', { points: points, class: 'pf-path' }));
    }

    draw();
    if (window.ResizeObserver) new ResizeObserver(draw).observe(host);
  }

  /* ==================================================================
     「只要一行就够」交互图
     点杨辉三角的任意一行 —— 那一行只依赖上一行，更上面的行算完就能扔掉。
     ================================================================== */

  function initRowFigure() {
    var host = document.querySelector('[data-row-figure]');
    if (!host) return;
    var svg = host.querySelector('.rf-svg');
    var detail = host.querySelector('.rf-detail');
    var ROWS = parseInt(host.getAttribute('data-rows'), 10) || 8;
    var sel = Math.min(4, ROWS - 1);

    function triangle() {
      var t = [[1]];
      for (var r = 1; r < ROWS; r++) {
        var prev = t[r - 1], cur = [1];
        for (var j = 1; j < prev.length; j++) cur.push(prev[j - 1] + prev[j]);
        cur.push(1);
        t.push(cur);
      }
      return t;
    }
    var TABLE = triangle();

    function draw() {
      var W = host.clientWidth || 640;
      var cellW = 44, gap = 8, rowH = 40, top = 8;
      var unit = cellW + gap;
      var H = top + ROWS * rowH + 6;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      svg.setAttribute('width', W);
      svg.setAttribute('height', H);
      clear(svg);

      function cx(r, c) { return W / 2 + (c - r / 2) * unit; }
      function cy(r) { return top + r * rowH + rowH / 2; }

      TABLE.forEach(function (row, r) {
        row.forEach(function (v, c) {
          var isSel = (r === sel);
          var g = svgEl('g', {});
          var rect = svgEl('rect', {
            x: cx(r, c) - cellW / 2, y: cy(r) - rowH / 2 + 4,
            width: cellW, height: rowH - 8, rx: 6,
            class: 'rf-cell' + (isSel ? ' is-sel' : '')
          });
          rect.addEventListener('click', function () { sel = r; draw(); });
          var title = svgEl('title', {});
          title.textContent = '第 ' + r + ' 行：' + row.join(' ') + '（点一下选中这一行）';
          rect.appendChild(title);
          g.appendChild(rect);
          var t = svgEl('text', { x: cx(r, c), y: cy(r), class: 'rf-num' + (isSel ? ' is-sel' : '') });
          t.textContent = v;
          g.appendChild(t);
          svg.appendChild(g);
        });
      });

      var row = TABLE[sel];
      var total = 0;
      for (var i = 1; i <= sel + 1; i++) total += i;
      svg.setAttribute('aria-label',
        '杨辉三角共 ' + ROWS + ' 行。选中第 ' + sel + ' 行，共 ' + row.length +
        ' 个数：' + row.join(' ') + '。');

      clear(detail);
      var sp = el('span');
      sp.innerHTML = '选中第 <b>' + sel + '</b> 行 → <code>getRow(' + sel + ')</code> 返回 <b>[' +
        row.join(', ') + ']</b>，共 <b>' + row.length + '</b> 个数。<br>' +
        '这一行只依赖<b>上一行</b>，所以更上面的行算完就可以扔掉：' +
        '存整张三角要 <b>' + total + '</b> 个数，<b>只留一行只要 ' + row.length + ' 个</b>。';
      detail.appendChild(sp);
    }

    draw();
    if (window.ResizeObserver) new ResizeObserver(draw).observe(host);
  }

  /* ==================================================================
     「乘法公式怎么来的」交互图
     双计数论证：C(n, j-1) × (n-j+1) 其实是「先选 j-1 个，再补 1 个」的方案数，
     但每个 j 元集合会被数 j 次（最后补的那个可以是其中任意一个），所以要 ÷ j。
     ================================================================== */

  function initFormulaFigure() {
    var host = document.querySelector('[data-formula-figure]');
    if (!host) return;
    var nNumsEl = host.querySelector('[data-ff-n]');
    var jNumsEl = host.querySelector('[data-ff-j]');
    var chipsEl = host.querySelector('[data-ff-chips]');
    var waysEl = host.querySelector('[data-ff-ways]');
    var calcEl = host.querySelector('[data-ff-calc]');
    var detailEl = host.querySelector('[data-ff-detail]');

    var n = 6, j = 3, picked = [];

    function comb(a, b) {
      if (b < 0 || b > a) return 0;
      var v = 1;
      for (var i = 0; i < b; i++) v = v * (a - i) / (i + 1);
      return Math.round(v);
    }

    function numBtn(val, on, onClick) {
      var b = el('button', 'ff-num' + (on ? ' is-on' : ''), String(val));
      b.type = 'button';
      b.addEventListener('click', onClick);
      return b;
    }

    function renderNums() {
      clear(nNumsEl);
      for (var v = 4; v <= 8; v++) {
        (function (val) {
          nNumsEl.appendChild(numBtn(val, val === n, function () {
            n = val; picked = []; render();
          }));
        })(v);
      }
      clear(jNumsEl);
      for (var k = 2; k <= Math.min(4, n); k++) {
        (function (val) {
          jNumsEl.appendChild(numBtn(val, val === j, function () {
            j = val; picked = []; render();
          }));
        })(k);
      }
    }

    function render() {
      renderNums();

      // n 个元素，点选 j 个
      clear(chipsEl);
      for (var i = 0; i < n; i++) {
        (function (idx) {
          var on = picked.indexOf(idx) >= 0;
          var chip = el('button', 'ff-chip' + (on ? ' is-on' : ''), String(idx + 1));
          chip.type = 'button';
          chip.addEventListener('click', function () {
            var at = picked.indexOf(idx);
            if (at >= 0) picked.splice(at, 1); else picked.push(idx);
            render();
          });
          chipsEl.appendChild(chip);
        })(i);
      }

      clear(waysEl);
      clear(calcEl);

      if (picked.length !== j) {
        detailEl.innerHTML = '在上面 <b>' + n + '</b> 个元素里点选 <b>' + j + '</b> 个' +
          '（已选 ' + picked.length + ' 个），看看这个集合会被重复数几次。';
        return;
      }

      // j 种产生方式：最后补上的那个可以是其中任意一个
      var waysTitle = el('div', 'ff-ways-title');
      waysTitle.innerHTML = '这个集合 { ' +
        picked.map(function (x) { return x + 1; }).join(', ') +
        ' } 被数了 <b>' + j + '</b> 次：';
      waysEl.appendChild(waysTitle);
      picked.forEach(function (last, idx) {
        var others = picked.filter(function (x) { return x !== last; });
        var row = el('div', 'ff-way');
        row.appendChild(el('span', 'ff-way-no', String(idx + 1)));
        row.appendChild(el('span', 'ff-way-txt',
          '先选 { ' + others.map(function (x) { return x + 1; }).join(', ') +
          ' }，再补 ' + (last + 1)));
        waysEl.appendChild(row);
      });

      // 计数式
      var c1 = comb(n, j - 1);
      var rem = n - (j - 1);
      var prod = c1 * rem;
      var res = comb(n, j);

      function calcRow(k, v, cls) {
        var row = el('div', 'ff-calc-row' + (cls ? ' ' + cls : ''));
        row.appendChild(el('span', 'ff-calc-k', k));
        row.appendChild(el('span', 'ff-calc-v', v));
        return row;
      }
      calcEl.appendChild(calcRow('先选 j-1 个', 'C(' + n + ', ' + (j - 1) + ') = ' + c1 + ' 种'));
      calcEl.appendChild(calcRow('再补 1 个', '还剩 n-(j-1) = ' + rem + ' 个可选'));
      calcEl.appendChild(calcRow('方案总数', c1 + ' × ' + rem + ' = ' + prod + ' 种', 'is-total'));
      calcEl.appendChild(calcRow('每个集合被数了 j 次', prod + ' ÷ ' + j + ' = ' + res, 'is-fix'));
      calcEl.appendChild(calcRow('正好是 C(' + n + ', ' + j + ')',
        'C(' + n + ', ' + j + ') = ' + res + ' ✓', 'is-check'));

      detailEl.innerHTML = '左边数出的是「有顺序的选法」，右边要的是「选出的集合」—— ' +
        '同一个集合被数了 <b>' + j + '</b> 次，所以要除以 j。';
    }

    render();
    if (window.ResizeObserver) new ResizeObserver(render).observe(host);
  }

  /* ==================================================================
     代码标签页
     ================================================================== */

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

  /* ==================================================================
     启动
     ================================================================== */

  function boot() {
    initTabs();
    initFilter();
    initPathFigure();
    initRowFigure();
    initFormulaFigure();
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
      interval: 850,
      laneOpts: { type: data.type }
    });

    // 代码面板
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

    // 横向对比
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
          type: data.type,
          frames: function (lane) { return lane.compareFrames || lane.frames; },
          tokens: function (lane) { return lane.compareTokens; },
          rows: function (lane) { return lane.compareRows; }
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
