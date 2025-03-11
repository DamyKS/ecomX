import requests

# Base URL of your Django server (update if different)
BASE_URL = "http://127.0.0.1:8000/api/v1/products/"

# Sample data for creating a product
PRODUCT_DATA = {
    "store_id": "850df182-beea-4f83-bacb-992247fa0932",  # Replace with actual store ID
    # "sku": "TEST123",
    "selling_type": "Retail",
    "weight": "2.5",
    "dimensions": "20x10x5",
    "name": "Test Product",
    "description": "This is a test product",
    "price": "49.99",
    "stock": "10",
    "category_id": 1,  # Replace with actual category ID
}

# Image files to upload
image_files = [
    ("images", ("download_4.jpg", open("download_4.jpg", "rb"), "image/jpeg")),
    ("images", ("download_4.jpg", open("download_4.jpg", "rb"), "image/jpeg")),
]

# Send POST request to create a product
response = requests.post(BASE_URL, data=PRODUCT_DATA, files=image_files)

# Print the response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())

# Close the files
for _, file in image_files:
    file[1].close()


# http://127.0.0.1:8000/admin/stores/store/850df182-beea-4f83-bacb-992247fa0932/change/
