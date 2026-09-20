from django.conf import settings
from django.db import models
from catalogue.models import GoldRate, calculate_price


class CustomizationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        REVIEWED = 'reviewed', 'Reviewed - Price Estimated'
        APPROVED = 'approved', 'Approved by Customer'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customization_requests')
    jewellery_type = models.CharField(max_length=100, help_text="e.g. Ring, Necklace, Bangle")
    metal_type = models.CharField(max_length=10, choices=GoldRate.MetalType.choices, default=GoldRate.MetalType.GOLD)
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Requested weight in grams")
    description = models.TextField(help_text="Design description / requirements")
    reference_image = models.ImageField(upload_to='customization_refs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    goldsmith_making_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    goldsmith_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.jewellery_type} request by {self.user} ({self.status})"

    def estimated_price(self):
        if self.goldsmith_making_charge is None:
            return None
        try:
            return calculate_price(self.weight, self.metal_type, self.goldsmith_making_charge)
        except ValueError:
            return None
