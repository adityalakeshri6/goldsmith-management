from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item_name', 'total_amount', 'advance_payment', 'status', 'order_date')
    list_filter = ('status',)
