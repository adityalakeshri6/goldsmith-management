from django.contrib import admin
from .models import Category, Jewellery, GoldRate

admin.site.register(Category)
admin.site.register(GoldRate)


@admin.register(Jewellery)
class JewelleryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'weight', 'metal_type', 'making_charge', 'is_active')
    list_filter = ('category', 'metal_type', 'is_active')
    search_fields = ('name', 'description')
