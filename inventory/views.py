from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from .models import Inventory
from .forms import InventoryForm, StockAdjustForm


@goldsmith_required
def inventory_list(request):
    items = Inventory.objects.all()
    return render(request, 'inventory/list.html', {'items': items})


@goldsmith_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material added to inventory.')
            return redirect('inventory:list')
    else:
        form = InventoryForm()
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Material'})


@goldsmith_required
def inventory_adjust(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = StockAdjustForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if form.cleaned_data['action'] == 'add':
                item.quantity += amount
            else:
                item.quantity = max(Decimal('0'), item.quantity - amount)
            item.save()
            messages.success(request, f'{item.material_name} stock updated.')
            return redirect('inventory:list')
    else:
        form = StockAdjustForm()
    return render(request, 'inventory/adjust.html', {'form': form, 'item': item})
