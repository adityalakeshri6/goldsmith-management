from django.db import models


class Inventory(models.Model):
    class MaterialType(models.TextChoices):
        GOLD = 'gold', 'Gold'
        SILVER = 'silver', 'Silver'
        STONE = 'stone', 'Precious Stone'
        OTHER = 'other', 'Other Raw Material'

    material_name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=MaterialType.choices, default=MaterialType.GOLD)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='grams')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventory'
        ordering = ['type', 'material_name']

    def __str__(self):
        return f"{self.material_name} - {self.quantity} {self.unit}"

    def is_low_stock(self, threshold=50):
        return self.quantity < threshold
