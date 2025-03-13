import requests
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from decouple import config
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Sum
from urllib.parse import urljoin

# Import your actual models
from django.contrib.auth import get_user_model
from stores.models import Store
from products.models import Product, Image, Category
from orders.models import Order, CartItem

User = get_user_model()

TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")

# Command structure and help information
COMMANDS = {
    "help": "Show available commands",
    "orders": "List recent orders",
    "products": "List your products",
    "add product": "Add a new product (follow format: add product NAME|CATEGORY|PRICE|DESCRIPTION|STOCK). Attach images to add them to the product.",
    "update product": "Update a product (format: update product ID|NAME|CATEGORY|PRICE|DESCRIPTION|STOCK)",
    "delete product": "Delete a product (format: delete product ID)",
    "stats": "Show store statistics",
}


def get_seller_from_whatsapp(phone_number):
    """
    Find the seller based on their WhatsApp number
    phone_number format: 'whatsapp:+1234567890'
    """
    # Extract the number without 'whatsapp:' prefix
    clean_number = phone_number.replace("whatsapp:", "")

    try:
        # Using your User model with user_type="seller"
        seller = User.objects.get(phone_number=clean_number, user_type="seller")
        return seller
    except User.DoesNotExist:
        return None


def get_store_for_seller(seller):
    """Get the store associated with a seller"""
    try:
        # Using your Store model that has an owner field
        store = Store.objects.get(owner=seller)
        return store
    except Store.DoesNotExist:
        return None


def format_order_list(orders):
    """Format a list of orders for WhatsApp display"""
    if not orders:
        return "No recent orders found."

    result = "Recent Orders:\n\n"
    for order in orders:
        result += f"Order #{order.id} - ${order.total_price:.2f}\n"
        result += f"Status: {order.status}\n"
        result += f"Date: {order.created_at.strftime('%Y-%m-%d')}\n"

        # Using your CartItem model to access items in the order
        if order.cart:
            cart_items = CartItem.objects.filter(cart=order.cart)
            result += "Products:\n"

            for item in cart_items:
                result += f"- {item.quantity}x {item.product.name} (${item.product.price:.2f})\n"

        result += "\n"

    return result


def format_product_list(products):
    """Format a list of products for WhatsApp display"""
    if not products:
        return "No products found in your store."

    result = "Your Products:\n\n"
    for product in products:
        result += f"ID: {product.id}\n"
        result += f"Name: {product.name}\n"
        result += f"Category: {product.category.name if product.category else 'None'}\n"
        result += f"Price: ${product.price:.2f}\n"
        result += f"Stock: {product.stock}\n"
        result += f"Images: {product.images.count()}\n\n"

    return result


def handle_add_product(store, message_parts):
    """Handle the add product command and return the created product"""
    # Expected format: add product NAME|CATEGORY|PRICE|DESCRIPTION|STOCK
    try:
        product_info = message_parts[2].split("|")
        if len(product_info) < 5:
            return (
                None,
                "Invalid format. Use: add product NAME|CATEGORY|PRICE|DESCRIPTION|STOCK",
            )

        name = product_info[0].strip()
        category_name = product_info[1].strip()
        price = float(product_info[2].strip())
        description = product_info[3].strip()
        stock = int(product_info[4].strip())

        # Get or create category
        category = None
        if category_name:
            category, created = Category.objects.get_or_create(
                store=store, name=category_name
            )

        # Create product using your existing models
        product = Product.objects.create(
            store=store,
            category=category,
            name=name,
            price=price,
            description=description,
            stock=stock,
        )

        return (
            product,
            f"Product added successfully!\nID: {product.id}\nName: {name}\nPrice: ${price:.2f}",
        )

    except (IndexError, ValueError) as e:
        return None, f"Error adding product: {str(e)}"


def handle_update_product(store, message_parts):
    """Handle the update product command"""
    # Expected format: update product ID|NAME|CATEGORY|PRICE|DESCRIPTION|STOCK
    try:
        product_info = message_parts[2].split("|")
        if len(product_info) < 6:
            return "Invalid format. Use: update product ID|NAME|CATEGORY|PRICE|DESCRIPTION|STOCK"

        product_id = int(product_info[0].strip())
        name = product_info[1].strip()
        category_name = product_info[2].strip()
        price = float(product_info[3].strip())
        description = product_info[4].strip()
        stock = int(product_info[5].strip())

        # Get and update the product
        try:
            product = Product.objects.get(id=product_id, store=store)

            # Update or create category
            if category_name:
                category, created = Category.objects.get_or_create(
                    store=store, name=category_name
                )
                product.category = category

            product.name = name
            product.price = price
            product.description = description
            product.stock = stock
            product.save()

            return f"Product updated successfully!\nID: {product.id}\nName: {name}\nPrice: ${price:.2f}"
        except Product.DoesNotExist:
            return f"Product with ID {product_id} not found in your store."

    except (IndexError, ValueError) as e:
        return f"Error updating product: {str(e)}"


def handle_delete_product(store, message_parts):
    """Handle the delete product command"""
    # Expected format: delete product ID
    try:
        product_id = int(message_parts[2].strip())

        try:
            product = Product.objects.get(id=product_id, store=store)
            product_name = product.name
            product.delete()

            return f"Product '{product_name}' (ID: {product_id}) deleted successfully."
        except Product.DoesNotExist:
            return f"Product with ID {product_id} not found in your store."

    except (IndexError, ValueError) as e:
        return f"Error deleting product: {str(e)}"


