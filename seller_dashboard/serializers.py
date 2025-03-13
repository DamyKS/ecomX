from rest_framework import serializers
from .models import Loan, Dashboard, Payment


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "loan_type",
            "purpose",
            "amount",
            "interest_rate",
            "term_months",
            "start_date",
            "end_date",
            "status",
            "payment_status",
        ]


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = [
            "total_revenue",
            "total_orders",
            "new_customers",
            "eligibility_score",
            "max_loan_amount",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "loan", "amount", "payment_date"]
