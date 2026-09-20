from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('order/<int:order_pk>/record/', views.record_payment, name='record'),
    path('manage/', views.payment_list, name='list'),
]
