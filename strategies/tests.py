"""Tests. Run with:  python manage.py test"""

import json
import math
import re

import numpy as np
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import translation
from scipy.linalg import expm

from . import numerics
from .catalog import PROBLEMS
from .presets import presets_for
from .safeexpr import ExpressionError, parse_function, parse_number

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class SafeExpressionTests(SimpleTestCase):
    def setUp(self):
        self.vars = numerics.symbol_table(1)

    def test_valid_expressions(self):
        for text in ["x*(1-x)", "sin(t)+x^2", "-2*t*x", "exp(-x)/(1+t**2)", "sqrt(x**2+1)", "2*pi*x", "0,5*x"]:
            parse_function(text, self.vars)

    def test_code_injection_is_rejected(self):
        for text in [
            "__import__('os').system('id')",
            "x.__class__",
            "open('/etc/passwd')",
            "eval(1)",
            "lambda: 1",
            "x; import os",
            "9**9**9**9**9",
            "y+1",
        ]:
            with self.assertRaises(ExpressionError, msg=text):
                parse_function(text, self.vars)

    def test_numbers(self):
        self.assertAlmostEqual(parse_number("pi/2"), math.pi / 2)
        self.assertEqual(parse_number("1e-3"), 0.001)
        self.assertEqual(parse_number("0,007"), 0.007)
        for bad in ["", "x", "1/0", "inf", "nan", "1,2,3"]:
            with self.assertRaises(ExpressionError):
                parse_number(bad)

    def test_integer_constants_stay_exact(self):
        expr = parse_function("2*x", self.vars)
        self.assertEqual(str(expr), "2*x")


class NumericsTests(SimpleTestCase):
    def test_euler_reaches_end_of_interval(self):
        f = lambda t, x: x  # x' = x, x(0)=1  ->  x(1)=e
        res = numerics.solve_scalar("picard", f, None, t0=0, x0=1, a=1, b=1, hp=0)
        self.assertAlmostEqual(res.t[-1], 1.0)
        self.assertAlmostEqual(sum(res.h), 1.0)

    def test_error_method_converges(self):
        f = lambda t, x: x
        df = lambda t, x: x  # f_t + f_x * f = x
        res = numerics.solve_scalar("error", f, df, t0=0, x0=1, a=1, b=1, hp=0, delta=1e-6)
        self.assertAlmostEqual(res.x[-1], math.e, places=2)

    def test_hp_stops_integration(self):
        f = lambda t, x: x
        df = lambda t, x: x
        res = numerics.solve_scalar("error", f, df, t0=0, x0=1, a=1, b=1, hp=0.5, delta=1e-6)
        self.assertTrue(res.stopped_by_hp)
        self.assertEqual(res.rows, [])

    def test_step_limit(self):
        f = lambda t, x: x
        df = lambda t, x: x
        with self.assertRaises(numerics.ComputationError):
            numerics.solve_scalar("error", f, df, t0=0, x0=1, a=1, b=1, hp=0, delta=1e-12, max_steps=50)

    def test_linear_local_error_uses_matrix_exponential(self):
        A = [[0.0, 1.0], [-1.0, 0.0]]
        res = numerics.solve_linear_system(A, [1, 0], t0=0, a=1, b=1, hp=0, delta=1e-3)
        h = res.h[0]
        y0 = np.array([[1.0], [0.0]])
        expected = np.linalg.norm(expm(np.array(A) * h) @ y0 - (y0 + h * np.array(A) @ y0))
        self.assertAlmostEqual(res.local_error[0], expected)
        self.assertAlmostEqual(res.t[-1], 1.0)

    def test_nonlinear_total_derivative(self):
        A = [[0.0, 1.0], [-1.0, 0.3]]
        names = numerics.symbol_table(2)
        model = numerics.build_nonlinear_model(
            A, [parse_function("0.1*x**2+t*y", names), parse_function("0.2*y*x+sin(t)", names)]
        )
        t0, X = 0.7, np.array([0.4, -0.3])
        flow = lambda t, Y: np.array(A) @ Y + model.phi(t, *Y)
        h = 1e-6
        numeric = (model.phi(t0 + h, *(X + h * flow(t0, X))) - model.phi(t0 - h, *(X - h * flow(t0, X)))) / (2 * h)
        np.testing.assert_allclose(model.dphi(t0, *X), numeric, rtol=1e-6)


