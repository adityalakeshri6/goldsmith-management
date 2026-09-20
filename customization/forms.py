from django import forms
from .models import CustomizationRequest


class CustomizationRequestForm(forms.ModelForm):
    class Meta:
        model = CustomizationRequest
        fields = ['jewellery_type', 'metal_type', 'weight', 'description', 'reference_image']


class GoldsmithReviewForm(forms.ModelForm):
    class Meta:
        model = CustomizationRequest
        fields = ['status', 'goldsmith_making_charge', 'goldsmith_notes']
