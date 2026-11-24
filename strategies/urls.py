"""Language-specific pages. The project URLconf mounts them with ``i18n_patterns``:
English at the root (``/picardcl/`` — the addresses of the original site keep working),
Turkish under ``/tr/`` (``/tr/picardcl/``)."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import RedirectView, TemplateView

from . import views
from .catalog import PROBLEMS

# Information pages (URL names are unchanged from the original site).
THEORY = [("picard", "picard"), ("hatanalizi", "error"), ("pihata", "pi"), ("sisalgo1", "linear"), ("nonsisalgo1", "nonlinear")]

urlpatterns = [
    path("", views.HomeView.as_view(), name="index"),
    path("about/", TemplateView.as_view(template_name="site/about.html"), name="about"),
]
urlpatterns += [
    path(f"{name}/", views.TheoryView.as_view(template_name=f"site/theory/{name}.html", strategy_key=key), name=name)
    for name, key in THEORY
]

urlpatterns += [
    path("strategiess/", RedirectView.as_view(pattern_name="index", permanent=False), name="strategiess"),
    path(
        "login/",
        LoginView.as_view(template_name="site/login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),  # POST only (Django >= 5.0)
    path("register/", views.register_view, name="register_view"),
    path("api/preview/", views.preview_view, name="preview"),
]

# Every solver page, under its charts (...cl*) and table (...clf*) address.
urlpatterns += [
    path(f"{problem.slug}/", views.ProblemView.as_view(problem=problem), name=problem.slug)
    for problem in PROBLEMS
]
