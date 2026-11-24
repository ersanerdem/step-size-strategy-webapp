"""Catalogue of the solver pages.

Every problem exists under two URLs: ``...cl`` (opens on the charts tab) and ``...clf``
(opens on the table tab). Both serve the same solver page; the old addresses of the
2018 site therefore keep working.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _

METHOD_TITLES = {
    "picard": _("Step Size Strategy Based on Picard Theorem"),
    "error": _("Step Size Strategy Based on Error Analysis"),
    "pi": _("Step Size Strategy Based on Picard Theorem and Error Analysis"),
}
METHOD_SHORT = {
    "picard": _("Picard theorem"),
    "error": _("Error analysis"),
    "pi": _("Picard theorem + error analysis"),
}
METHOD_SUMMARY = {
    "picard": _("For x' = f(t, x). The step is chosen so that the next point stays inside the rectangle where Picard's theorem guarantees a unique solution."),
    "error": _("For x' = f(t, x). The step is chosen so that the local error of every Euler step stays below the tolerance δ."),
    "pi": _("For x' = f(t, x) when existence is not known in advance. Combines the Picard bound with an error estimate that shrinks the search rectangle."),
}
THEORY_URL = {"picard": "picard", "error": "hatanalizi", "pi": "pihata", "linear": "sisalgo1", "nonlinear": "nonsisalgo1"}

LINEAR_TITLE = _("Step Size Strategy for Systems of Linear Differential Equations")
NONLINEAR_TITLE = _("Step Size Strategy for Systems of Non-Linear Differential Equations")
LINEAR_SUMMARY = _("For X' = AX. The step keeps the local error of every Euler step below δ; the local error is measured with the matrix exponential.")
NONLINEAR_SUMMARY = _("For X' = AX + φ(t, X). The step keeps the local error of every Euler step below δ, using bounds for X, φ and dφ/dt.")


@dataclass(frozen=True)
class Problem:
    slug: str  # URL name and path (kept identical to the original site)
    mode: str  # "sim" -> opens on charts, "calc" -> opens on the table
    family: str  # "scalar" | "linear" | "nonlinear"
    method: str  # scalar: "picard" | "error" | "pi";  systems: "-"
    n: int  # system dimension (1 for scalar equations)

    @property
    def is_calc(self) -> bool:
        return self.mode == "calc"

    @property
    def key(self) -> str:
        """Identifies the problem independent of the mode (used for presets)."""
        return self.method if self.family == "scalar" else f"{self.family}{self.n}"

    @property
    def sim_slug(self) -> str:
        return self.slug.replace("clf", "cl")

    @property
    def calc_slug(self) -> str:
        return self.sim_slug.replace("cl", "clf", 1)

    @property
    def title(self):
        if self.family == "scalar":
            return METHOD_TITLES[self.method]
        return LINEAR_TITLE if self.family == "linear" else NONLINEAR_TITLE

    @property
    def size_label(self) -> str:
        return "" if self.family == "scalar" else f"{self.n}×{self.n}"

    @property
    def short_title(self):
        if self.family == "scalar":
            return METHOD_SHORT[self.method]
        return self.size_label

    @property
    def summary(self):
        if self.family == "scalar":
            return METHOD_SUMMARY[self.method]
        return LINEAR_SUMMARY if self.family == "linear" else NONLINEAR_SUMMARY

    @property
    def theory_url_name(self) -> str:
        return THEORY_URL[self.method if self.family == "scalar" else self.family]

    @property
    def columns(self) -> list[tuple[str, str, str]]:
        """``(row key, plain header, LaTeX header)`` for the output table / Excel file."""
        base = [("ite", "i", "i"), ("hi", "h_i", "h_{i}"), ("ti", "t_i", "t_{i}")]
        if self.family == "scalar":
            return base + [("xi", "x_i", "x_{i}")]
        cols = base + [("Xti", "||X(t_i)||", r"\|X(t_{i})\|")]
        if self.family == "linear":
            cols.append(("LEi", "||LE_i||", r"\|LE_{i}\|"))
        for j in range(1, self.n + 1):
            cols.append((f"x{j}ti", f"x{j}(t_i)", rf"x_{{{j}}}(t_{{i}})"))
        return cols


def _build() -> list[Problem]:
    problems: list[Problem] = []
    for mode, suffix in (("sim", "cl"), ("calc", "clf")):
        for method, stem in (("picard", "picard"), ("error", "hatanalizi"), ("pi", "pihata")):
            problems.append(Problem(f"{stem}{suffix}", mode, "scalar", method, 1))
        for index, n in enumerate((2, 3, 4), start=1):
            problems.append(Problem(f"sisalgo{suffix}{index}", mode, "linear", "-", n))
            problems.append(Problem(f"nonsisalgo{suffix}{index}", mode, "nonlinear", "-", n))
    return problems


PROBLEMS: list[Problem] = _build()
PROBLEMS_BY_SLUG: dict[str, Problem] = {p.slug: p for p in PROBLEMS}


@dataclass(frozen=True)
class Strategy:
    """One step size strategy: its theory page, its solver pages and the key facts."""

    key: str  # "picard" | "error" | "pi" | "linear" | "nonlinear"
    theory: str  # URL name of the theory page
    problem_text: str  # plain text, for menus
    problem_latex: str
    formula_latex: str  # the step size formula, exactly as in the papers
    source: str

    @property
    def is_scalar(self) -> bool:
        return self.key in METHOD_TITLES

    @property
    def title(self):
        if self.is_scalar:
            return METHOD_TITLES[self.key]
        return LINEAR_TITLE if self.key == "linear" else NONLINEAR_TITLE

    @property
    def short_title(self):
        if self.is_scalar:
            return METHOD_SHORT[self.key]
        return _("Linear systems") if self.key == "linear" else _("Non-linear systems")

    @property
    def group_label(self):
        if self.is_scalar:
            return _("Single equation")
        return _("Linear system") if self.key == "linear" else _("Non-linear system")

    @property
    def summary(self):
        if self.is_scalar:
            return METHOD_SUMMARY[self.key]
        return LINEAR_SUMMARY if self.key == "linear" else NONLINEAR_SUMMARY

    @property
    def rule(self):
        return STEP_RULE[self.key]

    @property
    def requirement(self):
        return REQUIREMENT[self.key]

    @property
    def solvers(self) -> list[Problem]:
        """Chart pages of this strategy (one for a single equation, 2×2–4×4 for systems)."""
        if self.is_scalar:
            return [p for p in PROBLEMS if not p.is_calc and p.family == "scalar" and p.method == self.key]
        return [p for p in PROBLEMS if not p.is_calc and p.family == self.key]


STEP_RULE = {
    "picard": _("The next point stays in the rectangle of Picard's theorem."),
    "error": _("The local error of every step stays below δ_L."),
    "pi": _("Picard's rectangle, shrunk with an error estimate in every step."),
    "linear": _("The local error of every step stays below δ_L."),
    "nonlinear": _("The local error of every step stays below δ_L."),
}
REQUIREMENT = {
    "picard": _("Existence and uniqueness of the solution are known."),
    "error": _("Existence and uniqueness of the solution are known."),
    "pi": _("Existence of the solution need not be known."),
    "linear": _("Constant coefficient matrix A."),
    "nonlinear": _("φ is continuously differentiable."),
}

STRATEGIES: list[Strategy] = [
    Strategy("picard", "picard", "x′ = f(t, x)", "x'=f(t,x)",
             r"h_{i}=\min\left\{a,\frac{b}{M_{i}}\right\}", "Çelik Kızılkan 2004"),
    Strategy("error", "hatanalizi", "x′ = f(t, x)", "x'=f(t,x)",
             r"h_{i}=\sqrt{\dfrac{2\delta_{L}}{M_{t_{i}}}}", "Çelik Kızılkan 2004; Çelik Kızılkan and Aydın 2005"),
    Strategy("pi", "pihata", "x′ = f(t, x)", "x'=f(t,x)",
             r"h_{i}=\min\left\{a,\frac{b_{0i-1}}{M_{i}}\right\}", "Çelik Kızılkan 2004; Çelik Kızılkan and Aydın 2011"),
    Strategy("linear", "sisalgo1", "X′ = AX", "X'=AX",
             r"h_{i}=\dfrac{1}{\alpha\sqrt[4]{N^{5}}}\left(\dfrac{2\delta_{L}}{\beta_{i-1}}\right)^{\frac{1}{2}}",
             "Çelik Kızılkan 2009; Çelik Kızılkan and Aydın 2011"),
    Strategy("nonlinear", "nonsisalgo1", "X′ = AX + φ(t, X)", r"X'=AX+\varphi(t,X)",
             r"h_{i}=N^{-0.25}\left(\frac{2\delta_{L}}{N^{2}\alpha^{2}\beta_{i-1}+N\alpha\gamma_{i-1}+\zeta_{i-1}}\right)^{\frac{1}{2}}",
             "Çelik Kızılkan 2009; Çelik Kızılkan and Aydın 2011"),
]
STRATEGIES_BY_KEY: dict[str, Strategy] = {s.key: s for s in STRATEGIES}
STRATEGY_BY_THEORY: dict[str, Strategy] = {s.theory: s for s in STRATEGIES}


def strategy_for(problem: Problem) -> Strategy:
    return STRATEGIES_BY_KEY[problem.method if problem.family == "scalar" else problem.family]


def sidebar_menu() -> list[dict]:
    """Groups of the side menu: every strategy with its theory and solver pages."""
    groups = []
    for s in STRATEGIES:
        items = [{"url_name": s.theory, "label": _("Theory"), "icon": "journal-text"}]
        for p in s.solvers:
            label = _("Solver") if s.is_scalar else f"{_('Solver')} {p.size_label}"
            items.append({"url_name": p.slug, "label": label, "icon": "calculator"})
        groups.append({"title": s.short_title, "subtitle": s.problem_text, "links": items})
    groups.append({
        "title": _("Project"), "subtitle": "",
        "links": [
            {"url_name": "index", "label": _("Home"), "icon": "house"},
            {"url_name": "about", "label": _("About"), "icon": "people"},
        ],
    })
    return groups
