"""Numerical core of the step-size strategies (no Django, no plotting, no file I/O).

All functions are pure: they take numbers / callables and return a result object.
That makes them testable and safe to call from concurrent requests (the old views
wrote intermediate files that every visitor shared).

Behaviour is kept identical to the original views, with these deliberate fixes:

* ``legacy=False`` (default)
    - the bound ``M`` is the maximum over the *whole* rectangle
      ``|t - t_i| <= a, |x - x_i| <= b`` (a 50x50 grid). The old code paired two
      ``linspace`` arrays element by element, i.e. only looked at one diagonal.
    - the local error of linear systems uses the matrix exponential
      ``scipy.linalg.expm(h*A)``. The old code used ``numpy.exp(A*h)`` which is the
      element-wise exponential and is wrong for non-diagonal ``A``.
    - the total derivative of phi for non-linear systems is
      ``phi_t + J_x(phi) (A X + phi)``; the old code paired the terms in the wrong order.
* ``legacy=True`` reproduces the original numbers exactly.
* The loop stops cleanly when ``h < h*`` and when the interval is exhausted. The old
  code crashed with an ``IndexError`` (hidden by a bare ``except``) when ``h == h*``.
* Every run is limited to ``max_steps`` steps.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np
import sympy as sp
from scipy.linalg import expm

try:  # translated messages inside Django, plain English elsewhere
    from django.utils.translation import gettext as _
except ImportError:  # pragma: no cover
    def _(message: str) -> str:
        return message

GRID_POINTS = 50
DEFAULT_MAX_STEPS = 5000
_END_TOLERANCE = 1e-12


class ComputationError(ValueError):
    """The computation cannot be carried out for the given input."""


# --------------------------------------------------------------------------- results


@dataclass
class ScalarResult:
    """Result for ``x' = f(t, x)``."""

    rows: list[dict] = field(default_factory=list)  # one dict per step (table rows)
    t: list[float] = field(default_factory=list)  # t_0 ... t_n   (n+1 values)
    x: list[float] = field(default_factory=list)  # x_0 ... x_n   (n+1 values)
    h: list[float] = field(default_factory=list)  # h_0 ... h_{n-1}
    stopped_by_hp: bool = False


@dataclass
class SystemResult:
    """Result for systems ``X' = A X (+ phi(t, X))``."""

    n: int
    rows: list[dict] = field(default_factory=list)
    t: list[float] = field(default_factory=list)  # n_steps + 1 values
    h: list[float] = field(default_factory=list)  # n_steps values
    norm: list[float] = field(default_factory=list)  # ||X(t_i)||, n_steps + 1 values
    comps: list[list[float]] = field(default_factory=list)  # comps[j][i], n_steps + 1 values
    local_error: list[float] = field(default_factory=list)  # linear systems only
    stopped_by_hp: bool = False


# --------------------------------------------------------------------------- helpers


def _check_inputs(a: float, b: float, hp: float, delta: float | None = None) -> None:
    if not a > 0:
        raise ComputationError(_("a must be greater than 0."))
    if not b > 0:
        raise ComputationError(_("b must be greater than 0."))
    if hp < 0:
        raise ComputationError(_("h* must not be negative."))
    if delta is not None and not delta > 0:
        raise ComputationError(_("The error tolerance must be greater than 0."))


def _choose_step(h: float, covered: float, a: float, hp: float) -> float | None:
    """Return the step to take, or ``None`` when the integration must stop."""
    remaining = a - covered
    if remaining <= _END_TOLERANCE * max(1.0, abs(a)):
        return None  # reached t0 + a
    if not (h > 0 and h >= hp):
        return None  # step size fell below the prescribed minimum h*
    return min(h, remaining)


def _finished(covered: float, a: float) -> bool:
    return covered >= a - _END_TOLERANCE * max(1.0, abs(a))


