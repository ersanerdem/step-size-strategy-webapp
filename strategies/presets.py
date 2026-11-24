"""Ready-made examples for every solver page (engineering and textbook problems).

Values are strings exactly as a user would type them. ``tests.PresetTests`` runs every
preset through the real solver, so a preset that stops working is caught by
``python manage.py test``.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from .catalog import Problem


def _system(matrix: list[list[str]], x0: list[str], phi: list[str] | None = None, **params: str) -> dict:
    """``params`` holds t0, a, b, hp, d (the interval length ``a`` is a keyword here)."""
    values = dict(params)
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            values[f"a{i + 1}{j + 1}"] = matrix[i][j]
        values[f"x{i + 1}1"] = x0[i]
    for i, expr in enumerate(phi or []):
        values[f"fi{i}"] = expr
    return values


SCALAR = [
    {
        "id": "paper",
        "title": _("Linear test problem  x' = t + x"),
        "description": _("The example used in the original papers. Exact solution: x(t) = 2eᵗ − t − 1."),
        "values": {"f": "t+x", "t0": "0", "x0": "1", "a": "1", "b": "1", "hp": "0.00001", "d": "0.001"},
    },
    {
        "id": "logistic",
        "title": _("Logistic population growth"),
        "description": _("x' = x(1 − x): growth that saturates at the carrying capacity 1."),
        "values": {"f": "x*(1-x)", "t0": "0", "x0": "0.1", "a": "8", "b": "1", "hp": "0.00001", "d": "0.001"},
    },
    {
        "id": "cooling",
        "title": _("Newton's law of cooling"),
        "description": _("A 90 °C object in a 20 °C room: x' = −0.3 (x − 20)."),
        "values": {"f": "-0.3*(x-20)", "t0": "0", "x0": "90", "a": "15", "b": "10", "hp": "0.00001", "d": "0.01"},
    },
    {
        "id": "decay",
        "title": _("Radioactive decay"),
        "description": _("x' = −0.5 x with 100 units at t = 0."),
        "values": {"f": "-0.5*x", "t0": "0", "x0": "100", "a": "10", "b": "10", "hp": "0.00001", "d": "0.01"},
    },
    {
        "id": "riccati",
        "title": _("Riccati equation"),
        "description": _("x' = t² + x², a classic non-linear test problem without an elementary solution."),
        "values": {"f": "t**2+x**2", "t0": "0", "x0": "0", "a": "1", "b": "1", "hp": "0.00001", "d": "0.001"},
    },
    {
        "id": "rc",
        "title": _("RC circuit with sinusoidal source"),
        "description": _("Capacitor voltage: x' = cos(t) − x (RC = 1 s)."),
        "values": {"f": "cos(t)-x", "t0": "0", "x0": "0", "a": "10", "b": "1", "hp": "0.00001", "d": "0.001"},
    },
]

LINEAR = {
    2: [
        {
            "id": "oscillator",
            "title": _("Harmonic oscillator"),
            "description": _("x'' + x = 0 written as a first-order system (position, velocity)."),
            "values": _system([["0", "1"], ["-1", "0"]], ["1", "0"], t0="0", a="6.28", b="1", hp="0.000001", d="0.001"),
        },
        {
            "id": "spring",
            "title": _("Mass–spring–damper"),
            "description": _("m = 1 kg, c = 0.5 N·s/m, k = 4 N/m:  x'' + 0.5 x' + 4x = 0."),
            "values": _system([["0", "1"], ["-4", "-0.5"]], ["1", "0"], t0="0", a="10", b="1", hp="0.000001", d="0.005"),
        },
        {
            "id": "rlc",
            "title": _("Series RLC circuit"),
            "description": _("L = 0.5 H, R = 1 Ω, C = 0.2 F. State: charge q and current i."),
            "values": _system([["0", "1"], ["-10", "-2"]], ["1", "0"], t0="0", a="5", b="1", hp="0.000001", d="0.01"),
        },
    ],
    3: [
        {
            "id": "chain",
            "title": _("Radioactive decay chain A → B → C"),
            "description": _("k₁ = 1, k₂ = 0.5. Starts with only A."),
            "values": _system(
                [["-1", "0", "0"], ["1", "-0.5", "0"], ["0", "0.5", "0"]], ["1", "0", "0"],
                t0="0", a="10", b="1", hp="0.000001", d="0.001",
            ),
        },
        {
            "id": "third",
            "title": _("Third-order equation"),
            "description": _("x''' + 3x'' + 3x' + x = 0 (critically damped), state (x, x', x'')."),
            "values": _system(
                [["0", "1", "0"], ["0", "0", "1"], ["-1", "-3", "-3"]], ["1", "0", "0"],
                t0="0", a="5", b="1", hp="0.000001", d="0.005",
            ),
        },
    ],
    4: [
        {
            "id": "twomass",
            "title": _("Two coupled masses"),
            "description": _("Two equal masses between three springs. State (x₁, x₂, v₁, v₂)."),
            "values": _system(
                [["0", "0", "1", "0"], ["0", "0", "0", "1"], ["-2", "1", "0", "0"], ["1", "-2", "0", "0"]],
                ["1", "0", "0", "0"], t0="0", a="10", b="1", hp="0.000001", d="0.005",
            ),
        },
    ],
}

NONLINEAR = {
    2: [
        {
            "id": "pendulum",
            "title": _("Damped pendulum"),
            "description": _("θ'' + 0.2θ' + sin θ = 0, starting at θ = 1 rad. Here x = θ, y = θ'."),
            "values": _system([["0", "1"], ["0", "-0.2"]], ["1", "0"], ["0", "-sin(x)"], t0="0", a="10", b="1", hp="0.000001", d="0.001"),
        },
        {
            "id": "lotka",
            "title": _("Lotka–Volterra predator–prey"),
            "description": _("x: prey, y: predator.  x' = x − 0.5xy,  y' = −0.5y + 0.25xy."),
            "values": _system([["1", "0"], ["0", "-0.5"]], ["2", "1"], ["-0.5*x*y", "0.25*x*y"], t0="0", a="5", b="1", hp="0.000001", d="0.01"),
        },
        {
            "id": "vanderpol",
            "title": _("Van der Pol oscillator"),
            "description": _("x'' − (1 − x²)x' + x = 0 (μ = 1), a self-sustained oscillation from electronics."),
            "values": _system([["0", "1"], ["-1", "1"]], ["1", "0"], ["0", "-x**2*y"], t0="0", a="3", b="1", hp="0.000001", d="0.01"),
        },
    ],
    3: [
        {
            "id": "sir",
            "title": _("SIR epidemic model"),
            "description": _("Fractions of susceptible (x), infected (y) and recovered (z); β = 0.5, γ = 0.1 per day."),
            "values": _system(
                [["0", "0", "0"], ["0", "-0.1", "0"], ["0", "0.1", "0"]], ["0.99", "0.01", "0"],
                ["-0.5*x*y", "0.5*x*y", "0"], t0="0", a="40", b="1", hp="0.000001", d="0.01",
            ),
        },
    ],
    4: [
        {
            "id": "seir",
            "title": _("SEIR epidemic model"),
            "description": _("Susceptible x, exposed y, infected z, recovered w; β = 0.5, σ = 0.2, γ = 0.1 per day."),
            "values": _system(
                [["0", "0", "0", "0"], ["0", "-0.2", "0", "0"], ["0", "0.2", "-0.1", "0"], ["0", "0", "0.1", "0"]],
                ["0.99", "0", "0.01", "0"], ["-0.5*x*z", "0.5*x*z", "0", "0"],
                t0="0", a="40", b="1", hp="0.000001", d="0.01",
            ),
        },
    ],
}


def presets_for(problem: Problem) -> list[dict]:
    if problem.family == "scalar":
        return SCALAR
    table = LINEAR if problem.family == "linear" else NONLINEAR
    return table.get(problem.n, [])


def presets_json(problem: Problem) -> list[dict]:
    """JSON-ready presets (lazy translations evaluated in the current language)."""
    return [
        {"id": p["id"], "title": str(p["title"]), "description": str(p["description"]), "values": p["values"]}
        for p in presets_for(problem)
    ]
