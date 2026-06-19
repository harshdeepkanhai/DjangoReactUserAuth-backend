import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_create_user_hashes_password_and_normalizes_email():
    user = User.objects.create_user(
        username="alice",
        email="Alice@Example.COM",
        password="Sup3rStr0ng!pw",
    )
    assert user.check_password("Sup3rStr0ng!pw")
    # The domain portion is lower-cased by normalize_email.
    assert user.email == "Alice@example.com"
    assert not user.is_staff and not user.is_superuser


def test_create_superuser_flags():
    admin = User.objects.create_superuser(
        username="root",
        email="root@example.com",
        password="Sup3rStr0ng!pw",
    )
    assert admin.is_staff and admin.is_superuser


def test_email_must_be_unique():
    UserFactory(email="dup@example.com")
    with pytest.raises(IntegrityError):
        UserFactory(email="dup@example.com")


def test_str_returns_username():
    assert str(UserFactory(username="bob")) == "bob"
