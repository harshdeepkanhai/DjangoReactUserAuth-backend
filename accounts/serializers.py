from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read-only public representation of a user."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_superuser")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create a new user.

    The password is run through Django's configured validators and is
    write-only; it is never returned in a response.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def create(self, validated_data):
        # Use the manager so the password is hashed and the email normalized.
        return User.objects.create_user(**validated_data)


class LoginTokenSerializer(TokenObtainPairSerializer):
    """Issue access/refresh tokens and embed the authenticated user.

    Extends SimpleJWT's default so the login response is
    ``{"access": ..., "refresh": ..., "user": {...}}`` in a single round-trip.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
