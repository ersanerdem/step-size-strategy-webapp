from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView

from strategies.seo import SITEMAPS, robots_txt
from strategies.views import set_language

# Addresses that are the same in every language.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),  # language switch
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    # Browsers ask for /favicon.ico on their own; send them to the real file.
    path("favicon.ico", RedirectView.as_view(url=static("site/img/favicon.ico"), permanent=True), name="favicon"),
]

# Pages: English at the root (old addresses unchanged), Turkish under /tr/.
urlpatterns += i18n_patterns(
    path("", include("strategies.urls")),
    prefix_default_language=False,
)
