from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from orders.models import Order
from .forms import PaymentForm
from .models import Payment


@goldsmith_required
def record_payment(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            # a fresh payment always starts as pending until reconciled;
            # save() on the model recalculates the order's running total
            payment.status = Payment.Status.PENDING
            payment.save()
            messages.success(request, f'Payment of Rs.{payment.amount} recorded.')
            return redirect('orders:detail', pk=order.pk)
    else:
        form = PaymentForm(initial={'amount': order.remaining_amount})
    return render(request, 'payments/record.html', {'form': form, 'order': order})


@goldsmith_required
def payment_list(request):
    payments = Payment.objects.select_related('order', 'order__user').all()
    return render(request, 'payments/list.html', {'payments': payments})