def rect_max_abs(
    fn: Callable,
    t_center: float,
    x_center: float,
    a: float,
    b: float,
    *,
    legacy: bool = False,
) -> float:
    """max |fn(t, x)| over ``|t - t_c| <= a, |x - x_c| <= b`` (grid approximation)."""
    ts = np.linspace(t_center - a, t_center + a, GRID_POINTS)
    xs = np.linspace(x_center - b, x_center + b, GRID_POINTS)
    if legacy:
        grid_t, grid_x = ts, xs  # original behaviour: pair the points (one diagonal)
    else:
        grid_t, grid_x = np.meshgrid(ts, xs)
    with np.errstate(all="ignore"):
        values = np.abs(np.asarray(fn(grid_t, grid_x), dtype=float))
    values = np.broadcast_to(values, grid_t.shape)
    peak = float(np.max(values))
    if not math.isfinite(peak):
        raise ComputationError(
            _(
                "The function is not finite on the rectangle around the current point "
                "(division by zero, logarithm of a negative number, overflow ...)."
            )
        )
    return peak


def _scalar_value(fn: Callable, *args: float) -> float:
    with np.errstate(all="ignore"):  # numpy floats: 1/0 -> inf instead of ZeroDivisionError
        value = float(np.asarray(fn(*(np.float64(v) for v in args)), dtype=float))
    if not math.isfinite(value):
        raise ComputationError(_("The function value is not finite at a computed point."))
    return value


def _check_finite(values) -> None:
    if not np.all(np.isfinite(values)):
        raise ComputationError(_("The solution became infinite or undefined (the solution blows up)."))


def _too_many(max_steps: int) -> ComputationError:
    return ComputationError(
        _(
            "More than %(n)d steps would be needed. Increase h*, reduce a, "
            "or increase the error tolerance."
        )
        % {"n": max_steps}
    )


# --------------------------------------------------------------------------- scalar equations


def solve_scalar(
    method: str,
    f: Callable,
    df: Callable | None,
    *,
    t0: float,
    x0: float,
    a: float,
    b: float,
    hp: float,
    delta: float | None = None,
    max_steps: int = DEFAULT_MAX_STEPS,
    legacy: bool = False,
) -> ScalarResult:
    """Explicit Euler with a variable step.

    ``method``:
        ``"picard"``  h = min(a, b/M),               M = max|f|
        ``"error"``   h = sqrt(2*delta/M),           M = max|f_t + f_x f|
        ``"pi"``      Picard + error analysis: the radius b_i shrinks with the
                      second derivative bound, h = min(a, b_i/M_i).

    ``df`` is the total derivative ``f_t + f_x f`` (needed for ``error`` and ``pi``).
    """
    if method not in ("picard", "error", "pi"):
        raise ValueError(f"unknown method {method!r}")
    if method in ("error", "pi") and df is None:
        raise ValueError("df is required for this method")
    _check_inputs(a, b, hp, delta if method == "error" else None)

    res = ScalarResult()
    t, x, covered = t0, x0, 0.0
    res.t.append(t)
    res.x.append(x)
    radius = b  # b_i, only changes for method == "pi"
    prev_h = 0.0
    prev_radius = b

    i = 0
    while True:
        if i >= max_steps:
            raise _too_many(max_steps)

        if method == "picard":
            m = rect_max_abs(f, t, x, a, b, legacy=legacy)
            h = a if m == 0 else min(a, b / m)
        elif method == "error":
            m = rect_max_abs(df, t, x, a, b, legacy=legacy)
            h = math.inf if m == 0 else math.sqrt(2.0 * delta / m)
        else:  # "pi"
            if i == 0:
                radius = b
            else:
                tm = rect_max_abs(df, t, res.x[i - 1], a, prev_radius, legacy=legacy)
                radius = min(prev_radius, 0.5 * tm * prev_h**2)
            m = rect_max_abs(f, t, x, a, radius, legacy=legacy)
            h = a if m == 0 else min(a, radius / m)

        if method == "pi" and i == 0:
            step = h if h > 0 else None  # the original always performs the first step
        else:
            step = _choose_step(h, covered, a, hp)
        if step is None:
            res.stopped_by_hp = not _finished(covered, a)
            break

        slope = _scalar_value(f, t, x)
        res.rows.append({"ite": i, "hi": step, "ti": t, "xi": x})
        res.h.append(step)
        x = x + step * slope
        t = t + step
        covered += step
        _check_finite([x, t])
        res.t.append(t)
        res.x.append(x)
        prev_h, prev_radius = step, radius
        i += 1

    return res


