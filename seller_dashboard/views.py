# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import get_object_or_404
# from django.db.models import Sum
# from datetime import timedelta

# from .models import Dashboard, Loan, Payment
# from .serializers import DashboardSerializer, LoanSerializer, PaymentSerializer


# class DashboardView(APIView):
#     """
#     GET /api/v1/dashboard/
#     Returns dashboard metrics + loan details for the logged-in user.
#     """

#     def get(self, request):
#         user = request.user

#         # 1) Fetch the user's dashboard
#         dashboard = get_object_or_404(Dashboard, owner=user)
#         dashboard_data = DashboardSerializer(dashboard).data

#         # 2) Retrieve the user's loans
#         loans = Loan.objects.filter(borrower=user)

#         # 3) Build loan-specific data
#         loans_data = []
#         for loan in loans:
#             # All payments for this loan, sorted by date
#             payments = loan.payments.order_by("payment_date")

#             # Total amount paid so far
#             total_paid = payments.aggregate(Sum("amount"))["amount__sum"] or 0

#             # Number of payments made
#             payments_made = payments.count()
#             payments_remaining = loan.term_months - payments_made

#             # Last payment date (if any)
#             last_payment_date = (
#                 payments.last().payment_date if payments.exists() else None
#             )

#             # Compute next payment date: last payment date + 30 days
#             if last_payment_date:
#                 next_payment_date = last_payment_date + timedelta(days=30)
#             else:
#                 # If no payments yet, next payment is 30 days from start_date
#                 next_payment_date = loan.start_date + timedelta(days=30)

#             loans_data.append(
#                 {
#                     "loan_id": loan.loan_id,
#                     "loan_type": loan.loan_type,
#                     "amount": str(loan.amount),
#                     "interest_rate": loan.interest_rate,
#                     "term_months": loan.term_months,
#                     "start_date": str(loan.start_date),
#                     "end_date": str(loan.end_date),
#                     "status": loan.status,
#                     "payment_status": loan.payment_status,
#                     "total_paid": str(total_paid),
#                     "payments_made": payments_made,
#                     "payments_remaining": payments_remaining,
#                     "next_payment_date": str(next_payment_date),
#                 }
#             )

#         # 4) Combine dashboard data + loans data into a single response
#         response_data = {
#             "total_revenue": float(dashboard_data["total_revenue"]),
#             "new_customers": dashboard_data["new_customers"],
#             "total_orders": dashboard_data["total_orders"],
#             "max_loan_amount": dashboard_data["max_loan_amount"],
#             "loan_summary": {
#                 "eligibility_score": dashboard_data["eligibility_score"],
#                 "max_loan_amount": dashboard_data["max_loan_amount"],
#             },
#             "loans": loans_data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import timedelta
from .models import Dashboard, Loan, Payment
from .serializers import DashboardSerializer


class DashboardView(APIView):
    """
    GET /api/v1/dashboard/
    Returns a JSON response with dashboard metrics, details of the user's active loan,
    and payment status/history based on monthly repayments.
    """

    def get(self, request):
        user = request.user

        # 1) Get the user's dashboard record
        dashboard = get_object_or_404(Dashboard, owner=user)
        dashboard_data = DashboardSerializer(dashboard).data

        # 2) Retrieve the user's single active loan (if any)
        active_loan = Loan.objects.filter(borrower=user, status="active").first()

        if active_loan:
            # Retrieve payments for the active loan, ordered by payment_date
            payments = active_loan.payments.order_by("payment_date")
            if payments.exists():
                last_payment_date = payments.last().payment_date
                next_payment_date = last_payment_date + timedelta(days=30)
            else:
                next_payment_date = active_loan.start_date + timedelta(days=30)

            # Calculate monthly payment
            monthly_payment = float(active_loan.amount) / active_loan.term_months

            # Total paid for this loan
            total_paid = payments.aggregate(total_paid=Sum("amount"))["total_paid"] or 0

            # Build payment history for the active loan
            payment_history = []
            for payment in payments.order_by("payment_date"):
                payment_history.append(
                    {
                        "amount": float(payment.amount),
                        "payment_date": payment.payment_date.isoformat(),
                    }
                )

            loan_summary = {
                "loan_id": active_loan.loan_id,
                "loan_type": active_loan.loan_type,
                "amount": float(active_loan.amount),
                "interest_rate": active_loan.interest_rate,
                "term_months": active_loan.term_months,
                "start_date": active_loan.start_date.isoformat(),
                "end_date": active_loan.end_date.isoformat(),
                "status": active_loan.status,
                "payment_status": active_loan.payment_status,
            }

            payment_status = {
                "next_payment_due": next_payment_date.isoformat(),
                "repayment_progress": {
                    "paid": round(float(total_paid), 2),
                    "total": round(float(monthly_payment), 2),
                },
            }
        else:
            loan_summary = None
            payment_status = None
            payment_history = []

        # 3) Build the final response data
        response_data = {
            "total_revenue": float(dashboard_data["total_revenue"]),
            "new_customers": dashboard_data["new_customers"],
            "total_orders": dashboard_data["total_orders"],
            "loan_eligibility": dashboard_data["max_loan_amount"],
            "loan_summary": loan_summary,
            "payment_status": payment_status,
            "payment_history": payment_history,
        }

        return Response(response_data, status=status.HTTP_200_OK)
