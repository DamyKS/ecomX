from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    USER_TYPES = (
        ("seller", "Seller"),
        ("customer", "Customer"),
    )
    user_type = models.CharField(max_length=10, default="customer", choices=USER_TYPES)
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True
    )

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Optional
    last_access = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-created_at"]  # newest first

    def __str__(self):
        return self.email
