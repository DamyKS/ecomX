from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from .serializers import (
    UserSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    MeUserSerializer,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()
from orders.models import Cart
from stores.models import Store
from seller_dashboard.models import Dashboard


class RegisterView(APIView):
    def post(self, request):
        user_type = request.data.get("user_type")

        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(user_serializer.validated_data["password"])
            if user_type == "customer":
                store_id = request.data.get("store_id")
                store = Store.objects.get(id=store_id)
                store.customers.add(user)
            elif user_type == "seller":
                seller_dashboard = Dashboard.objects.create(owner=user)
                seller_dashboard.save()
            user.save()
            user_data = UserSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get(
                settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]
            )
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            response = Response(
                {"message": "Logout successful"}, status=status.HTTP_200_OK
            )
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE"],
                "",
                max_age=0,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                "",
                max_age=0,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
            return response
        except Exception as e:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                context = {
                    "user": user,
                    "reset_url": f"https://yourfrontend.com/reset-password?token={token}?email={email}",
                    "valid_hours": 24,
                }
                html_message = render_to_string(
                    "accounts/password_reset_email.html", context
                )
                plain_message = html_message
                subject = "Reset Your Password"
                recipient_list = [email]
                from_email = settings.DEFAULT_FROM_EMAIL
                try:
                    with get_connection(
                        host=settings.MAILERSEND_SMTP_HOST,
                        port=settings.MAILERSEND_SMTP_PORT,
                        username=settings.MAILERSEND_SMTP_USERNAME,
                        password=settings.MAILERSEND_API_KEY,
                        use_tls=True,
                    ) as connection:
                        email = EmailMessage(
                            subject=subject,
                            body=plain_message,
                            to=recipient_list,
                            from_email=from_email,
                            connection=connection,
                        )
                        email.content_subtype = "html"
                        email.send()
                    return Response(
                        {"message": "Password reset email sent"},
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    return Response(
                        {"error": "Failed to send email"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except User.DoesNotExist:
                return Response(
                    {
                        "message": "If an account exists with this email, a password reset link has been sent."
                    },
                    status=status.HTTP_200_OK,
                )


class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=request.data.get("email"))
                if default_token_generator.check_token(
                    user, serializer.validated_data["token"]
                ):
                    user.set_password(serializer.validated_data["new_password"])
                    user.save()
                    return Response({"message": "Password has been reset"})
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            tokens = response.data
            response = Response({"message": "Login successful"})
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE"],
                tokens["access"],
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                tokens["refresh"],
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        previous_password = request.data.get("previous_password")
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")
        if not previous_password or not password1 or not password2:
            return Response(
                {"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        if not check_password(previous_password, user.password):
            return Response(
                {"error": "Previous password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if password1 != password2:
            return Response(
                {"error": "New passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password1)
        user.save()
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        store_id = None
        if user.user_type == "seller":
            store = Store.objects.get(owner=user)
            store_id = store.id
        serializer = MeUserSerializer(request.user)
        if store_id:
            serializer.data["store_id"] = store_id
        return Response(serializer.data, status=status.HTTP_200_OK)
