from django.urls import path, include
from .views import SellerDashboardView


app_name = "seller_dashboard"


urlpatterns = [
    path("", SellerDashboardView.as_view(), name="seller_dashboard"),
]
