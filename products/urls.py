from django.urls import path, include
from .views import CategoryAPIView, ProductAPIView, ProductDetailAPIView


app_name = "products"


urlpatterns = [
    path("", ProductAPIView.as_view(), name="list-create"),
    path("<int:product_id>/", ProductDetailAPIView.as_view(), name="detail"),
    #     path("", CategoryAPIView.as_view(), name="list-create"),
]
