from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from .models import Jewellery, Category, GoldRate
from .forms import JewelleryForm, GoldRateForm, CategoryForm


def jewellery_list(request):
    items = Jewellery.objects.filter(is_active=True).select_related('category')

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        items = items.filter(category_id=category_id)

    context = {
        'items': items,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'catalogue/list.html', context)


def jewellery_detail(request, pk):
    item = get_object_or_404(Jewellery, pk=pk, is_active=True)
    price_breakdown = None
    try:
        price_breakdown = item.estimated_price()
    except ValueError:
        pass
    return render(request, 'catalogue/detail.html', {'item': item, 'price': price_breakdown})


# ---- Goldsmith/admin side ----

@goldsmith_required
def manage_catalogue(request):
    items = Jewellery.objects.all().select_related('category')
    return render(request, 'catalogue/manage_list.html', {'items': items})


@goldsmith_required
def jewellery_create(request):
    if request.method == 'POST':
        form = JewelleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jewellery item added.')
            return redirect('catalogue:manage_list')
    else:
        form = JewelleryForm()
    return render(request, 'catalogue/form.html', {'form': form, 'title': 'Add Jewellery'})


@goldsmith_required
def jewellery_edit(request, pk):
    item = get_object_or_404(Jewellery, pk=pk)
    if request.method == 'POST':
        form = JewelleryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jewellery item updated.')
            return redirect('catalogue:manage_list')
    else:
        form = JewelleryForm(instance=item)
    return render(request, 'catalogue/form.html', {'form': form, 'title': 'Edit Jewellery'})


@goldsmith_required
def jewellery_delete(request, pk):
    item = get_object_or_404(Jewellery, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Jewellery item deleted.')
        return redirect('catalogue:manage_list')
    return render(request, 'catalogue/confirm_delete.html', {'item': item})


@goldsmith_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('catalogue:manage_list')
    else:
        form = CategoryForm()
    return render(request, 'catalogue/form.html', {'form': form, 'title': 'Add Category'})


@goldsmith_required
def gold_rate_list(request):
    rates = GoldRate.objects.all()[:20]
    if request.method == 'POST':
        form = GoldRateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rate updated.')
            return redirect('catalogue:gold_rates')
    else:
        form = GoldRateForm()
    return render(request, 'catalogue/gold_rates.html', {'rates': rates, 'form': form})
