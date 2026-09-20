from django import forms
from .models import Jewellery, Category, GoldRate


class JewelleryForm(forms.ModelForm):
    class Meta:
        model = Jewellery
        fields = ['category', 'name', 'description', 'weight', 'metal_type', 'making_charge', 'image', 'is_active']


class GoldRateForm(forms.ModelForm):
    class Meta:
        model = GoldRate
        fields = ['metal_type', 'purity', 'rate_per_gram']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