# --------------------------------------------------------------------------- systems (shared)


def _as_column(values: Sequence[float]) -> np.ndarray:
    return np.asarray(values, dtype=float).reshape(-1, 1)


def _push_state(res: SystemResult, time: float, vec: np.ndarray) -> None:
    res.t.append(time)
    res.norm.append(float(np.linalg.norm(vec)))
    for j in range(res.n):
        res.comps[j].append(float(vec[j, 0]))


# --------------------------------------------------------------------------- linear systems


def solve_linear_system(
    A: Sequence[Sequence[float]],
    x0: Sequence[float],
    *,
    t0: float,
    a: float,
    b: float,
    hp: float,
    delta: float,
    max_steps: int = DEFAULT_MAX_STEPS,
    legacy: bool = False,
) -> SystemResult:
    """Euler for ``X' = A X`` with  h = sqrt(2*delta/beta) / (alpha * N**1.25).

    ``alpha = max|a_ij|``, ``beta = max(b + |X_k|)``. The local error of every step is
    ``|| exp(h A) X_k - X_{k+1} ||`` (``expm`` unless ``legacy``).
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if A.shape != (n, n) or len(x0) != n:
        raise ComputationError(_("Matrix and initial vector sizes do not match."))
    _check_inputs(a, b, hp, delta)

    alpha = float(np.max(np.abs(A)))
    y = _as_column(x0)
    res = SystemResult(n=n, comps=[[] for _ in range(n)])
    t, covered = t0, 0.0

    _push_state(res, t, y)
    k = 0
    while True:
        if k >= max_steps:
            raise _too_many(max_steps)
        beta = float(np.max(b + np.abs(y)))
        h = math.inf if alpha == 0 else math.sqrt(2.0 * delta / beta) / (alpha * n**1.25)
        step = _choose_step(h, covered, a, hp)
        if step is None:
            res.stopped_by_hp = not _finished(covered, a)
            break

        y_next = y + step * (A @ y)
        exact = (np.exp(A * step) if legacy else expm(A * step)) @ y
        local_error = float(np.linalg.norm(exact - y_next))
        _check_finite(y_next)

        row = {"ite": k, "hi": step, "ti": t, "Xti": res.norm[-1], "LEi": local_error}
        for j in range(n):
            row[f"x{j + 1}ti"] = float(y[j, 0])
        res.rows.append(row)
        res.h.append(step)
        res.local_error.append(local_error)

        y = y_next
        t += step
        covered += step
        _push_state(res, t, y)
        k += 1
    return res


# --------------------------------------------------------------------------- non-linear systems

STATE_SYMBOL_NAMES = ("x", "y", "z", "w")  # names usable in phi(t, x, y, z, w)
TIME_SYMBOL = sp.Symbol("t")
STATE_SYMBOLS = tuple(sp.Symbol(name) for name in STATE_SYMBOL_NAMES)


def symbol_table(n: int) -> dict[str, sp.Symbol]:
    """Names allowed inside phi_j for an ``n``-dimensional system (``n=1``: t, x)."""
    table = {"t": TIME_SYMBOL}
    table.update({name: STATE_SYMBOLS[j] for j, name in enumerate(STATE_SYMBOL_NAMES[:n])})
    return table


@dataclass
class NonlinearModel:
    n: int
    phi: Callable  # (t, x1..xn) -> array (n,)
    dphi: Callable  # total time derivative of phi along solutions of X' = A X + phi


def build_nonlinear_model(
    A: Sequence[Sequence[float]],
    phi_exprs: Sequence[sp.Expr],
    *,
    legacy: bool = False,
) -> NonlinearModel:
    """Compile phi and its total time derivative along solutions of ``X' = A X + phi``.

    Correct formula:  d(phi)/dt = phi_t + J_x(phi) * (A X + phi).

    The original code multiplied the Jacobian columns ``(t, x1..xn)`` by the vector
    ``(x1', .., xn', 1)`` - i.e. in the wrong order (phi_t was paired with x1', phi_x1
    with x2', ...). ``legacy=True`` reproduces that ordering.
    """
    n = len(phi_exprs)
    xs = STATE_SYMBOLS[:n]
    phi = sp.Matrix(list(phi_exprs))
    a_matrix = sp.Matrix([[sp.Float(v) for v in row] for row in A])
    state = sp.Matrix(list(xs))
    rhs = a_matrix * state + phi
    if legacy:
        jac_full = phi.jacobian([TIME_SYMBOL, *xs])  # n x (n+1), columns t, x1..xn
        total = jac_full * sp.Matrix([*rhs, sp.Integer(1)])
    else:
        total = phi.diff(TIME_SYMBOL) + phi.jacobian(list(xs)) * rhs

    args = (TIME_SYMBOL, *xs)
    phi_fn = sp.lambdify(args, phi, modules="numpy")
    dphi_fn = sp.lambdify(args, total, modules="numpy")

    def _wrap(fn: Callable) -> Callable:
        def call(*values: float) -> np.ndarray:
            with np.errstate(all="ignore"):  # numpy floats: 1/0 -> inf instead of ZeroDivisionError
                return np.asarray(fn(*(np.float64(v) for v in values)), dtype=float).reshape(-1)

        return call

    return NonlinearModel(n=n, phi=_wrap(phi_fn), dphi=_wrap(dphi_fn))


def solve_nonlinear_system(
    A: Sequence[Sequence[float]],
    x0: Sequence[float],
    model: NonlinearModel,
    *,
    t0: float,
    a: float,
    b: float,
    hp: float,
    delta: float,
    max_steps: int = DEFAULT_MAX_STEPS,
) -> SystemResult:
    """Euler for ``X' = A X + phi(t, X)``.

    h = sqrt(2*delta / (N^2 beta alpha^2 + N alpha gamma + eta)) / N^0.25
    with beta = max(b + |X_k|), gamma = max|phi(t0+a, beta, ..)|, eta = max|dphi/dt(t0+a, beta, ..)|.
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if n != model.n or A.shape != (n, n) or len(x0) != n:
        raise ComputationError(_("Matrix, vector and phi sizes do not match."))
    _check_inputs(a, b, hp, delta)

    alpha = float(np.max(np.abs(A)))
    y = _as_column(x0)
    res = SystemResult(n=n, comps=[[] for _ in range(n)])
    t, covered = t0, 0.0
    t_end = t0 + a

    _push_state(res, t, y)
    k = 0
    while True:
        if k >= max_steps:
            raise _too_many(max_steps)
        beta = float(np.max(b + np.abs(y)))
        probe = (t_end, *([beta] * n))
        gamma = float(np.max(np.abs(model.phi(*probe))))
        eta = float(np.max(np.abs(model.dphi(*probe))))
        if not (math.isfinite(gamma) and math.isfinite(eta)):
            raise ComputationError(_("phi (or its derivative) is not finite at the bounding point."))
        denominator = n**2 * beta * alpha**2 + n * alpha * gamma + eta
        h = math.inf if denominator == 0 else math.sqrt(2.0 * delta / denominator) / n**0.25
        step = _choose_step(h, covered, a, hp)
        if step is None:
            res.stopped_by_hp = not _finished(covered, a)
            break

        forcing = model.phi(t, *y[:, 0])
        if forcing.shape != (n,) or not np.all(np.isfinite(forcing)):
            raise ComputationError(_("phi is not finite at a computed point."))
        y_next = y + step * (A @ y) + step * forcing.reshape(-1, 1)
        _check_finite(y_next)

        row = {"ite": k, "hi": step, "ti": t, "Xti": res.norm[-1]}
        for j in range(n):
            row[f"x{j + 1}ti"] = float(y[j, 0])
        res.rows.append(row)
        res.h.append(step)

        y = y_next
        t += step
        covered += step
        _push_state(res, t, y)
        k += 1
    return res
