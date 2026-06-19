from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Manager for the custom user model.

    Inherits Django's username-based ``create_user`` / ``create_superuser`` but
    normalizes the email on every creation so uniqueness is enforced
    consistently regardless of how the user is created (API, admin, shell).
    """

    def _create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email) if email else email
        return super()._create_user(username, email, password, **extra_fields)
