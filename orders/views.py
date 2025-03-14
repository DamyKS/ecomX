from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order
from products.models import Product
from stores.models import Store
from .serializers import CartSerializer, OrderSerializer
from django.db.models import Sum


class AddToCartAPIView(APIView):
    """
    POST /api/cart/add/
    Adds a product to the user's active cart.
    """

    def post(self, request):
        user = request.user  # Get the logged-in user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        product = get_object_or_404(Product, id=product_id)
        store = product.store

        # Get or create an active cart for the user
        cart, created = Cart.objects.get_or_create(
            user=user, store=store, status="active"
        )

        # Check if product already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response(
            {"message": "Product added to cart!"}, status=status.HTTP_201_CREATED
        )


class ViewCartAPIView(APIView):
    """
    GET /api/cart/?store_id={store_id}
    Retrieves all items in the user's active cart.
    """

    def get(self, request):
        user = request.user
        store_id = request.query_params.get("store_id")
        store = get_object_or_404(Store, id=store_id)
        try:
            cart = get_object_or_404(Cart, user=user, status="active")
        except Cart.DoesNotExist:
            # create cart
            cart = Cart.objects.create(user=user, store=store, status="active")

        cart_items = CartItem.objects.filter(cart=cart)
        cart_data = [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
            }
            for item in cart_items
        ]

        return Response(cart_data, status=status.HTTP_200_OK)


class CreateOrderAPIView(APIView):
    """
    POST /api/orders/create/
    Converts the user's cart into an order and clears the cart.
    """

    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user, status="active")
        payment_method = request.data.get("payment_method")
        shipping_address = request.data.get("shipping_address")

        # Calculate total price
        total_price = (
            CartItem.objects.filter(cart=cart).aggregate(Sum("product__price"))[
                "product__price__sum"
            ]
            or 0
        )

        # Create an order from the cart
        order = Order.objects.create(
            cart=cart,
            user=user,
            store=cart.store,
            total_price=total_price,
            status="pending",
            payment_method=payment_method,
            shipping_address=shipping_address,
        )

        # Change cart status to inactive
        cart.status = "inactive"
        cart.save()

        # Create a new active cart for the user
        Cart.objects.create(user=user, store=cart.store, status="active")

        return Response(
            {"message": "Order placed successfully!", "order_id": order.id},
            status=status.HTTP_201_CREATED,
        )


# class ListOrderAPIView(APIView):
#     """
#     GET /api/orders/
#     Retrieves all orders placed by the user.
#     """

#     def get(self, request):

#         user = request.user
#         store = get_object_or_404(Store, owner=user)
#         orders = Order.objects.filter(store=store)
#         orders = Order.objects.filter(user=user)

#         order_data = [
#             {
#                 "id": order.id,
#                 "store": order.store.name,
#                 "total_price": order.total_price,
#                 "status": order.status,
#             }
#             for order in orders
#         ]

#         return Response(order_data, status=status.HTTP_200_OK)

from django.utils import timezone
from datetime import timedelta

4


class ListOrderAPIView(APIView):
    """
    GET /api/store/orders/dashboard/
    Returns a summary of orders and order history for the store dashboard.
    """

    def get(self, request):
        user = request.user
        store = get_object_or_404(Store, owner=user)

        # Get all orders for this store
        orders = Order.objects.filter(store=store)

        # Calculate counts for the order summary
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_orders_count = orders.filter(created_at__gte=thirty_days_ago).count()
        pending_orders_count = orders.filter(status="pending").count()
        delivered_orders_count = orders.filter(status="delivered").count()

        # Prepare order history data
        order_history = []
        for order in orders:
            order_history.append(
                {
                    "order_id": order.id,
                    "ordered_date": order.created_at.strftime("%d-%m-%Y"),
                    "customer_name": order.user.get_full_name() or order.user.username,
                    # "product_name": order.cart.items.first().product.name if order.cart and order.cart.items.exists() else "N/A",
                    "total_price": str(order.total_price),
                    "status": order.status,
                }
            )

        # Format the response
        response_data = {
            "order_summary": {
                "new_orders": new_orders_count,
                "pending_orders": pending_orders_count,
                "delivered": delivered_orders_count,
            },
            "order_history": order_history,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class OrderDetailAPIView(APIView):
    """
    GET /api/orders/{order_id}/
    Retrieves details of a specific order.
    """

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        order_items = CartItem.objects.filter(cart=order.cart)
        order_data = {
            "id": order.id,
            "status": order.status,
            "items": [
                {
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "price": item.product.price,
                }
                for item in order_items
            ],
        }

        return Response(order_data, status=status.HTTP_200_OK)
