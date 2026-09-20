from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from catalogue.models import Jewellery
from .models import Order
from .forms import OrderStatusForm


@login_required
def place_order(request, jewellery_pk):
    """Order a catalogue (non-custom) item directly."""
    item = get_object_or_404(Jewellery, pk=jewellery_pk, is_active=True)
    if request.method == 'POST':
        try:
            price = item.estimated_price()
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('catalogue:detail', pk=item.pk)
        order = Order.objects.create(
            user=request.user,
            jewellery=item,
            description=item.name,
            total_amount=price['total'],
        )
        messages.success(request, 'Order placed successfully.')
        return redirect('orders:detail', pk=order.pk)
    return redirect('catalogue:detail', pk=item.pk)


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    if request.user.is_goldsmith:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@goldsmith_required
def manage_orders(request):
    orders = Order.objects.select_related('user').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'orders/manage_list.html', {
        'orders': orders,
        'statuses': Order.Status.choices,
        'status_filter': status_filter,
    })


@goldsmith_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated.')
            return redirect('orders:manage_list')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'orders/update_status.html', {'form': form, 'order': order})
