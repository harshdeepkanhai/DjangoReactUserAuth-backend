"""
Local development settings.

Activated with ``DJANGO_SETTINGS_MODULE=config.settings.local`` (the default in
``manage.py``). Defaults here are deliberately convenient, not secure — never
use this module to serve real traffic.
"""

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK, env

# A throwaway key so the project runs without a .env during quick local hacking.
# Production reads DJANGO_SECRET_KEY from the environment (see base.py).
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-local-development-key-do-not-use-in-prod",
)

DEBUG = env("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"])

# Allow the React dev server by default; override via CORS_ALLOWED_ORIGINS.
CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)

# Enable the browsable API and session auth for easy manual exploration in dev.
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
)
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
