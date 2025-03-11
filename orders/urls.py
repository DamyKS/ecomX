from django.urls import path
from .views import (
    AddToCartAPIView,
    ViewCartAPIView,
    CreateOrderAPIView,
    OrderDetailAPIView,
)

app_name = "orders"
urlpatterns = [
    path("cart/add/", AddToCartAPIView.as_view(), name="cart-add"),
    path("cart/", ViewCartAPIView.as_view(), name="cart-view"),
    path("create/", CreateOrderAPIView.as_view(), name="order-create"),
    path("<int:order_id>/", OrderDetailAPIView.as_view(), name="order-detail"),
]
