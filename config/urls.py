"""
Root URL configuration.

API endpoints are versioned under ``/api/v1/``. The OpenAPI schema and an
interactive Swagger UI are exposed for documentation, and a lightweight
``/health/`` endpoint supports container/load-balancer health checks.
"""

from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request):
    """Return 200 only when the database connection is usable."""
    try:
        connection.ensure_connection()
    except Exception:  # pragma: no cover - exercised via DB outage
        return JsonResponse({"status": "error", "database": "down"}, status=503)
    return JsonResponse({"status": "ok", "database": "up"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    # API schema & docs.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("health/", health, name="health"),
]
