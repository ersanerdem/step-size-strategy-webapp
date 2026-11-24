/* Solver page: examples, live formula preview, solving without reload, charts and table. */
(function () {
  "use strict";

  var configEl = document.getElementById("solver-config");
  var form = document.getElementById("solver-form");
  if (!configEl || !form) { return; }

  var config = JSON.parse(configEl.textContent);
  var textEl = document.getElementById("solver-text");
  var text = textEl ? JSON.parse(textEl.textContent) : {};
  var PAGE_SIZE = 50;

  var els = {
    solve: document.getElementById("solve-button"),
    alert: document.getElementById("form-alert"),
    presetSelect: document.getElementById("preset-select"),
    presetDescription: document.getElementById("preset-description"),
    empty: document.getElementById("results-empty"),
    results: document.getElementById("results"),
    notice: document.getElementById("result-notice"),
    summary: document.getElementById("result-summary"),
    charts: document.getElementById("charts"),
    tableHead: document.querySelector("#result-table thead"),
    tableBody: document.querySelector("#result-table tbody"),
    tableInfo: document.getElementById("table-info"),
    prev: document.getElementById("page-prev"),
    next: document.getElementById("page-next"),
    tabCharts: document.getElementById("tab-charts"),
    tabTable: document.getElementById("tab-table")
  };

  var state = { rows: [], columns: [], page: 0, charts: [], tabShown: false };

  /* ------------------------------------------------------------------ helpers */

  function format(text, values) {
    return String(text || "").replace(/\{(\w+)\}/g, function (_m, key) {
      return values[key] !== undefined ? values[key] : "";
    });
  }

  function typeset(elements) {
    var mj = window.MathJax;
    if (!mj || !mj.startup || !mj.startup.promise || !mj.typesetPromise) { return; }
    mj.startup.promise.then(function () {
      if (mj.typesetClear) { mj.typesetClear(elements); }
      return mj.typesetPromise(elements);
    }).catch(function () { /* a typesetting problem must not break the page */ });
  }

  function formatNumber(value, isIndex) {
    if (typeof value !== "number") { return String(value); }
    if (isIndex) { return String(value); }
    if (value === 0) { return "0"; }
    return String(Number(value.toPrecision(8)));
  }

  function field(name) {
    return form.elements.namedItem(name);
  }

  /* ------------------------------------------------------------------ errors */

  function clearErrors() {
    Array.prototype.forEach.call(form.querySelectorAll(".is-invalid"), function (el) { el.classList.remove("is-invalid"); });
    Array.prototype.forEach.call(form.querySelectorAll("[data-error-for]"), function (el) { el.textContent = ""; });
    var group = form.querySelector("[data-error-group]");
    if (group) { group.textContent = ""; }
    els.alert.classList.add("d-none");
    els.alert.textContent = "";
  }

  function showErrors(data) {
    var first = null;
    var groupMessages = [];
    Object.keys(data.errors || {}).forEach(function (name) {
      var input = field(name);
      var message = data.errors[name].join(" ");
      if (input) {
        input.classList.add("is-invalid");
        if (!first) { first = input; }
      }
      var target = form.querySelector('[data-error-for="' + name + '"]');
      if (target) {
        target.textContent = message;
      } else {
        groupMessages.push(name + ": " + message);
      }
    });
    var group = form.querySelector("[data-error-group]");
    if (group) { group.textContent = groupMessages.join("  "); }
    if (data.non_field_errors && data.non_field_errors.length) {
      els.alert.textContent = data.non_field_errors.join(" ");
      els.alert.classList.remove("d-none");
      if (!first) { first = els.alert; }
    }
    if (first && first.focus) {
      first.focus({ preventScroll: true });
      first.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function showFailure(message) {
    els.alert.textContent = message;
    els.alert.classList.remove("d-none");
  }

  /* ------------------------------------------------------------------ charts */

  function chartColors() {
    var dark = document.documentElement.getAttribute("data-bs-theme") === "dark";
    return {
      font: dark ? "#e6edf3" : "#1f2a37",
      grid: dark ? "rgba(255,255,255,0.12)" : "rgba(15,23,42,0.10)",
      zero: dark ? "rgba(255,255,255,0.25)" : "rgba(15,23,42,0.25)"
    };
  }

  function chartLayout(chart) {
    var c = chartColors();
    var axis = function (spec) {
      return {
        title: { text: (spec && spec.title) || "" },
        type: (spec && spec.type) || "linear",
        gridcolor: c.grid, zerolinecolor: c.zero, automargin: true
      };
    };
    var layout = {
      title: { text: chart.title, font: { size: 15 } },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { color: c.font, family: "Inter, system-ui, sans-serif" },
      margin: { l: 60, r: 20, t: 48, b: 48 },
      hovermode: "closest",
      legend: { orientation: "h", y: -0.2 },
      colorway: ["#138a72", "#3b6fd8", "#e07b39", "#a54ec9", "#d64560", "#6b7280"]
    };
    if (chart.scene) {
      layout.scene = {
        xaxis: axis(chart.scene.xaxis), yaxis: axis(chart.scene.yaxis), zaxis: axis(chart.scene.zaxis)
      };
      layout.margin = { l: 0, r: 0, t: 48, b: 0 };
    } else {
      layout.xaxis = axis(chart.xaxis);
      layout.yaxis = axis(chart.yaxis);
    }
    return layout;
  }

  function plotConfig() {
    var remove = ["lasso2d", "select2d"];
    if (!config.canExport) { remove.push("toImage"); }
    return {
      responsive: true,
      displaylogo: false,
      modeBarButtonsToRemove: remove,
      toImageButtonOptions: { format: "png", filename: config.slug, scale: 2 }
    };
  }

  function renderCharts(charts) {
    state.charts = charts || [];
    if (window.Plotly) {
      Array.prototype.forEach.call(els.charts.querySelectorAll(".chart"), function (div) { window.Plotly.purge(div); });
    }
    els.charts.innerHTML = "";
    if (!window.Plotly) {
      els.charts.innerHTML = '<p class="text-body-secondary small">Plotly could not be loaded.</p>';
      return;
    }
    state.charts.forEach(function (chart) {
      var block = document.createElement("div");
      block.className = "chart-block";
      var div = document.createElement("div");
      div.className = "chart";
      div.id = "chart-" + chart.id;
      block.appendChild(div);
      els.charts.appendChild(block);
      window.Plotly.newPlot(div, chart.traces, chartLayout(chart), plotConfig());
    });
  }

  function restyleCharts() {
    if (!window.Plotly) { return; }
    state.charts.forEach(function (chart) {
      var div = document.getElementById("chart-" + chart.id);
      if (div) { window.Plotly.relayout(div, chartLayout(chart)); }
    });
  }

  function resizeCharts() {
    if (!window.Plotly) { return; }
    Array.prototype.forEach.call(els.charts.querySelectorAll(".chart"), function (div) { window.Plotly.Plots.resize(div); });
  }

  /* ------------------------------------------------------------------ table */

  function renderTableHead() {
    var tr = document.createElement("tr");
    state.columns.forEach(function (column) {
      var th = document.createElement("th");
      th.scope = "col";
      th.textContent = "\\(" + column.latex + "\\)";
      tr.appendChild(th);
    });
    els.tableHead.innerHTML = "";
    els.tableHead.appendChild(tr);
    typeset([els.tableHead]);
  }

  function renderTablePage() {
    var pages = Math.max(1, Math.ceil(state.rows.length / PAGE_SIZE));
    state.page = Math.min(Math.max(state.page, 0), pages - 1);
    var start = state.page * PAGE_SIZE;
    var fragment = document.createDocumentFragment();
    state.rows.slice(start, start + PAGE_SIZE).forEach(function (row) {
      var tr = document.createElement("tr");
      row.forEach(function (value, index) {
        var td = document.createElement("td");
        td.textContent = formatNumber(value, index === 0);
        tr.appendChild(td);
      });
      fragment.appendChild(tr);
    });
    els.tableBody.innerHTML = "";
    els.tableBody.appendChild(fragment);
    els.tableInfo.textContent = format(text.pageInfo, { page: state.page + 1, pages: pages, rows: state.rows.length });
    els.prev.disabled = state.page === 0;
    els.next.disabled = state.page >= pages - 1;
  }

  /* ------------------------------------------------------------------ result */

  function renderSummary(items) {
    els.summary.innerHTML = "";
    (items || []).forEach(function (item) {
      var box = document.createElement("div");
      box.className = "summary-item";
      var label = document.createElement("div");
      label.className = "label";
      label.textContent = item.label;
      var value = document.createElement("div");
      value.className = "value";
      value.textContent = item.value;
      box.appendChild(label);
      box.appendChild(value);
      els.summary.appendChild(box);
    });
  }

  function showTab(name) {
    var trigger = name === "table" ? els.tabTable : els.tabCharts;
    if (trigger && window.bootstrap && window.bootstrap.Tab) {
      window.bootstrap.Tab.getOrCreateInstance(trigger).show();
    }
  }

  function renderResult(result) {
    els.empty.classList.add("d-none");
    els.empty.classList.remove("d-flex");
    els.results.classList.remove("d-none");

    if (result.notice) {
      els.notice.textContent = result.notice;
      els.notice.classList.remove("d-none");
    } else {
      els.notice.classList.add("d-none");
    }
    renderSummary(result.summary);

    state.columns = result.columns || [];
    state.rows = result.rows || [];
    state.page = 0;
    renderTableHead();
    renderTablePage();

    if (!state.tabShown) {
      showTab(config.defaultTab);
      state.tabShown = true;
    }
    renderCharts(result.charts);
  }

  /* ------------------------------------------------------------------ solving */

  function setBusy(busy) {
    if (!els.solve) { return; }
    els.solve.disabled = busy;
    var spinner = els.solve.querySelector(".spinner-border");
    var icon = els.solve.querySelector(".bi");
    if (spinner) { spinner.classList.toggle("d-none", !busy); }
    if (icon) { icon.classList.toggle("d-none", busy); }
  }

  function solve() {
    clearErrors();
    setBusy(true);
    var data = new FormData(form);
    data.set("action", "run");
    fetch(window.location.pathname, {
      method: "POST",
      body: data,
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    }).then(function (response) {
      if (!response.ok) { throw new Error("status " + response.status); }
      return response.json();
    }).then(function (payload) {
      if (payload.ok) {
        renderResult(payload);
        if (window.matchMedia("(max-width: 1199.98px)").matches) {
          els.results.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      } else {
        showErrors(payload);
      }
    }).catch(function (error) {
      showFailure(error && error.message && error.message.indexOf("status") === 0 ? text.server : text.network);
    }).then(function () {
      setBusy(false);
    });
  }

  form.addEventListener("submit", function (event) {
    var submitter = event.submitter;
    if (submitter && submitter.value === "download") { return; } /* normal POST -> file download */
    if (!window.fetch || !window.FormData) { return; }
    event.preventDefault();
    solve();
  });

  /* ------------------------------------------------------------------ live preview */

  var previewTimers = {};
  var previewSerial = {};

  function updatePreview(name) {
    var input = field(name);
    var box = form.querySelector('[data-preview-for="' + name + '"]');
    if (!input || !box) { return; }
    var value = input.value.trim();
    var serial = (previewSerial[name] || 0) + 1;
    previewSerial[name] = serial;
    if (!value) {
      box.textContent = "";
      box.classList.remove("is-error");
      return;
    }
    var url = config.previewUrl + "?problem=" + encodeURIComponent(config.slug) +
      "&field=" + encodeURIComponent(name) + "&expr=" + encodeURIComponent(value);
    fetch(url, { credentials: "same-origin" }).then(function (response) {
      return response.json();
    }).then(function (data) {
      if (previewSerial[name] !== serial) { return; } /* an older answer arrived late */
      if (data.ok) {
        box.classList.remove("is-error");
        box.textContent = data.latex ? "\\(" + (config.expressions[name] || "") + " " + data.latex + "\\)" : "";
        typeset([box]);
      } else {
        box.classList.add("is-error");
        box.textContent = data.error || "";
      }
    }).catch(function () { /* the preview is optional */ });
  }

  Object.keys(config.expressions || {}).forEach(function (name) {
    var input = field(name);
    if (!input) { return; }
    input.addEventListener("input", function () {
      window.clearTimeout(previewTimers[name]);
      previewTimers[name] = window.setTimeout(function () { updatePreview(name); }, 350);
    });
    if (input.value.trim()) { updatePreview(name); }
  });

  /* ------------------------------------------------------------------ examples */

  if (els.presetSelect) {
    els.presetSelect.addEventListener("change", function () {
      var preset = (config.presets || []).filter(function (p) { return p.id === els.presetSelect.value; })[0];
      if (!preset) {
        els.presetDescription.textContent = "";
        return;
      }
      els.presetDescription.textContent = preset.description;
      Object.keys(preset.values).forEach(function (name) {
        var input = field(name);
        if (input) { input.value = preset.values[name]; }
      });
      Object.keys(config.expressions || {}).forEach(updatePreview);
      solve();
    });
  }

  /* ------------------------------------------------------------------ misc */

  if (els.prev) { els.prev.addEventListener("click", function () { state.page -= 1; renderTablePage(); }); }
  if (els.next) { els.next.addEventListener("click", function () { state.page += 1; renderTablePage(); }); }
  if (els.tabCharts) { els.tabCharts.addEventListener("shown.bs.tab", resizeCharts); }
  document.addEventListener("themechange", restyleCharts);

  if (config.result) {
    renderResult(config.result);
  } else if (config.initialPreset && els.presetSelect) {
    /* Opened from an example card (?example=...): load that example and solve it. */
    els.presetSelect.value = config.initialPreset;
    els.presetSelect.dispatchEvent(new Event("change"));
  }
})();
