from django.db import models
from stores.models import Store
from cloudinary.models import CloudinaryField


class Category(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.store.name}"


class Image(models.Model):
    image = CloudinaryField("products/images")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.image}"


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    # sku = models.CharField(max_length=255, default="")
    selling_type = models.CharField(max_length=20, default="")
    images = models.ManyToManyField(Image, related_name="products", blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dimensions = models.CharField(max_length=255, default="0x0x0")

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, default=0, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price} - {self.store.name}"
