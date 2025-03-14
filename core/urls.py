from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import (
    RegisterView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    CustomTokenObtainPairView,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static


# from bank.views import DashboardAPIView
# from bank.views import AcctDetailView

# from bank.views import TransferAPIView
from products.views import CategoryAPIView, CategoryDetailAPIView

from whatsapp_bot import views

schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version="v1",
        description="API documentation for your project",
        terms_of_service="https://www.yoursite.com/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/register", RegisterView.as_view(), name="register"),
    path("api/v1/auth/login", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/v1/auth/logout", LogoutView.as_view(), name="logout"),
    path(
        "api/v1/auth/password/reset",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "api/v1/auth/password/reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # accounts
    path("api/v1/accounts/", include("accounts.urls")),
    # stores urls
    path("api/v1/stores/", include("stores.urls")),
    # products and categories urls
    path("api/v1/products/", include("products.urls")),
    path("api/v1/categories/", CategoryAPIView.as_view(), name="categories"),
    path(
        "api/v1/categories/<int:category_id>/",
        CategoryDetailAPIView.as_view(),
        name="category-detail",
    ),
    # orders urls
    path("api/v1/orders/", include("orders.urls")),
    # payments urls
    path("api/v1/payments/", include("payments.urls")),
    # seller dashboard urls
    path("api/v1/seller_dashboard/", include("seller_dashboard.urls")),
    # whatsapp bot urls
    # path("api/v1/whatsapp_bot/message", views.message, name="whatsapp_bot"),
    # # Swagger UI
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # Redoc UI
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Raw JSON schema
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
