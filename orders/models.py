from django.conf import settings
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = 'placed', 'Order Placed'
        ADVANCE_PAID = 'advance_paid', 'Advance Paid'
        IN_PRODUCTION = 'in_production', 'In Production'
        READY = 'ready', 'Jewellery Ready'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    jewellery = models.ForeignKey('catalogue.Jewellery', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    custom_request = models.ForeignKey('customization.CustomizationRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    description = models.CharField(max_length=255, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)

    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.pk} - {self.user} - {self.status}"

    @property
    def remaining_amount(self):
        return self.total_amount - self.advance_payment

    @property
    def item_name(self):
        if self.jewellery:
            return self.jewellery.name
        return self.description or "Custom order"
