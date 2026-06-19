import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from .factories import DEFAULT_PASSWORD, UserFactory


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    """Reset the throttle history between tests (rates use the default cache)."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory(username="jane", email="jane@example.com")


@pytest.fixture
def auth_client(api_client, user):
    """An APIClient authenticated as ``user`` via a bearer access token."""
    from rest_framework_simplejwt.tokens import RefreshToken

    access = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api_client


@pytest.fixture
def password():
    return DEFAULT_PASSWORD
