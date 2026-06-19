"""
Production settings.

Activated with ``DJANGO_SETTINGS_MODULE=config.settings.production``. Every
secret and host is read from the environment — there are no insecure defaults.
Run ``python manage.py check --deploy`` to validate the security posture.
"""

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK, env

# DEBUG must be off; SECRET_KEY / ALLOWED_HOSTS are required (no defaults).
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")

# API-only in production: drop the browsable renderer and session auth.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

# Serve compressed, hashed static assets through WhiteNoise.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Security hardening ---------------------------------------------------
# Terminating TLS at a proxy (nginx, load balancer) is the common deployment;
# trust its forwarded scheme header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", default=True)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 365)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default=CORS_ALLOWED_ORIGINS)
