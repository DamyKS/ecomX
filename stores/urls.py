from django.urls import path
from .views import StoreView, StoreDetailView

app_name = "stores"
urlpatterns = [
    path("", StoreView.as_view(), name="stores"),
    path("<uuid:id>/", StoreDetailView.as_view(), name="store_detail"),
]
