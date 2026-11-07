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
