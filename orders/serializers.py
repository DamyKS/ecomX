from rest_framework import serializers
from .models import Cart, CartItem, Order
from stores.models import Store
from products.models import Product

# If you have a ProductSerializer already, you can import it; otherwise, here’s a simple one.
# from products.serializers import ProductSerializer


# A simple ProductSerializer example for nested representation.
class ProductSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "description",
            "product_image",
        )  # adjust as needed

    def get_product_image(self, obj):
        # get all images of the product and return the url of the first one if it exists
        images = obj.images.all()
        if images:
            return images[0].image.url
        return None


class CartItemSerializer(serializers.ModelSerializer):
    # For reading, return full product details.
    product = ProductSerializer(read_only=True)
    # For writes, accept a product id.
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ("product", "product_id", "quantity")  # "id"


class CartSerializer(serializers.ModelSerializer):
    # Represent the user as a string (for example, username); set this from the authenticated user in your view.
    user = serializers.StringRelatedField(read_only=True)
    # For writes, expect a store id.
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source="store"
    )
    # Nested cart items.
    cart_items = CartItemSerializer(many=True, required=False)

    class Meta:
        model = Cart
        fields = ("id", "user", "store_id", "cart_items", "status")

    def create(self, validated_data):
        cart_items_data = validated_data.pop("cart_items", [])
        cart = Cart.objects.create(**validated_data)
        for item_data in cart_items_data:
            # Create each CartItem and add it to the many-to-many relation.
            cart_item = CartItem.objects.create(**item_data)
            cart.cart_items.add(cart_item)
        return cart

    def update(self, instance, validated_data):
        cart_items_data = validated_data.pop("cart_items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if cart_items_data is not None:
            # Optionally, clear existing cart items and replace with new ones.
            instance.cart_items.clear()
            for item_data in cart_items_data:
                cart_item = CartItem.objects.create(**item_data)
                instance.cart_items.add(cart_item)
        return instance


class OrderSerializer(serializers.ModelSerializer):
    # For read operations, nest full cart details.
    cart = CartSerializer(read_only=True)
    # For writes, accept a cart id.
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(), source="cart", write_only=True
    )
    # Represent the user as a string.
    user = serializers.StringRelatedField(read_only=True)
    # For writes, accept a store id.
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source="store"
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "cart",
            "cart_id",
            "user",
            "store_id",
            "total_price",
            "status",
            "created_at",
            "shipping_address",
            "payment_method",
        )
