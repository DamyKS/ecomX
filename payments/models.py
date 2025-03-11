from django.db import models
from orders.models import Order


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(
        max_length=20,  # choices=[("stripe", "Stripe"), ("paypal", "PayPal")]
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
