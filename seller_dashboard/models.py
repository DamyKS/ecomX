from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Dashboard(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_dashboards"
    )
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.owner.email


# class MonthlyRecord(models.Model):
#     """
#     Stores a snapshot of the user's dashboard data (total_revenue and total_orders)
#     for a given month.
#     """

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     # We'll store the "month" as a DateField with day=1 for convenience
#     month = models.DateField()
#     total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_orders = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.month.strftime('%Y-%m')}"
