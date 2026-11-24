"""Django settings for stepsizestrategies (Django 6.1, Python >= 3.12).

Configuration comes from environment variables:

    DJANGO_SECRET_KEY         required in production (any long random string)
    DJANGO_DEBUG              "1" / "0"  (default: "1" when no secret key is set, else "0")
    DJANGO_ALLOWED_HOSTS      comma separated, e.g. "stepsizestrategies.pythonanywhere.com"
    DJANGO_SECURE_SSL         "1" to force HTTPS and secure cookies (default: on when DEBUG is off)
    STEPSIZE_MAX_STEPS        upper limit of Euler steps per request (default 5000)
    STEPSIZE_LEGACY_NUMERICS  "1" to reproduce the numbers of the original site exactly
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_bool(name: str, default: bool) -> bool:
    return env(name, "1" if default else "0").lower() in {"1", "true", "yes", "on"}


_SECRET_FROM_ENV = env("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", default=not _SECRET_FROM_ENV)

if _SECRET_FROM_ENV:
    SECRET_KEY = _SECRET_FROM_ENV
elif DEBUG:
    SECRET_KEY = "django-insecure-local-development-only-change-me"
else:
    raise ImproperlyConfigured("Set the DJANGO_SECRET_KEY environment variable in production.")

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS").split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1", "[::1]")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "strategies.apps.StrategiesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # TR / EN (browser language or the switch in the menu)
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stepsizestrategies.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "strategies.context_processors.navigation",
                "strategies.seo.seo",
            ],
        },
    },
]

WSGI_APPLICATION = "stepsizestrategies.wsgi.application"
ASGI_APPLICATION = "stepsizestrategies.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "login"

LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("tr", "Türkçe")]
LOCALE_PATHS = [BASE_DIR / "strategies" / "locale"]
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # filled by `python manage.py collectstatic`

# Security settings for production (HTTPS).
if env_bool("DJANGO_SECURE_SSL", default=not DEBUG):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Search engines -------------------------------------------------------------------
# Public address used in canonical links, the sitemap and social cards,
# e.g. "https://stepsizestrategies.pythonanywhere.com" (empty: taken from the request).
SITE_URL = env("SITE_URL")
# Verification codes from Google Search Console, Bing Webmaster Tools and Yandex Webmaster
# (only the code inside content="..."). Empty: no tag is added.
GOOGLE_SITE_VERIFICATION = env("GOOGLE_SITE_VERIFICATION")
BING_SITE_VERIFICATION = env("BING_SITE_VERIFICATION")
YANDEX_VERIFICATION = env("YANDEX_VERIFICATION")

# --- Application settings -----------------------------------------------------------
STEPSIZE_MAX_STEPS = int(env("STEPSIZE_MAX_STEPS", "5000"))
# True  -> reproduce the numbers of the original 2018 site exactly
# False -> mathematically corrected versions (see strategies/numerics.py)
STEPSIZE_LEGACY_NUMERICS = env_bool("STEPSIZE_LEGACY_NUMERICS", default=False)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"strategies": {"handlers": ["console"], "level": "INFO"}},
}
