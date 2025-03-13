from django.shortcuts import render

# Create an api view for the seller dashboard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product
from orders.models import Order
from stores.models import Store
from products.serializers import ProductSerializer
from orders.serializers import OrderSerializer
from stores.serializers import StoreSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Dashboard


class SellerDashboardView(APIView):
    """
    API view to return all products, orders and stores by a particular user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        dashboard = Dashboard.objects.get(user=user)
        return Response(
            {
                "total_revenue": dashboard.total_revenue,
                "new_customers": dashboard.new_customers,
                "total_orders": dashboard.total_orders,
            },
            status=status.HTTP_200_OK,
        )
