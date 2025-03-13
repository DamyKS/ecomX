from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import timedelta

from .models import Dashboard, Loan, Payment
from .serializers import DashboardSerializer, LoanSerializer, PaymentSerializer


class DashboardView(APIView):
    """
    GET /api/v1/dashboard/
    Returns dashboard metrics + loan details for the logged-in user.
    """

    def get(self, request):
        user = request.user

        # 1) Fetch the user's dashboard
        dashboard = get_object_or_404(Dashboard, owner=user)
        dashboard_data = DashboardSerializer(dashboard).data

        # 2) Retrieve the user's loans
        loans = Loan.objects.filter(borrower=user)

        # 3) Build loan-specific data
        loans_data = []
        for loan in loans:
            # All payments for this loan, sorted by date
            payments = loan.payments.order_by("payment_date")

            # Total amount paid so far
            total_paid = payments.aggregate(Sum("amount"))["amount__sum"] or 0

            # Number of payments made
            payments_made = payments.count()
            payments_remaining = loan.term_months - payments_made

            # Last payment date (if any)
            last_payment_date = (
                payments.last().payment_date if payments.exists() else None
            )

            # Compute next payment date: last payment date + 30 days
            if last_payment_date:
                next_payment_date = last_payment_date + timedelta(days=30)
            else:
                # If no payments yet, next payment is 30 days from start_date
                next_payment_date = loan.start_date + timedelta(days=30)

            loans_data.append(
                {
                    "loan_id": loan.loan_id,
                    "loan_type": loan.loan_type,
                    "amount": str(loan.amount),
                    "interest_rate": loan.interest_rate,
                    "term_months": loan.term_months,
                    "start_date": str(loan.start_date),
                    "end_date": str(loan.end_date),
                    "status": loan.status,
                    "payment_status": loan.payment_status,
                    "total_paid": str(total_paid),
                    "payments_made": payments_made,
                    "payments_remaining": payments_remaining,
                    "next_payment_date": str(next_payment_date),
                }
            )

        # 4) Combine dashboard data + loans data into a single response
        response_data = {
            "total_revenue": float(dashboard_data["total_revenue"]),
            "new_customers": dashboard_data["new_customers"],
            "total_orders": dashboard_data["total_orders"],
            "max_loan_amount": dashboard_data["max_loan_amount"],
            "loan_summary": {
                "eligibility_score": dashboard_data["eligibility_score"],
                "max_loan_amount": dashboard_data["max_loan_amount"],
            },
            "loans": loans_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
