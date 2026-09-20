from django.contrib import admin
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('material_name', 'type', 'quantity', 'unit', 'last_updated')
    list_filter = ('type',)
