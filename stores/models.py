from django.db import models
from django.contrib.auth import get_user_model
import uuid
from cloudinary.models import CloudinaryField

User = get_user_model()


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # slug = models.SlugField(unique=True)
    # description = models.TextField(blank=True, null=True)
    hero_name = models.CharField(max_length=255, null=True, blank=True)
    hero_description = models.TextField(blank=True, null=True)
    hero_image = CloudinaryField("stores/images")
    template = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.owner.email}"
