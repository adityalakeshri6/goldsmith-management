from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import goldsmith_required
from orders.models import Order
from .models import CustomizationRequest
from .forms import CustomizationRequestForm, GoldsmithReviewForm


@login_required
def create_request(request):
    if request.method == 'POST':
        form = CustomizationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.save()
            messages.success(request, 'Your customization request has been submitted.')
            return redirect('customization:my_requests')
    else:
        form = CustomizationRequestForm()
    return render(request, 'customization/create.html', {'form': form})


@login_required
def my_requests(request):
    requests_qs = CustomizationRequest.objects.filter(user=request.user)
    return render(request, 'customization/my_requests.html', {'requests': requests_qs})


@login_required
def request_detail(request, pk):
    if request.user.is_goldsmith:
        req = get_object_or_404(CustomizationRequest, pk=pk)
    else:
        req = get_object_or_404(CustomizationRequest, pk=pk, user=request.user)
    return render(request, 'customization/detail.html', {'req': req, 'price': req.estimated_price()})


@login_required
def approve_request(request, pk):
    """Customer approves a reviewed request -> creates an Order."""
    req = get_object_or_404(CustomizationRequest, pk=pk, user=request.user, status=CustomizationRequest.Status.REVIEWED)
    if request.method == 'POST':
        price = req.estimated_price()
        order = Order.objects.create(
            user=request.user,
            custom_request=req,
            description=f"Custom {req.jewellery_type} - {req.description[:100]}",
            total_amount=price['total'] if price else 0,
        )
        req.status = CustomizationRequest.Status.APPROVED
        req.save()
        messages.success(request, 'Design approved! Your order has been created.')
        return redirect('orders:detail', pk=order.pk)
    return render(request, 'customization/approve_confirm.html', {'req': req})


# ---- Goldsmith side ----

@goldsmith_required
def manage_requests(request):
    requests_qs = CustomizationRequest.objects.all()
    return render(request, 'customization/manage_list.html', {'requests': requests_qs})


@goldsmith_required
def review_request(request, pk):
    req = get_object_or_404(CustomizationRequest, pk=pk)
    if request.method == 'POST':
        form = GoldsmithReviewForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Request updated.')
            return redirect('customization:manage_list')
    else:
        form = GoldsmithReviewForm(instance=req)
    return render(request, 'customization/review.html', {'form': form, 'req': req})
