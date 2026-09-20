from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class GoldRate(models.Model):
    class MetalType(models.TextChoices):
        GOLD = 'gold', 'Gold'
        SILVER = 'silver', 'Silver'

    metal_type = models.CharField(max_length=10, choices=MetalType.choices, default=MetalType.GOLD)
    purity = models.CharField(max_length=20, default='22K', help_text="e.g. 22K, 24K, 92.5 (silver)")
    rate_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_metal_type_display()} ({self.purity}) - Rs.{self.rate_per_gram}/g on {self.date}"

    @classmethod
    def current_rate(cls, metal_type='gold'):
        """Latest rate for a metal type. Returns None if none has been set yet."""
        return cls.objects.filter(metal_type=metal_type).order_by('-date', '-id').first()


class Jewellery(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jewellery_items')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Weight in grams")
    metal_type = models.CharField(max_length=10, choices=GoldRate.MetalType.choices, default=GoldRate.MetalType.GOLD)
    making_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='jewellery/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Jewellery'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def estimated_price(self):
        return calculate_price(self.weight, self.metal_type, self.making_charge)


GST_PERCENT = 3  # Adjust to your applicable GST slab


def calculate_price(weight_grams, metal_type, making_charge, gst_percent=GST_PERCENT):
    """
    Core pricing formula (slide 10 of the proposal):
        total = (weight * rate_per_gram) + making_charge + GST
    Returns a dict with the breakdown so templates can show it line by line.
    Raises ValueError if no gold/silver rate has been set yet.
    """
    rate = GoldRate.current_rate(metal_type)
    if rate is None:
        raise ValueError(f"No {metal_type} rate has been set yet. Ask the goldsmith to add one.")

    weight_grams = float(weight_grams)
    making_charge = float(making_charge)
    metal_cost = weight_grams * float(rate.rate_per_gram)
    subtotal = metal_cost + making_charge
    gst_amount = subtotal * (gst_percent / 100)
    total = subtotal + gst_amount

    return {
        'rate_per_gram': rate.rate_per_gram,
        'metal_cost': round(metal_cost, 2),
        'making_charge': round(making_charge, 2),
        'gst_percent': gst_percent,
        'gst_amount': round(gst_amount, 2),
        'total': round(total, 2),
    }
