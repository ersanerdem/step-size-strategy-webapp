"""Views. One class-based view serves every solver page."""

from __future__ import annotations

import logging
from urllib.parse import urlsplit

import sympy as sp
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.views import View
from django.views.i18n import set_language as django_set_language
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET

from . import services
from .catalog import PROBLEMS_BY_SLUG, STRATEGIES, STRATEGIES_BY_KEY, Problem, strategy_for
from .exports import rows_to_xlsx
from .forms import ProblemForm, RegisterForm
from .numerics import ComputationError
from .presets import presets_for, presets_json
from .safeexpr import ExpressionError, parse_function

logger = logging.getLogger(__name__)

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _wants_json(request) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _form_errors(form) -> dict:
    return {
        "ok": False,
        "errors": {name: [str(e) for e in errors] for name, errors in form.errors.items() if name != "__all__"},
        "non_field_errors": [str(e) for e in form.non_field_errors()],
    }


class ProblemView(View):
    """GET shows the form; POST validates and computes.

    * ``X-Requested-With: XMLHttpRequest`` (sent by the page script) -> JSON result.
    * ``action=download`` -> Excel file (logged-in users).
    * a plain POST (no JavaScript) -> the page with the result embedded.

    Nothing is written to disk and no state is shared between requests.
    """

    problem: Problem | None = None
    template_name = "site/solver.html"

    def get(self, request, *args, **kwargs):
        return self._render(request, ProblemForm(problem=self.problem))

    def post(self, request, *args, **kwargs):
        form = ProblemForm(request.POST, problem=self.problem)
        wants_json = _wants_json(request)
        if not form.is_valid():
            if wants_json:
                return JsonResponse(_form_errors(form))
            return self._render(request, form)

        try:
            result, payload = services.run(
                self.problem,
                form.cleaned_data,
                legacy=getattr(settings, "STEPSIZE_LEGACY_NUMERICS", False),
                max_steps=getattr(settings, "STEPSIZE_MAX_STEPS", 5000),
            )
        except ComputationError as exc:
            form.add_error(None, str(exc))
        except Exception:  # unexpected: log it, show a friendly message instead of a 500 page
            logger.exception("Unexpected error in %s", self.problem.slug)
            form.add_error(None, _("The computation failed for these inputs. Please check them and try again."))
        else:
            if request.POST.get("action") == "download":
                if not request.user.is_authenticated:
                    return redirect_to_login(request.get_full_path())
                response = HttpResponse(rows_to_xlsx(result.rows, self.problem.columns), content_type=XLSX_CONTENT_TYPE)
                response["Content-Disposition"] = f'attachment; filename="{self.problem.sim_slug}.xlsx"'
                return response
            if wants_json:
                return JsonResponse(payload)
            return self._render(request, form, payload)

        if wants_json:
            return JsonResponse(_form_errors(form))
        return self._render(request, form)

    def _render(self, request, form, result: dict | None = None):
        problem = self.problem
        config = {
            "slug": problem.slug,
            "previewUrl": reverse("preview"),
            "expressions": form.expression_fields(),
            "presets": presets_json(problem),
            "defaultTab": "table" if problem.is_calc else "charts",
            "result": result,
            "canExport": request.user.is_authenticated,
            "initialPreset": None,
        }
        example = request.GET.get("example", "")
        if result is None and example in {p["id"] for p in config["presets"]}:
            config["initialPreset"] = example  # opened from an example card: load and solve it
        text = {
            "pageInfo": _("Page {page} of {pages} · {rows} steps"),
            "network": _("Connection problem. Please check your internet connection and try again."),
            "server": _("The server could not complete the request. Please try again."),
        }
        size = f" ({problem.size_label})" if problem.size_label else ""
        context = {
            "strategy": strategy_for(problem),
            "meta_title": f"{problem.title}{size} – {_('Online Euler method solver')}",
            "meta_description": f"{problem.summary} {_('Free and online, with interactive charts and ready-made examples.')}",
            "problem": problem,
            "form": form,
            "layout": form.layout(),
            "solver_config": config,
            "solver_text": text,
        }
        return render(request, self.template_name, context)


def example_cards(strategy, limit: int = 4) -> list[dict]:
    """Ready-made examples of a strategy, taken in turn from each of its solver pages."""
    queues = [[(p, preset) for preset in presets_for(p)] for p in strategy.solvers]
    cards = []
    while len(cards) < limit and any(queues):
        for queue in queues:
            if queue and len(cards) < limit:
                problem, preset = queue.pop(0)
                cards.append({
                    "title": preset["title"],
                    "description": preset["description"],
                    "size": problem.size_label,
                    "url": f"{reverse(problem.slug)}?example={preset['id']}",
                })
    return cards


class TheoryView(TemplateView):
    """A theory page: the strategy's text plus key facts and example cards."""

    strategy_key = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        strategy = STRATEGIES_BY_KEY[self.strategy_key]
        context.update(strategy=strategy, examples=example_cards(strategy))
        return context


class HomeView(TemplateView):
    template_name = "site/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["strategies"] = STRATEGIES
        return context


def set_language(request):
    """Django's language switch, reading ``next`` in the language of its own address.

    With ``prefix_default_language=False`` the switch itself (/i18n/setlang/, no prefix) always runs in
    English, so Django could not recognise a Turkish address such as /tr/picard/ and sent the visitor
    back to it unchanged. Activating the language of ``next`` first lets it be translated.
    """
    next_url = request.POST.get("next", request.GET.get("next")) or ""
    current = translation.get_language_from_path(urlsplit(next_url).path) or settings.LANGUAGE_CODE
    with translation.override(current):
        return django_set_language(request)


@require_GET
def preview_view(request):
    """Live LaTeX preview of an expression field: ``?problem=<slug>&field=<name>&expr=...``."""
    problem = PROBLEMS_BY_SLUG.get(request.GET.get("problem", ""))
    if problem is None:
        return JsonResponse({"ok": False, "error": _("Unknown problem.")}, status=404)
    field = ProblemForm(problem=problem).fields.get(request.GET.get("field", ""))
    if field is None or not getattr(field, "is_expression", False):
        return JsonResponse({"ok": False, "error": _("Unknown field.")}, status=404)
    text = request.GET.get("expr", "")
    if not text.strip():
        return JsonResponse({"ok": True, "latex": ""})
    try:
        expr = parse_function(text, field.variables)
    except ExpressionError as exc:
        return JsonResponse({"ok": False, "error": str(exc)})
    return JsonResponse({"ok": True, "latex": sp.latex(expr)})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "site/register.html", {"form": form})
