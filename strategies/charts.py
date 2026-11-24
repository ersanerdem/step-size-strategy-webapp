"""Chart data for Plotly (drawn in the browser).

The 2018 site drew PNG files with matplotlib on the server. Sending the numbers and
letting Plotly draw them in the browser gives zoomable, hoverable charts and saves
server CPU time (PythonAnywhere free accounts get 100 CPU seconds per day).
"""

from __future__ import annotations

from django.utils.translation import gettext as _

from .numerics import ScalarResult, SystemResult


def _line(x, y, name: str, *, mode: str = "lines+markers") -> dict:
    return {"type": "scatter", "mode": mode, "x": list(x), "y": list(y), "name": name}


def _chart(chart_id: str, title: str, traces: list[dict], xtitle: str, ytitle: str, *, log_y: bool = False) -> dict:
    return {
        "id": chart_id,
        "title": title,
        "traces": traces,
        "xaxis": {"title": xtitle},
        "yaxis": {"title": ytitle, "type": "log" if log_y else "linear"},
    }


def scalar_charts(result: ScalarResult) -> list[dict]:
    steps = list(range(len(result.h)))
    return [
        _chart("solution", _("Numerical solution"), [_line(result.t, result.x, "xᵢ")], "t", "x(t)"),
        _chart("stepsize", _("Step size"), [_line(steps, result.h, "hᵢ", mode="markers")], "i", "hᵢ"),
    ]


def system_charts(result: SystemResult, *, with_local_error: bool) -> list[dict]:
    steps = list(range(len(result.h)))
    components = [_line(result.t, result.comps[j], f"x{j + 1}", mode="lines") for j in range(result.n)]
    charts = [
        _chart("components", _("Components of the solution"), components, "t", "xⱼ(t)"),
        _chart("norm", _("Norm of the numerical solution"), [_line(result.t, result.norm, "‖X‖", mode="lines")], "t", "‖X(t)‖"),
        _chart("stepsize", _("Step size"), [_line(steps, result.h, "hᵢ", mode="markers")], "i", "hᵢ"),
    ]
    if with_local_error and result.local_error:
        positive = all(v > 0 for v in result.local_error)
        charts.append(
            _chart(
                "localerror", _("Local error"),
                [_line(steps, result.local_error, "‖LEᵢ‖", mode="markers")], "i", "‖LEᵢ‖", log_y=positive,
            )
        )
    charts.append(
        _chart("phase", _("Phase plane"), [_line(result.comps[0], result.comps[1], "(x1, x2)", mode="lines")], "x1", "x2")
    )
    if result.n >= 3:
        charts.append(
            {
                "id": "trajectory",
                "title": _("Trajectory in 3D"),
                "traces": [
                    {
                        "type": "scatter3d", "mode": "lines", "name": "(x1, x2, x3)",
                        "x": result.comps[0], "y": result.comps[1], "z": result.comps[2],
                    }
                ],
                "scene": {"xaxis": {"title": "x1"}, "yaxis": {"title": "x2"}, "zaxis": {"title": "x3"}},
            }
        )
    return charts
