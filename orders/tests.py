from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from stores.models import Store
from products.models import Product
from orders.models import Cart, CartItem, Order

User = get_user_model()


class CartAndOrderTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password")

        # Authenticate the test client
        self.client.force_authenticate(user=self.user)

        # Create a store (Ensure owner is set to avoid integrity errors)
        self.store = Store.objects.create(name="Test Store", owner=self.user)

        # Create products
        self.product1 = Product.objects.create(
            name="Leather Jacket", price=79.99, store=self.store
        )
        self.product2 = Product.objects.create(
            name="Leather Jacket 2", price=67.99, store=self.store
        )

        # Create a cart for the user
        self.cart = Cart.objects.create(user=self.user, store=self.store)

        # Add items to the cart
        self.cart_item = CartItem.objects.create(product=self.product1, quantity=2)
        self.cart.cart_items.add(self.cart_item)

    def test_add_product_to_cart(self):
        """Test adding a product to the cart."""
        data = {"product_id": self.product1.id, "quantity": 2}

        response = self.client.post("/api/cart/add/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Product added to cart!")

    def test_view_cart(self):
        """Test retrieving cart items."""
        response = self.client.get("/api/cart/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product_name"], "Leather Jacket")

    def test_place_order(self):
        """Test placing an order."""
        data = {
            "cart_id": self.cart.id,
            "payment_method": "credit_card",
            "shipping_address": "123 Test St, NY",
        }

        response = self.client.post("/api/orders/create/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_id", response.data)

    def test_get_order_details(self):
        """Test retrieving order details."""
        # Create an order first
        order = Order.objects.create(
            cart=self.cart,
            user=self.user,
            store=self.store,
            total_price=159.98,
            status="pending",
        )

        response = self.client.get(f"/api/orders/{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["items"][0]["product"], "Leather Jacket")
