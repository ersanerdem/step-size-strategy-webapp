"""Glue between validated form data, the numerical core and the JSON sent to the page."""

from __future__ import annotations

import time

import sympy as sp
from django.utils.translation import gettext as _

from . import charts, numerics
from .catalog import Problem
from .numerics import ScalarResult, SystemResult

_T = numerics.TIME_SYMBOL
_X = numerics.STATE_SYMBOLS[0]


def solve(problem: Problem, data: dict, *, legacy: bool, max_steps: int) -> ScalarResult | SystemResult:
    """Run the algorithm selected by ``problem`` with already validated ``data``."""
    if problem.family == "scalar":
        expr = data["f"]
        f = sp.lambdify((_T, _X), expr, modules="numpy")
        df = None
        if problem.method in ("error", "pi"):
            total = sp.diff(expr, _X) * expr + sp.diff(expr, _T)  # f_x * f + f_t
            df = sp.lambdify((_T, _X), total, modules="numpy")
        return numerics.solve_scalar(
            problem.method, f, df,
            t0=data["t0"], x0=data["x0"], a=data["a"], b=data["b"], hp=data["hp"],
            delta=data.get("d"), max_steps=max_steps, legacy=legacy,
        )

    n = problem.n
    matrix = [[data[f"a{i}{j}"] for j in range(1, n + 1)] for i in range(1, n + 1)]
    start = [data[f"x{i}1"] for i in range(1, n + 1)]
    common = dict(t0=data["t0"], a=data["a"], b=data["b"], hp=data["hp"], delta=data["d"], max_steps=max_steps)

    if problem.family == "linear":
        return numerics.solve_linear_system(matrix, start, legacy=legacy, **common)

    phi = [data[f"fi{i}"] for i in range(n)]
    model = numerics.build_nonlinear_model(matrix, phi, legacy=legacy)
    return numerics.solve_nonlinear_system(matrix, start, model, **common)


def _fmt(value: float) -> str:
    return format(value, ".6g")


def summary(problem: Problem, result, data: dict, elapsed: float) -> list[dict]:
    """Key figures shown above the charts."""
    t_end_target = data["t0"] + data["a"]
    items = [
        {"label": _("Steps"), "value": str(len(result.h))},
        {"label": _("Reached t"), "value": f"{_fmt(result.t[-1])} / {_fmt(t_end_target)}"},
    ]
    if result.h:
        items += [
            {"label": _("Smallest step"), "value": _fmt(min(result.h))},
            {"label": _("Largest step"), "value": _fmt(max(result.h))},
        ]
    if problem.family == "scalar":
        items.append({"label": _("Final value x"), "value": _fmt(result.x[-1])})
    else:
        final = ", ".join(_fmt(c[-1]) for c in result.comps)
        items.append({"label": _("Final value X"), "value": f"({final})"})
        if result.local_error:
            items.append({"label": _("Largest local error"), "value": _fmt(max(result.local_error))})
    items.append({"label": _("Computation time"), "value": f"{elapsed * 1000:.0f} ms"})
    return items


def result_payload(problem: Problem, result, data: dict, elapsed: float) -> dict:
    """Everything the page needs to show a result, as JSON-ready data."""
    keys = [key for key, _plain, _latex in problem.columns]
    if problem.family == "scalar":
        chart_list = charts.scalar_charts(result)
    else:
        chart_list = charts.system_charts(result, with_local_error=problem.family == "linear")
    notice = None
    if result.stopped_by_hp:
        notice = _("The integration stopped because the step size became smaller than h*.")
    elif not result.rows:
        notice = _("No step was taken.")
    return {
        "ok": True,
        "notice": notice,
        "summary": summary(problem, result, data, elapsed),
        "columns": [{"key": key, "latex": latex} for key, _plain, latex in problem.columns],
        "rows": [[row[key] for key in keys] for row in result.rows],
        "charts": chart_list,
    }


def run(problem: Problem, data: dict, *, legacy: bool, max_steps: int) -> tuple[object, dict]:
    """Solve and build the payload; returns ``(result, payload)``."""
    start = time.perf_counter()
    result = solve(problem, data, legacy=legacy, max_steps=max_steps)
    payload = result_payload(problem, result, data, time.perf_counter() - start)
    return result, payload
