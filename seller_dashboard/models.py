from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Dashboard(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
