from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from orders.models import Order
from . import gateway
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


@login_required
def pay_online(request, order_pk):
    """Customer-facing: starts a Razorpay Checkout for the order's remaining balance."""
    order = get_object_or_404(Order, pk=order_pk, user=request.user)

    if not gateway.is_configured():
        messages.info(request, 'Online payment is not set up yet — please pay the goldsmith directly.')
        return redirect('orders:detail', pk=order.pk)

    if order.remaining_amount <= 0:
        messages.info(request, 'This order is already fully paid.')
        return redirect('orders:detail', pk=order.pk)

    razorpay_order = gateway.create_razorpay_order(
        amount_rupees=order.remaining_amount,
        receipt=f"order-{order.pk}",
    )

    context = {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'amount_paise': razorpay_order['amount'],
        'business_name': settings.BUSINESS_NAME,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def verify_online_payment(request, order_pk):
    """
    Called by the browser after Razorpay Checkout reports success. We do NOT
    trust that message on its own — we re-verify the signature server-side
    before creating a Payment record. This is the only place a Payment
    should ever be created from an online transaction.
    """
    order = get_object_or_404(Order, pk=order_pk, user=request.user)

    if request.method != 'POST':
        return redirect('orders:detail', pk=order.pk)

    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    verified = gateway.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    if not verified:
        messages.error(request, 'Payment verification failed. If money was deducted, contact the shop — do not retry blindly.')
        return redirect('orders:detail', pk=order.pk)

    amount_paid = order.remaining_amount
    Payment.objects.create(
        order=order,
        amount=amount_paid,
        status=Payment.Status.PAID,
        notes=f"Online payment via Razorpay (payment_id={razorpay_payment_id})",
    )
    messages.success(request, 'Payment successful! Thank you.')
    return redirect('orders:detail', pk=order.pk)
