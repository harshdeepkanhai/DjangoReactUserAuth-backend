import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from .factories import DEFAULT_PASSWORD, UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


# --- registration --------------------------------------------------------


def test_register_creates_user_and_returns_tokens(api_client):
    payload = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": DEFAULT_PASSWORD,
        "first_name": "New",
        "last_name": "Bie",
    }
    resp = api_client.post(reverse("accounts:register"), payload, format="json")

    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["username"] == "newbie"
    assert "access" in body and "refresh" in body
    assert "password" not in body["user"]

    created = User.objects.get(username="newbie")
    assert created.check_password(DEFAULT_PASSWORD)


def test_register_rejects_weak_password(api_client):
    resp = api_client.post(
        reverse("accounts:register"),
        {"username": "weak", "email": "weak@example.com", "password": "123"},
        format="json",
    )
    assert resp.status_code == 400
    assert "password" in resp.json()
    assert not User.objects.filter(username="weak").exists()


def test_register_rejects_duplicate_username(api_client):
    UserFactory(username="taken", email="first@example.com")
    resp = api_client.post(
        reverse("accounts:register"),
        {"username": "taken", "email": "second@example.com", "password": DEFAULT_PASSWORD},
        format="json",
    )
    assert resp.status_code == 400
    assert "username" in resp.json()


# --- login ---------------------------------------------------------------


def test_login_returns_tokens_and_user(api_client, user, password):
    resp = api_client.post(
        reverse("accounts:login"),
        {"username": user.username, "password": password},
        format="json",
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["username"] == user.username
    assert body["access"] and body["refresh"]


def test_login_rejects_bad_credentials(api_client, user):
    resp = api_client.post(
        reverse("accounts:login"),
        {"username": user.username, "password": "wrong-password"},
        format="json",
    )
    assert resp.status_code == 401


# --- current user --------------------------------------------------------


def test_me_requires_authentication(api_client):
    assert api_client.get(reverse("accounts:current-user")).status_code == 401


def test_me_returns_authenticated_user(auth_client, user):
    resp = auth_client.get(reverse("accounts:current-user"))
    assert resp.status_code == 200
    assert resp.json()["username"] == user.username


# --- refresh & logout ----------------------------------------------------


def test_refresh_issues_new_access(api_client, user, password):
    login = api_client.post(
        reverse("accounts:login"),
        {"username": user.username, "password": password},
        format="json",
    ).json()

    resp = api_client.post(
        reverse("accounts:token-refresh"),
        {"refresh": login["refresh"]},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.json()["access"]


def test_logout_blacklists_refresh_token(auth_client, user, password):
    login = auth_client.post(
        reverse("accounts:login"),
        {"username": user.username, "password": password},
        format="json",
    ).json()

    logout = auth_client.post(
        reverse("accounts:logout"),
        {"refresh": login["refresh"]},
        format="json",
    )
    assert logout.status_code == 205

    # The blacklisted refresh token can no longer mint access tokens.
    reuse = auth_client.post(
        reverse("accounts:token-refresh"),
        {"refresh": login["refresh"]},
        format="json",
    )
    assert reuse.status_code == 401
