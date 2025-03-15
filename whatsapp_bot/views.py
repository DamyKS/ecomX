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
import tempfile
import os
from cloudinary.uploader import upload
from google import genai
from google.genai import types
from twilio.twiml.messaging_response import MessagingResponse
import os

# Import your actual models
from django.contrib.auth import get_user_model
from stores.models import Store
from products.models import Product, Image, Category
from orders.models import Order, CartItem

User = get_user_model()

TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")

# Command structure and help information
# Update the COMMANDS dictionary to include the new category commands
COMMANDS = {
    "help": "Show available commands",
    "orders": "List recent orders",
    "products": "List your products",
    "categories": "List your categories",
    "add product": "Add a new product (follow format: add product NAME|CATEGORY|PRICE|DESCRIPTION|STOCK). Attach images to add them to the product.",
    "update product": "Update a product (format: update product ID|NAME|CATEGORY|PRICE|DESCRIPTION|STOCK)",
    "delete product": "Delete a product (format: delete product ID)",
    "add category": "Add a new category (format: add category NAME)",
    "edit category": "Edit a category (format: edit category OLD_NAME|NEW_NAME)",
    "delete category": "Delete a category (format: delete category NAME)",
    "stats": "Show store statistics",
    "ai": "Ask a question to the AI model (format: ai QUESTION)",
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
        result += f"Order #{order.id} - N{order.total_price:.2f}\n"
        result += f"Status: {order.status}\n"
        result += f"Date: {order.created_at.strftime('%Y-%m-%d')}\n"

        # Using your CartItem model to access items in the order
        if order.cart:
            cart_items = CartItem.objects.filter(cart=order.cart)
            result += "Products:\n"

            for item in cart_items:
                result += f"- {item.quantity}x {item.product.name} (N{item.product.price:.2f})\n"

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
        result += f"Price: N{product.price:.2f}\n"
        result += f"Description: {product.description}\n"
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
            f"Product added successfully!\nID: {product.id}\nName: {name}\nPrice: N{price:.2f}",
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

            return f"Product updated successfully!\nID: {product.id}\nName: {name}\nPrice: N{price:.2f}"
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
                # Create a new Image instance
                new_image = Image()

                # Create a temporary file to store the image content
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(image_response.content)
                temp_file.close()

                # Upload to Cloudinary directly using the Cloudinary field
                # The folder structure can be specified in the upload options
                upload_result = upload(
                    temp_file.name,
                    folder=f"products/images/{product.store.id}/{product.id}",
                    public_id=f"product_{product.id}_image_{i}",
                )

                # Now assign the Cloudinary response to the CloudinaryField
                # Since CloudinaryField handles the URL formatting internally
                new_image.image = upload_result["public_id"]
                new_image.save()

                # Remove temporary file
                os.unlink(temp_file.name)

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
    result += f"Total Revenue: N{revenue:.2f}\n"
    result += f"Total Customers: {recent_customers}\n"
    result += f"Recent Orders: {recent_order_count}\n"

    return result


def handle_ai(message):
    """
    Process AI queries from users via WhatsApp

    Args:
        message (str): The message body starting with 'ai'

    Returns:
        str: Response from the AI model
    """
    try:
        # Strip 'ai' prefix and extract the actual query
        query = message.lower().replace("ai", "", 1).strip()

        if not query:
            return "Please provide a question after 'ai'. Example: 'ai what is a noun?'"

        # Initialize Google Generative AI client
        api_key = config("GOOGLE_GENERATIVE_AI_API_KEY")

        client = genai.Client(api_key=api_key)

        # Define system instructions
        sys_instruct = (
            "You are a helpful assistant responding to questions by online stoee owners on ecomX's  via WhatsApp bot. "
            "Keep your answers concise and informative, but a bit detailed  since this is for a mobile interface. "
            "Format your response appropriately for WhatsApp (no HTML, use * for bold, etc.)."
        )

        # Generate content using Google's Generative AI
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                max_output_tokens=500,  # Limit response length for WhatsApp
            ),
            contents=[query],
        )

        # Extract and clean the response text
        ai_response = response.text

        return ai_response

    except Exception as e:
        return f"Sorry, I couldn't process your AI request: {str(e)}"


# here
# Add these functions to your existing code


def format_category_list(categories):
    """Format a list of categories for WhatsApp display"""
    if not categories:
        return "No categories found in your store."

    result = "Your Categories:\n\n"
    for category in categories:
        # Count products in this category
        product_count = Product.objects.filter(category=category).count()
        result += f"ID: {category.id}\n"
        result += f"Name: {category.name}\n"
        result += f"Products: {product_count}\n\n"

    return result