def process_media_to_images(request, product, num_media):
    """Process media items in the request and add them as images to the product"""
    image_count = 0
    errors = []

    # Process all images attached to the message
    for i in range(num_media):
        media_url = request.POST.get(f"MediaUrl{i}")
        media_type = request.POST.get(f"MediaContentType{i}")

        # Make sure we only process images
        if not media_type.startswith("image/"):
            errors.append(f"File type {media_type} is not an image and was skipped")
            continue

        # Authenticate and download the image
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        image_response = requests.get(media_url, auth=auth)

        if image_response.status_code == 200:
            try:
                # Create a new Image instance for this product
                new_image = Image.objects.create()

                # For Cloudinary, we'd typically use a different approach than direct file saving
                # This is a placeholder that should be replaced with your Cloudinary implementation
                # The actual implementation depends on how your Cloudinary field is configured

                # For this example, we're using a naming convention that would identify the image
                file_name = f"products/images/{product.store.id}_{product.id}_{i}.jpg"

                # Update the cloudinary field - this is a simplified representation
                # In a real implementation, you would use Cloudinary's upload API
                new_image.image = file_name
                new_image.save()

                # Add the image to the product's images
                product.images.add(new_image)
                image_count += 1

            except Exception as e:
                errors.append(f"Error processing image {i}: {str(e)}")

    return image_count, errors


def get_store_stats(store):
    """Get statistics about the store"""
    total_products = Product.objects.filter(store=store).count()
    total_orders = Order.objects.filter(store=store).count()

    # Calculate completed orders revenue
    revenue = (
        Order.objects.filter(store=store, status="completed").aggregate(
            Sum("total_price")
        )["total_price__sum"]
        or 0
    )

    # Get recent customers
    recent_customers = store.customers.count()

    # Get recent orders
    recent_orders = Order.objects.filter(store=store).order_by("-created_at")[:5]
    recent_order_count = recent_orders.count()

    result = "Store Statistics:\n\n"
    result += f"Store Name: {store.name}\n"
    result += f"Total Products: {total_products}\n"
    result += f"Total Orders: {total_orders}\n"
    result += f"Total Revenue: ${revenue:.2f}\n"
    result += f"Total Customers: {recent_customers}\n"
    result += f"Recent Orders: {recent_order_count}\n"

    return result


@csrf_exempt
def message(request):
    user_whatsapp = request.POST.get("From")
    message_body = request.POST.get("Body", "").strip()
    num_media = int(request.POST.get("NumMedia", 0))
    response = MessagingResponse()

    # Identify the seller from their WhatsApp number
    seller = get_seller_from_whatsapp(user_whatsapp)

    if not seller:
        response.message(
            "Sorry, your WhatsApp number is not registered with any seller account. "
            "Please register your WhatsApp number in your account settings."
        )
        return HttpResponse(str(response))

    # Get the seller's store
    store = get_store_for_seller(seller)

    if not store:
        response.message(
            "You don't have a store set up yet. Please create a store in the platform first."
        )
        return HttpResponse(str(response))

    # Process text commands
    message_parts = message_body.lower().split(" ", 2)
    command = message_parts[0] if message_parts else ""

    # Process various commands
    if message_body.lower() == "help":
        help_text = "Available commands:\n\n"
        for cmd, desc in COMMANDS.items():
            help_text += f"{cmd} - {desc}\n"
        response.message(help_text)

    elif message_body.lower() == "orders":
        # Get recent orders
        recent_orders = Order.objects.filter(store=store).order_by("-created_at")[:5]
        response.message(format_order_list(recent_orders))

    elif message_body.lower() == "products":
        # Get products list
        products = Product.objects.filter(store=store)
        response.message(format_product_list(products))

    elif message_body.lower().startswith("add product"):
        # Create the product
        product, result_message = handle_add_product(store, message_parts)

        # If product creation was successful and there are images, process them
        if product and num_media > 0:
            image_count, errors = process_media_to_images(request, product, num_media)

            # Add image results to the response message
            result_message += f"\n\n{image_count} images added to product."
            if errors:
                result_message += "\nSome errors occurred during image processing."

        response.message(result_message)

    elif message_body.lower().startswith("update product"):
        result = handle_update_product(store, message_parts)
        response.message(result)

    elif message_body.lower().startswith("delete product"):
        result = handle_delete_product(store, message_parts)
        response.message(result)

    elif message_body.lower() == "stats":
        stats = get_store_stats(store)
        response.message(stats)

    # Handle image uploads for existing products with format "product ID" + images
    elif message_body.lower().startswith("product ") and num_media > 0:
        try:
            # Extract product ID
            product_id = int(message_body.split("product ")[1].strip())

            try:
                # Get the product
                product = Product.objects.get(id=product_id, store=store)

                # Process the images
                image_count, errors = process_media_to_images(
                    request, product, num_media
                )

                result_message = f"Added {image_count} images to '{product.name}'."
                if errors:
                    result_message += "\nSome errors occurred during image processing."

                response.message(result_message)
            except Product.DoesNotExist:
                response.message(
                    f"Product with ID {product_id} not found in your store."
                )
        except (IndexError, ValueError):
            response.message("Invalid format. Use: product [ID] and attach images.")

    else:
        response.message(
            f"Hello {seller.full_name}! Welcome to your store WhatsApp manager.\n"
            "Type 'help' to see available commands."
        )

    return HttpResponse(str(response))