def sample_data(problem):
    if problem.family == "scalar":
        return {"f": "t+x", "t0": "0", "x0": "1", "a": "1", "b": "1", "hp": "0,001", "d": "0.01"}
    data = {"hp": "0.0001", "t0": "0", "a": "1", "b": "1", "d": "0.01"}
    n = problem.n
    for i in range(1, n + 1):
        data[f"x{i}1"] = "1"
        for j in range(1, n + 1):
            data[f"a{i}{j}"] = "-1" if i == j else "0.1"
    if problem.family == "nonlinear":
        for i in range(n):
            data[f"fi{i}"] = "0.1*x*t"
    return data


class PageTests(TestCase):
    def test_information_pages(self):
        for name in ["index", "about", "picard", "hatanalizi", "pihata", "sisalgo1", "nonsisalgo1", "login", "register_view"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_favicon_redirect(self):
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response["Location"].endswith("site/img/favicon.ico"))

    def test_every_solver_page_get_plain_post_and_ajax(self):
        for problem in PROBLEMS:
            url = reverse(problem.slug)
            self.assertEqual(self.client.get(url).status_code, 200, problem.slug)

            response = self.client.post(url, sample_data(problem))  # no JavaScript
            self.assertEqual(response.status_code, 200, problem.slug)
            self.assertFalse(response.context["form"].errors, (problem.slug, response.context["form"].errors))
            self.assertTrue(response.context["solver_config"]["result"]["rows"], problem.slug)

            payload = self.client.post(url, sample_data(problem), **AJAX).json()
            self.assertTrue(payload["ok"], (problem.slug, payload))
            self.assertTrue(payload["rows"] and payload["charts"] and payload["summary"], problem.slug)
            json.dumps(payload, allow_nan=False)  # strict JSON (no NaN / Infinity)

    def test_invalid_input(self):
        url = reverse("picardcl")
        data = {**sample_data(PROBLEMS[0]), "f": "__import__('os')", "a": "-1"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("f", response.context["form"].errors)
        payload = self.client.post(url, data, **AJAX).json()
        self.assertFalse(payload["ok"])
        self.assertIn("f", payload["errors"])
        self.assertIn("a", payload["errors"])

    def test_computation_error_is_reported(self):
        data = {**sample_data(PROBLEMS[0]), "f": "1/(x-1)", "x0": "1"}
        payload = self.client.post(reverse("picardcl"), data, **AJAX).json()
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["non_field_errors"])

    def test_preview(self):
        url = reverse("preview")
        ok = self.client.get(url, {"problem": "picardcl", "field": "f", "expr": "x^2 - 2*x"}).json()
        self.assertTrue(ok["ok"])
        self.assertIn("x^{2}", ok["latex"])
        bad = self.client.get(url, {"problem": "picardcl", "field": "f", "expr": "x +* 2"}).json()
        self.assertFalse(bad["ok"])
        self.assertTrue(bad["error"])
        phi = self.client.get(url, {"problem": "nonsisalgocl2", "field": "fi1", "expr": "x*y*z"}).json()
        self.assertTrue(phi["ok"])
        self.assertEqual(self.client.get(url, {"problem": "nope", "field": "f", "expr": "x"}).status_code, 404)
        self.assertEqual(self.client.get(url, {"problem": "picardcl", "field": "t0", "expr": "1"}).status_code, 404)

    def test_excel_download_requires_login_and_works(self):
        problem = next(p for p in PROBLEMS if p.slug == "picardclf")
        data = {**sample_data(problem), "action": "download"}
        response = self.client.post(reverse(problem.slug), data)
        self.assertEqual(response.status_code, 302)
        get_user_model().objects.create_user("ali", password="S3cure-pass-123")
        self.client.login(username="ali", password="S3cure-pass-123")
        response = self.client.post(reverse(problem.slug), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"PK"))  # .xlsx is a zip file

    def test_register_login_logout(self):
        response = self.client.post(
            reverse("register_view"),
            {
                "username": "ayse",
                "first_name": "Ayşe",
                "last_name": "Yılmaz",
                "email": "ayse@example.com",
                "password1": "Very-Strong-123",
                "password2": "Very-Strong-123",
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.assertContains(self.client.get(reverse("index")), "Ayşe")
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)  # GET logout not allowed
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"), fetch_redirect_response=False)

    def test_register_requires_first_and_last_name(self):
        data = {
            "username": "mehmet",
            "first_name": "",
            "last_name": " ",
            "email": "mehmet@example.com",
            "password1": "Very-Strong-123",
            "password2": "Very-Strong-123",
        }
        response = self.client.post(reverse("register_view"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("first_name", response.context["form"].errors)
        self.assertIn("last_name", response.context["form"].errors)
        self.assertFalse(get_user_model().objects.filter(username="mehmet").exists())

    def test_example_link_preloads_preset(self):
        problem = next(p for p in PROBLEMS if p.slug == "picardcl")
        preset_id = presets_for(problem)[0]["id"]
        url = reverse("picardcl")
        response = self.client.get(url, {"example": preset_id})
        self.assertEqual(response.context["solver_config"]["initialPreset"], preset_id)
        response = self.client.get(url, {"example": "no-such-example"})
        self.assertIsNone(response.context["solver_config"]["initialPreset"])

    def test_theory_pages_link_to_examples(self):
        for name in ["picard", "hatanalizi", "pihata", "sisalgo1", "nonsisalgo1"]:
            response = self.client.get(reverse(name))
            self.assertTrue(response.context["examples"], name)
            self.assertContains(response, "?example=", msg_prefix=name)
            self.assertContains(response, 'class="formula-card is-main', msg_prefix=name)

    def test_sidebar_marks_current_page(self):
        # The table view of a solver highlights its chart view in the menu.
        response = self.client.get(reverse("picardclf"))
        self.assertContains(response, f'href="{reverse("picardcl")}" aria-current="page"')
        self.assertContains(response, 'aria-current="page"', count=2)  # sidebar link + breadcrumb

    def test_about_page_shows_thesis_and_article(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "site/docs/ersan-erdem-thesis-2019.pdf")
        self.assertContains(response, "konuralpjournalmath/article/618922")
        self.assertContains(self.client.get("/tr/about/"), "Adım Genişliği Stratejileri İçin Web Uygulaması")
        for event in ("ICMME-2017", "ICMME-2019", "ICMME-2021"):
            self.assertContains(response, event)

    def test_css_and_js_carry_a_version(self):
        # Browsers must not keep an old site.css after an update.
        self.assertContains(self.client.get(reverse("picard")), "site/css/site.css?v=")
        self.assertContains(self.client.get(reverse("hatanalizicl")), "site/js/solver.js?v=")

    def test_home_lists_all_strategies(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "strategy-card", count=5)
        self.assertContains(response, r"h_{i}=\min\left\{a,\frac{b}{M_{i}}\right\}")

    def test_language_addresses(self):
        # English at the root (old addresses unchanged), Turkish under /tr/.
        self.assertContains(self.client.get("/"), "Start solving")
        self.assertContains(self.client.get("/picardcl/"), "Online Euler method solver")
        self.assertContains(self.client.get("/tr/"), "Çözmeye başla")
        self.assertContains(self.client.get("/tr/picard/"), "Aşağıdaki Cauchy problemini")
        self.assertContains(self.client.get("/tr/picardcl/"), '<html lang="tr"')
        with translation.override("tr"):
            self.assertEqual(reverse("picardcl"), "/tr/picardcl/")
            self.assertEqual(reverse("preview"), "/tr/api/preview/")
        payload = self.client.post("/tr/picardcl/", {**sample_data(PROBLEMS[0]), "a": "0"}, **AJAX).json()
        self.assertIn("0'dan büyük olmalı.", payload["errors"]["a"])
        bad = self.client.get("/tr/api/preview/", {"problem": "picardcl", "field": "f", "expr": "y"}).json()
        self.assertIn("Bilinmeyen ad", bad["error"])

    def test_language_switch_translates_the_address(self):
        response = self.client.post(reverse("set_language"), {"language": "tr", "next": "/hatanalizicl/"})
        self.assertRedirects(response, "/tr/hatanalizicl/", fetch_redirect_response=False)
        response = self.client.post(reverse("set_language"), {"language": "en", "next": "/tr/hatanalizicl/"})
        self.assertRedirects(response, "/hatanalizicl/", fetch_redirect_response=False)


@override_settings(SITE_URL="https://stepsizestrategies.example")
class SeoTests(TestCase):
    def test_head_tags(self):
        html = self.client.get("/hatanalizicl/").content.decode()
        self.assertIn('<link rel="canonical" href="https://stepsizestrategies.example/hatanalizicl/">', html)
        self.assertIn('hreflang="tr" href="https://stepsizestrategies.example/tr/hatanalizicl/"', html)
        self.assertIn('hreflang="x-default" href="https://stepsizestrategies.example/hatanalizicl/"', html)
        self.assertIn('property="og:image" content="https://stepsizestrategies.example/static/site/img/og-image.png"', html)
        self.assertIn("Online Euler method solver", html)
        self.assertNotIn('name="robots"', html)

    def test_table_view_points_to_chart_view(self):
        html = self.client.get("/tr/hatanaliziclf/").content.decode()
        self.assertIn('<link rel="canonical" href="https://stepsizestrategies.example/tr/hatanalizicl/">', html)

    def test_login_and_register_are_noindex(self):
        for url in ("/login/", "/register/", "/tr/login/"):
            self.assertContains(self.client.get(url), '<meta name="robots" content="noindex, follow">')

    def test_structured_data_is_valid_json(self):
        for url, kind in (("/", "WebApplication"), ("/tr/", "WebApplication"), ("/picard/", "TechArticle"), ("/tr/sisalgo1/", "TechArticle")):
            html = self.client.get(url).content.decode()
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
            self.assertEqual(len(blocks), 1, url)
            data = json.loads(blocks[0])
            self.assertEqual(data["@type"], kind, url)
            self.assertTrue(data["url"].startswith("https://stepsizestrategies.example/"), url)

    def test_verification_tags(self):
        with self.settings(GOOGLE_SITE_VERIFICATION="abc123", YANDEX_VERIFICATION="y42"):
            html = self.client.get("/").content.decode()
        self.assertIn('<meta name="google-site-verification" content="abc123">', html)
        self.assertIn('<meta name="yandex-verification" content="y42">', html)
        self.assertNotIn("msvalidate.01", html)

    def test_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        xml = response.content.decode()
        for path in ("/", "/tr/", "/picardcl/", "/tr/nonsisalgocl3/", "/tr/about/"):
            self.assertIn(f"<loc>https://testserver{path}</loc>", xml)
        self.assertNotIn("clf", xml)  # table views are duplicates of the chart views
        self.assertNotIn("/login/", xml)
        self.assertIn('hreflang="tr"', xml)
        self.assertIn('hreflang="x-default"', xml)

    def test_robots(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        text = response.content.decode()
        self.assertIn("Disallow: /admin/", text)
        self.assertIn("Sitemap: https://stepsizestrategies.example/sitemap.xml", text)


class PresetTests(TestCase):
    """Every ready-made example must solve without errors on its page."""

    def test_every_preset_solves(self):
        for problem in [p for p in PROBLEMS if not p.is_calc]:
            presets = presets_for(problem)
            self.assertTrue(presets, problem.slug)
            for preset in presets:
                payload = self.client.post(reverse(problem.slug), preset["values"], **AJAX).json()
                self.assertTrue(payload.get("ok"), (problem.slug, preset["id"], payload))
                if problem.method != "pi":  # the combined strategy may legitimately stop early
                    self.assertIsNone(payload["notice"], (problem.slug, preset["id"], payload["notice"]))
