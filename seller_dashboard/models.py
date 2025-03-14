from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


# class Loan(models.Model):
#     STATUS_CHOICES = [
#         ("active", "Active"),
#         ("closed", "Closed"),
#         ("defaulted", "Defaulted"),
#     ]

#     PAYMENT_STATUS_CHOICES = [
#         ("current", "Current"),
#         ("late", "Late"),
#         ("paid_off", "Paid Off"),
#     ]
#     borrower = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="loans", null=True, blank=True
#     )
#     loan_id = models.CharField(max_length=20, unique=True, editable=False)
#     loan_type = models.CharField(max_length=50)  # choices=LOAN_TYPES)
#     purpose = models.CharField(max_length=255)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     interest_rate = models.FloatField()
#     term_months = models.IntegerField()
#     start_date = models.DateField()
#     end_date = models.DateField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
#     payment_status = models.CharField(
#         max_length=20, choices=PAYMENT_STATUS_CHOICES, default="current"
#     )

#     def save(self, *args, **kwargs):
#         if not self.loan_id:
#             self.loan_id = (
#                 f"LOAN-{self.start_date.year}-{str(uuid.uuid4())[:8].upper()}"
#             )
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.loan_id} - {self.loan_type} - {self.amount}"


class Dashboard(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_dashboards"
    )
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)
    eligibility_score = models.IntegerField(default=0)
    max_loan_amount = models.IntegerField(default=50000)

    def __str__(self):
        return self.owner.email


from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import date

User = get_user_model()


class Loan(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("closed", "Closed"),
        ("defaulted", "Defaulted"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("current", "Current"),
        ("late", "Late"),
        ("paid_off", "Paid Off"),
    ]

    # Add borrower reference
    borrower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="loans", null=True, blank=True
    )

    loan_id = models.CharField(max_length=20, unique=True, editable=False)
    loan_type = models.CharField(max_length=50)
    purpose = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField()
    term_months = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="current"
    )

    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = (
                f"LOAN-{self.start_date.year}-{str(uuid.uuid4())[:8].upper()}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_id} - {self.loan_type} - {self.amount}"


class Payment(models.Model):
    """
    Stores each monthly payment made towards a Loan.
    """

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()

    def __str__(self):
        return f"Payment for {self.loan.loan_id} - {self.amount}"


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