def handle_add_category(store, message_parts):
    """Handle the add category command"""
    # Expected format: add category NAME
    try:
        if len(message_parts) < 3:
            return "Invalid format. Use: add category NAME"

        category_name = message_parts[2].strip()

        # Check if category already exists
        existing_category = Category.objects.filter(
            store=store, name=category_name
        ).first()
        if existing_category:
            return f"Category '{category_name}' already exists with ID: {existing_category.id}"

        # Create category
        category = Category.objects.create(store=store, name=category_name)

        return f"Category added successfully!\nID: {category.id}\nName: {category_name}"

    except Exception as e:
        return f"Error adding category: {str(e)}"


def handle_edit_category(store, message_parts):
    """Handle the edit category command"""
    # Expected format: edit category OLD_NAME|NEW_NAME
    try:
        if len(message_parts) < 3:
            return "Invalid format. Use: edit category OLD_NAME|NEW_NAME"

        name_parts = message_parts[2].split("|")
        if len(name_parts) != 2:
            return "Invalid format. Use: edit category OLD_NAME|NEW_NAME"

        old_name = name_parts[0].strip()
        new_name = name_parts[1].strip()

        # Check if old category exists
        try:
            category = Category.objects.get(store=store, name=old_name)

            # Check if new name already exists (but isn't the same category)
            existing_category = Category.objects.filter(
                store=store, name=new_name
            ).first()
            if existing_category and existing_category.id != category.id:
                return f"Cannot update: A category named '{new_name}' already exists."

            # Update the category
            category.name = new_name
            category.save()

            return f"Category updated successfully!\nID: {category.id}\nNew Name: {new_name}"

        except Category.DoesNotExist:
            return f"Category '{old_name}' not found in your store."

    except Exception as e:
        return f"Error updating category: {str(e)}"


def handle_delete_category(store, message_parts):
    """Handle the delete category command"""
    # Expected format: delete category NAME
    try:
        if len(message_parts) < 3:
            return "Invalid format. Use: delete category NAME"

        category_name = message_parts[2].strip()

        try:
            # Find the category
            category = Category.objects.get(store=store, name=category_name)

            # Check if products are using this category
            product_count = Product.objects.filter(category=category).count()
            if product_count > 0:
                return f"Cannot delete: Category '{category_name}' is used by {product_count} products. Update these products first."

            # Delete the category
            category_id = category.id
            category.delete()

            return (
                f"Category '{category_name}' (ID: {category_id}) deleted successfully."
            )

        except Category.DoesNotExist:
            return f"Category '{category_name}' not found in your store."

    except Exception as e:
        return f"Error deleting category: {str(e)}"


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
            "Please register your WhatsApp number in your dashboard settings."
        )
        return HttpResponse(str(response))

    # Get the seller's store
    store = get_store_for_seller(seller)

    if not store:
        response.message(
            "You don't have a store set up yet. Please create a store in the platform first."
        )
        return HttpResponse(str(response))

    # Check if there's an image without caption (or with empty caption)
    if num_media > 0 and not message_body:
        # Get the most recently created product for this store
        try:
            latest_product = Product.objects.filter(store=store).latest("created_at")

            # Process the images for the latest product
            image_count, errors = process_media_to_images(
                request, latest_product, num_media
            )

            result_message = f"Added {image_count} image(s) to your latest product '{latest_product.name}'."
            if errors:
                result_message += "\nSome errors occurred during image processing."

            response.message(result_message)
            return HttpResponse(str(response))

        except Product.DoesNotExist:
            response.message(
                "You don't have any products yet. Please create a product first."
            )
            return HttpResponse(str(response))

    # Process text commands
    message_parts = message_body.lower().split(" ", 2)
    command = message_parts[0] if message_parts else ""
    # ✅
    # Process various commands
    if message_body.lower() == "help":
        help_text = f"Welcome to *{store.name}*\n\n *Available commands*:\n\n"
        for cmd, desc in COMMANDS.items():
            help_text += f"*{cmd}* - {desc}\n\n"
        response.message(help_text)
    elif message_body.lower().startswith("ai "):
        ai_response = handle_ai(message_body)
        ai_response = "*AI Response:*\n\n" + ai_response
        response.message(ai_response)
        return HttpResponse(str(response))

    elif message_body.lower() == "orders":
        # Get recent orders
        recent_orders = Order.objects.filter(store=store).order_by("-created_at")[:6]
        response.message(format_order_list(recent_orders))

    elif message_body.lower() == "products":
        # Get products list
        products = Product.objects.filter(store=store)
        response.message(format_product_list(products))

    elif message_body.lower() == "categories":
        # Get categories list
        categories = Category.objects.filter(store=store)
        response.message(format_category_list(categories))

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

    elif message_body.lower().startswith("add category"):
        result = handle_add_category(store, message_parts)
        response.message(result)

    elif message_body.lower().startswith("edit category"):
        result = handle_edit_category(store, message_parts)
        response.message(result)

    elif message_body.lower().startswith("delete category"):
        result = handle_delete_category(store, message_parts)
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
            f"Hello {seller.full_name}! Welcome to *{store.name}* WhatsApp manager.\n\n"
            "Type *'help'* to see available commands."
        )

    return HttpResponse(str(response))
