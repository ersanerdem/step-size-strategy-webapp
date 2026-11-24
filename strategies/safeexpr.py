"""Safe parser for user-supplied mathematical expressions.

The original code called ``sympify(request.POST[...])``. ``sympify`` uses ``eval``
internally, which lets any visitor run arbitrary Python on the server.

This module never evaluates user text as Python:

1. A tokenizer only lets through numbers, whitelisted names and ``+ - * / ^ ** ( )``.
   A comma is read as a decimal point (``0,007`` == ``0.007``), because every
   supported function takes exactly one argument.
2. The cleaned text is parsed with :mod:`ast` (parsing only, no execution) and the
   syntax tree is walked by hand; only whitelisted node types are understood.
3. Every constant sub-expression is folded with ordinary Python floats *before* sympy
   sees it. Inputs such as ``9**9**9**9`` therefore fail fast with an overflow error
   instead of hanging sympy's arbitrary-precision arithmetic.
"""

from __future__ import annotations

import ast
import math
import re

import sympy as sp

try:  # translated messages inside Django, plain English elsewhere
    from django.utils.translation import gettext as _
except ImportError:  # pragma: no cover
    def _(message: str) -> str:
        return message

MAX_LENGTH = 200
_EXACT_INTEGER_LIMIT = 1e15

_TOKEN = re.compile(
    r"""\s*(?:
        (?P<number>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)
      | (?P<name>[A-Za-z][A-Za-z0-9]*)
      | (?P<op>\*\*|[-+*/^()])
    )""",
    re.VERBOSE,
)


def _cot(v: float) -> float:
    return 1.0 / math.tan(v)


def _sec(v: float) -> float:
    return 1.0 / math.cos(v)


def _csc(v: float) -> float:
    return 1.0 / math.sin(v)


# name -> (sympy function, python float function)
FUNCTIONS = {
    "sin": (sp.sin, math.sin),
    "cos": (sp.cos, math.cos),
    "tan": (sp.tan, math.tan),
    "cot": (sp.cot, _cot),
    "sec": (sp.sec, _sec),
    "csc": (sp.csc, _csc),
    "asin": (sp.asin, math.asin),
    "acos": (sp.acos, math.acos),
    "atan": (sp.atan, math.atan),
    "sinh": (sp.sinh, math.sinh),
    "cosh": (sp.cosh, math.cosh),
    "tanh": (sp.tanh, math.tanh),
    "exp": (sp.exp, math.exp),
    "log": (sp.log, math.log),
    "ln": (sp.log, math.log),
    "sqrt": (sp.sqrt, math.sqrt),
    "abs": (sp.Abs, abs),
    "Abs": (sp.Abs, abs),
}
CONSTANTS = {"pi": math.pi, "E": math.e}


class ExpressionError(ValueError):
    """The expression is invalid or not allowed."""


def _tokenize(text: str, allowed_names: set[str]) -> str:
    text = (text or "").strip().replace(",", ".")  # Turkish decimal comma: 0,007 -> 0.007
    if not text:
        raise ExpressionError(_("The expression cannot be empty."))
    if len(text) > MAX_LENGTH:
        raise ExpressionError(_("The expression may have at most %(n)d characters.") % {"n": MAX_LENGTH})

    pieces: list[str] = []
    pos = 0
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None:
            bad = text[pos:].strip()[:1] or text[pos:pos + 1]
            raise ExpressionError(_("Character not allowed in expression: %(char)s") % {"char": repr(bad)})
        pos = match.end()
        if match.group("name") is not None:
            name = match.group("name")
            if name not in allowed_names:
                raise ExpressionError(_("Unknown name: %(name)s") % {"name": repr(name)})
            pieces.append(name)
        elif match.group("op") == "^":
            pieces.append("**")
        else:
            pieces.append(match.group(0).strip())
    return " ".join(pieces)


