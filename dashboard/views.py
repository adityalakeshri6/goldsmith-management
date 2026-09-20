import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from accounts.decorators import goldsmith_required
from orders.models import Order
from customization.models import CustomizationRequest
from inventory.models import Inventory


@login_required
def home(request):
    if request.user.is_goldsmith:
        return goldsmith_dashboard(request)
    return customer_dashboard(request)


def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]
    requests_qs = CustomizationRequest.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'dashboard/customer_home.html', {
        'orders': orders,
        'requests': requests_qs,
    })


@goldsmith_required
def goldsmith_dashboard(request):
    total_orders = Order.objects.count()
    pending_requests = CustomizationRequest.objects.filter(status=CustomizationRequest.Status.PENDING).count()
    total_sales = Order.objects.exclude(status=Order.Status.CANCELLED).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    low_stock = [i for i in Inventory.objects.all() if i.is_low_stock()]

    sales_by_month = (
        Order.objects.exclude(status=Order.Status.CANCELLED)
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    chart_labels = [s['month'].strftime('%b %Y') for s in sales_by_month]
    chart_values = [float(s['total']) for s in sales_by_month]

    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    status_labels = [dict(Order.Status.choices)[s['status']] for s in status_counts]
    status_values = [s['count'] for s in status_counts]

    return render(request, 'dashboard/goldsmith_home.html', {
        'total_orders': total_orders,
        'pending_requests': pending_requests,
        'total_sales': total_sales,
        'low_stock': low_stock,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'status_labels': json.dumps(status_labels),
        'status_values': json.dumps(status_values),
    })
