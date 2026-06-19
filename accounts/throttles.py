from rest_framework.throttling import ScopedRateThrottle


class AuthRateThrottle(ScopedRateThrottle):
    """Tight throttle for unauthenticated auth endpoints (register/login).

    Uses the ``auth`` rate from ``REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']``
    to blunt credential-stuffing and brute-force attempts.
    """

    scope = "auth"
