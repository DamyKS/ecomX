# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Use the refreshed token if available; otherwise, fallback to the cookie.
        token = getattr(request, "new_access_token", None)
        if token is None:
            token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if token is None:
            return None

        # Modify the request to include the token in the header.
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        return super().authenticate(request)
