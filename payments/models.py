from django.db import models
from orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIALLY_PAID = 'partially_paid', 'Partially Paid'
        PAID = 'paid', 'Paid'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of Rs.{self.amount} for Order #{self.order_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_order_status()

    def _update_order_status(self):
        order = self.order
        total_paid = order.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        order.advance_payment = total_paid
        if total_paid <= 0:
            pass
        elif total_paid >= order.total_amount:
            if order.status not in (Order.Status.DELIVERED, Order.Status.CANCELLED):
                order.status = Order.Status.ADVANCE_PAID if order.status == Order.Status.PLACED else order.status
        order.save()

    @property
    def order_payment_status(self):
        total_paid = self.order.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        if total_paid <= 0:
            return Payment.Status.PENDING
        elif total_paid >= self.order.total_amount:
            return Payment.Status.PAID
        return Payment.Status.PARTIALLY_PAID
