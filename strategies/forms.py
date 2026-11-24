"""Forms: validation of every numeric input and function expression (no ``eval``)."""

from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from .catalog import Problem
from .numerics import STATE_SYMBOL_NAMES, symbol_table
from .safeexpr import ExpressionError, parse_function, parse_number


def _text_input(maxlength: int, *, inputmode: str = "text", placeholder: str = "") -> forms.TextInput:
    return forms.TextInput(
        attrs={
            "class": "form-control",
            "maxlength": maxlength,
            "autocomplete": "off",
            "spellcheck": "false",
            "inputmode": inputmode,
            "placeholder": placeholder,
        }
    )


def _clean_text(value) -> str:
    return "" if value is None else str(value).strip()


class NumberField(forms.Field):
    """A real number. ``0,5``, ``1e-3`` and constant expressions such as ``pi/2`` are accepted."""

    def __init__(self, *, minimum=None, strictly_positive=False, **kwargs):
        self.minimum = minimum
        self.strictly_positive = strictly_positive
        kwargs.setdefault("widget", _text_input(40, inputmode="decimal"))
        super().__init__(**kwargs)

    def to_python(self, value):
        value = _clean_text(value)
        if value == "":
            return None
        try:
            number = parse_number(value)
        except ExpressionError as exc:
            raise ValidationError(str(exc), code="invalid") from exc
        if self.strictly_positive and not number > 0:
            raise ValidationError(_("Must be greater than 0."), code="min_value")
        if self.minimum is not None and number < self.minimum:
            raise ValidationError(_("Must be at least %(min)s.") % {"min": self.minimum}, code="min_value")
        return number


class ExpressionField(forms.Field):
    """A function of the variables in ``variables``; ``clean`` returns a sympy expression."""

    is_expression = True

    def __init__(self, *, variables: dict, preview_prefix: str = "", **kwargs):
        self.variables = variables
        self.preview_prefix = preview_prefix
        kwargs.setdefault("widget", _text_input(200, placeholder=", ".join(variables)))
        super().__init__(**kwargs)

    def to_python(self, value):
        value = _clean_text(value)
        if value == "":
            return None
        try:
            return parse_function(value, self.variables)
        except ExpressionError as exc:
            raise ValidationError(str(exc), code="invalid") from exc


class ProblemForm(forms.Form):
    """Input form for one solver page. Field names match the original site.

    Labels are LaTeX (rendered by MathJax); ``help_text`` explains each field.
    """

    def __init__(self, *args, problem: Problem, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem = problem
        n = problem.n
        fields = self.fields
        interval = gettext_lazy("Length of the interval [t₀, t₀ + a]; also the half-width of the search rectangle in t.")
        radius = gettext_lazy("Half-width of the search rectangle around the solution.")
        minimum = gettext_lazy("Minimum allowed step size. The integration stops if the step falls below it.")

        if problem.family == "scalar":
            fields["f"] = ExpressionField(
                label="f(t,x)", variables=symbol_table(1), preview_prefix="x' =",
                help_text=gettext_lazy("Right-hand side. Use t, x, + − * / ^ and sin, cos, exp, log, sqrt …"),
            )
            fields["t0"] = NumberField(label="t_{0}", help_text=gettext_lazy("Initial time."))
            fields["x0"] = NumberField(label="x_{0}", help_text=gettext_lazy("Initial value x(t₀)."))
            fields["a"] = NumberField(label="a", strictly_positive=True, help_text=interval)
            fields["b"] = NumberField(label="b", strictly_positive=True, help_text=radius)
            fields["hp"] = NumberField(label="h^{*}", minimum=0, help_text=minimum)
            if problem.method == "error":
                fields["d"] = NumberField(
                    label=r"\delta", strictly_positive=True,
                    help_text=gettext_lazy("Desired local error level of every step."),
                )
            return

        fields["t0"] = NumberField(label="t_{0}", help_text=gettext_lazy("Initial time."))
        fields["a"] = NumberField(label="a", strictly_positive=True, help_text=gettext_lazy("Length of the interval [t₀, t₀ + a]."))
        fields["b"] = NumberField(label="b", strictly_positive=True, help_text=radius)
        fields["hp"] = NumberField(label="h^{*}", minimum=0, help_text=minimum)
        fields["d"] = NumberField(
            label=r"\delta_{L}", strictly_positive=True,
            help_text=gettext_lazy("Desired local error level of every step."),
        )
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                fields[f"a{i}{j}"] = NumberField(label=f"a_{{{i}{j}}}")
        for i in range(1, n + 1):
            fields[f"x{i}1"] = NumberField(label=f"x_{{{i}}}(t_{{0}})")
        if problem.family == "nonlinear":
            variables = symbol_table(n)
            names = ",".join(["t", *STATE_SYMBOL_NAMES[:n]])
            for i in range(n):
                fields[f"fi{i}"] = ExpressionField(
                    label=rf"\varphi_{{{i + 1}}}({names})", variables=variables,
                    preview_prefix=rf"\varphi_{{{i + 1}}} =",
                )

    def layout(self) -> dict:
        """Bound fields grouped the way the template draws them."""
        p = self.problem
        if p.family == "scalar":
            params = [self[k] for k in ("t0", "x0", "a", "b", "hp")]
            if "d" in self.fields:
                params.append(self["d"])
            return {"expressions": [self["f"]], "params": params}
        n = p.n
        layout = {
            "params": [self[k] for k in ("t0", "a", "b", "hp", "d")],
            "A": [[self[f"a{i}{j}"] for j in range(1, n + 1)] for i in range(1, n + 1)],
            "X0": [self[f"x{i}1"] for i in range(1, n + 1)],
            "expressions": [],
        }
        if p.family == "nonlinear":
            layout["expressions"] = [self[f"fi{i}"] for i in range(n)]
            layout["variables"] = ", ".join(STATE_SYMBOL_NAMES[:n])
        return layout

    def expression_fields(self) -> dict[str, str]:
        """Field name -> LaTeX prefix for the live preview."""
        return {name: f.preview_prefix for name, f in self.fields.items() if getattr(f, "is_expression", False)}


class RegisterForm(UserCreationForm):
    """Sign-up form. Passwords are confirmed and checked by ``AUTH_PASSWORD_VALIDATORS``."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name"):
            self.fields[name].required = True  # the site greets users by name
