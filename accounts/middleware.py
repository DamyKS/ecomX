from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.conf import settings
from datetime import datetime, timezone
import jwt
from rest_framework_simplejwt.exceptions import TokenError


class JWTRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("Middleware called")
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        access_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if not refresh_token:
            return  # No way to refresh without refresh token

        try:
            # Check if the access token is expired using SimpleJWT's built-in check
            if access_token:
                token = AccessToken(access_token)
                token.check_exp()  # Raises TokenError if expired
                return  # Token is valid, no need to refresh
        except TokenError:
            pass  # Access token is expired
        # Try refreshing the access token
        try:
            # Manually decode refresh token to check its validity
            decoded = jwt.decode(
                refresh_token,
                settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=["HS256"],  # Adjust based on your JWT settings
            )
            # Generate a new access token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Add new access token to request
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"

            # Store new access token for response
            request.new_access_token = new_access_token
            # print("New access token issued via refresh token")
        except jwt.ExpiredSignatureError:
            print("Refresh token is expired")
        except jwt.InvalidTokenError:
            print("Invalid refresh token")
        except TokenError as e:
            print(f"Refresh token error: {e}")

    def process_response(self, request, response):
        if hasattr(request, "new_access_token"):
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE"],
                request.new_access_token,
                httponly=True,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )
        return response
