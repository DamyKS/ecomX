from django.contrib import admin
from .models import Dashboard, Loan, Payment

admin.site.register(Dashboard)
admin.site.register(Loan)
admin.site.register(Payment)
