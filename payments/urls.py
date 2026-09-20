from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('order/<int:order_pk>/record/', views.record_payment, name='record'),
    path('order/<int:order_pk>/pay/', views.pay_online, name='pay_online'),
    path('order/<int:order_pk>/pay/verify/', views.verify_online_payment, name='verify_online'),
    path('manage/', views.payment_list, name='list'),
]
