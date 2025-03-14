from django.urls import path, include

from .views import DashboardView


app_name = "seller_dashboard"


urlpatterns = [
    path("", DashboardView.as_view(), name="seller_dashboard"),
]
