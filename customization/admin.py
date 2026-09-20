from django.contrib import admin
from .models import CustomizationRequest


@admin.register(CustomizationRequest)
class CustomizationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'jewellery_type', 'weight', 'status', 'created_at')
    list_filter = ('status', 'metal_type')
