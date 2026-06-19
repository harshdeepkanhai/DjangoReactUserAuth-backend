from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Project user model.

    Subclassing ``AbstractUser`` from the start is the recommended Django
    convention: it lets the project add fields later without the painful
    swap that an in-place migration off the built-in user would require.

    ``username`` remains the login field (``USERNAME_FIELD``), preserving the
    existing username/password sign-in flow, while ``email`` is promoted to a
    required, unique field.
    """

    email = models.EmailField("email address", unique=True)

    objects = UserManager()

    # ``username`` stays the USERNAME_FIELD; require email when creating
    # superusers via ``createsuperuser``.
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username
