"""Search engine helpers: sitemap, robots.txt and per-page SEO data for the templates."""

from __future__ import annotations

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.templatetags.static import static
from django.urls import reverse, translate_url
from django.utils.translation import get_language
from django.views.decorators.http import require_GET

from .catalog import PROBLEMS, PROBLEMS_BY_SLUG

OG_LOCALES = {"en": "en_US", "tr": "tr_TR"}


def site_base(request) -> str:
    """``https://host`` used in absolute links (``SITE_URL`` wins over the request)."""
    configured = getattr(settings, "SITE_URL", "").rstrip("/")
    return configured or f"{request.scheme}://{request.get_host()}"


class PageSitemap(Sitemap):
    """Every public page in English and Turkish, with hreflang alternates."""

    i18n = True
    alternates = True
    x_default = True
    protocol = "https"

    def items(self):
        pages = [("index", 1.0, "monthly")]
        pages += [(p.slug, 0.9, "monthly") for p in PROBLEMS if not p.is_calc]
        pages += [(name, 0.7, "yearly") for name in ("picard", "hatanalizi", "pihata", "sisalgo1", "nonsisalgo1")]
        pages += [("about", 0.5, "yearly")]
        return pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


SITEMAPS = {"pages": PageSitemap}


@require_GET
def robots_txt(request):
    base = site_base(request)
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /tr/api/",
        "Disallow: /i18n/",
        "",
        f"Sitemap: {base}{reverse('sitemap')}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def seo(request):
    """Canonical URL, hreflang alternates, social-card data and verification codes."""
    base = site_base(request)
    path = request.path
    match = getattr(request, "resolver_match", None)
    problem = PROBLEMS_BY_SLUG.get(match.url_name) if match else None
    if problem is not None and problem.is_calc:
        path = reverse(problem.sim_slug)  # the table view is the same page as the chart view

    current = get_language() or settings.LANGUAGE_CODE
    alternates = [
        {"code": code, "href": base + translate_url(path, code)} for code, _name in settings.LANGUAGES
    ]
    default_href = next((a["href"] for a in alternates if a["code"] == settings.LANGUAGE_CODE), base + path)
    return {
        "seo": {
            "base": base,
            "canonical": base + path,
            "alternates": alternates,
            "x_default": default_href,
            "og_image": base + static("site/img/og-image.png"),
            "og_locale": OG_LOCALES.get(current, "en_US"),
            "og_locale_alternates": [v for k, v in OG_LOCALES.items() if k != current],
            "other_language": next((a for a in alternates if a["code"] != current), None),
            "google_verification": getattr(settings, "GOOGLE_SITE_VERIFICATION", ""),
            "bing_verification": getattr(settings, "BING_SITE_VERIFICATION", ""),
            "yandex_verification": getattr(settings, "YANDEX_VERIFICATION", ""),
        }
    }