class _Builder:
    """Walks the syntax tree and builds a sympy expression with float constant folding."""

    def __init__(self, variables: dict[str, sp.Symbol]):
        self.variables = variables

    # Each visit returns (sympy_expression, float_value_or_None).
    # float_value is not None  <=>  the sub-expression is a pure constant.
    def visit(self, node: ast.AST) -> tuple[sp.Expr, float | None]:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ExpressionError(_("Only numbers are allowed."))
            try:
                value = float(node.value)
            except OverflowError as exc:
                raise ExpressionError(_("Number too large.")) from exc
            return self._const(value)
        if isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id], None
            if node.id in CONSTANTS:
                return self._const(CONSTANTS[node.id])
            raise ExpressionError(_("Unknown name: %(name)s") % {"name": repr(node.id)})
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            expr, value = self.visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return expr, value
            return self._const(-value) if value is not None else (-expr, None)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            return self._binop(node)
        if isinstance(node, ast.Call):
            return self._call(node)
        raise ExpressionError(_("Unsupported syntax in expression."))

    @staticmethod
    def _const(value: float) -> tuple[sp.Expr, float]:
        if isinstance(value, complex) or not math.isfinite(value):
            raise ExpressionError(_("The expression produces a non-finite or complex constant."))
        if value == int(value) and abs(value) <= _EXACT_INTEGER_LIMIT:
            return sp.Integer(int(value)), value  # 2*x is shown as 2x, not 2.0x
        return sp.Float(value), value

    def _binop(self, node: ast.BinOp) -> tuple[sp.Expr, float | None]:
        le, lv = self.visit(node.left)
        re_, rv = self.visit(node.right)
        op = node.op

        if isinstance(op, ast.Div) and rv == 0:
            raise ExpressionError(_("Division by zero."))

        if lv is not None and rv is not None:  # both constant -> fold with plain floats
            try:
                if isinstance(op, ast.Add):
                    result = lv + rv
                elif isinstance(op, ast.Sub):
                    result = lv - rv
                elif isinstance(op, ast.Mult):
                    result = lv * rv
                elif isinstance(op, ast.Div):
                    result = lv / rv
                else:
                    result = lv ** rv
            except (OverflowError, ZeroDivisionError) as exc:
                raise ExpressionError(_("Constant value out of range.")) from exc
            return self._const(result)

        if isinstance(op, ast.Add):
            return le + re_, None
        if isinstance(op, ast.Sub):
            return le - re_, None
        if isinstance(op, ast.Mult):
            return le * re_, None
        if isinstance(op, ast.Div):
            return le / re_, None
        # Power with at least one symbolic operand. Integer-valued constant
        # exponents become exact sympy integers (x**2 instead of x**2.0).
        if rv is not None and rv == int(rv) and abs(rv) <= 1000:
            return le ** sp.Integer(int(rv)), None
        return le ** re_, None

    def _call(self, node: ast.Call) -> tuple[sp.Expr, float | None]:
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise ExpressionError(_("Unknown function."))
        if node.keywords or len(node.args) != 1:
            raise ExpressionError(_("%(name)s() takes exactly one argument.") % {"name": node.func.id})
        sym_fn, py_fn = FUNCTIONS[node.func.id]
        expr, value = self.visit(node.args[0])
        if value is not None:
            try:
                return self._const(py_fn(value))
            except (ValueError, OverflowError, ZeroDivisionError) as exc:
                raise ExpressionError(
                    _("%(name)s(%(value)s) is not defined.") % {"name": node.func.id, "value": f"{value:g}"}
                ) from exc
        return sym_fn(expr), None


def _parse(text: str, variables: dict[str, sp.Symbol]) -> tuple[sp.Expr, float | None]:
    names = set(variables) | set(FUNCTIONS) | set(CONSTANTS)
    clash = set(variables) & (set(FUNCTIONS) | set(CONSTANTS))
    if clash:
        raise ExpressionError(_("Variable names clash with reserved names: %(names)s") % {"names": sorted(clash)})
    cleaned = _tokenize(text, names)
    try:
        tree = ast.parse(cleaned, mode="eval")
    except (SyntaxError, ValueError, MemoryError, RecursionError) as exc:
        raise ExpressionError(_("Invalid expression (use * for multiplication, e.g. 2*x).")) from exc
    try:
        return _Builder(variables).visit(tree)
    except RecursionError as exc:
        raise ExpressionError(_("Expression is nested too deeply.")) from exc


def parse_function(text: str, variables: dict[str, sp.Symbol]) -> sp.Expr:
    """Parse ``text`` into a sympy expression whose free symbols are limited to ``variables``."""
    expr, _value = _parse(text, variables)
    return expr


def parse_number(text: str) -> float:
    """Number or constant expression (``0.5``, ``0,5``, ``1e-3``, ``pi/2``) -> ``float``."""
    text = (text or "").strip().replace(",", ".")  # Turkish decimal comma: 0,007 -> 0.007
    try:
        value = float(text)
    except ValueError:
        _expr, value = _parse(text, {})
        if value is None:  # cannot happen without variables, kept as a guard
            raise ExpressionError(_("Enter a real number."))
    if not math.isfinite(value):
        raise ExpressionError(_("The number must be finite."))
    return value
