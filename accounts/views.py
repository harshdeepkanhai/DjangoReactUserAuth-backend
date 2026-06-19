from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginTokenSerializer, RegisterSerializer, UserSerializer
from .throttles import AuthRateThrottle


def _tokens_for(user):
    """Return a freshly minted refresh/access pair for ``user``."""
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    """Create an account and return tokens so the client is logged in."""

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (AuthRateThrottle,)

    @extend_schema(
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "user": UserSerializer(),
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, **_tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Obtain an access/refresh pair plus the authenticated user."""

    serializer_class = LoginTokenSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (AuthRateThrottle,)


class LogoutView(APIView):
    """Blacklist a refresh token so it can no longer be used."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=inline_serializer(
            name="LogoutRequest",
            fields={"refresh": serializers.CharField()},
        ),
        responses={205: OpenApiResponse(description="Refresh token blacklisted.")},
    )
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response(
                {"detail": "The 'refresh' token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class CurrentUserView(generics.RetrieveAPIView):
    """Return the user resolved from the bearer token."""

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
