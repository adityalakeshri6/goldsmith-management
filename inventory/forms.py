from django import forms
from .models import Inventory


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['material_name', 'type', 'quantity', 'unit']


class StockAdjustForm(forms.Form):
    ACTION_CHOICES = (('add', 'Add stock'), ('use', 'Use / deduct stock'))
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    amount = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2)
