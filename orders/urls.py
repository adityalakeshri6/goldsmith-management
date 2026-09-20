from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place/<int:jewellery_pk>/', views.place_order, name='place'),
    path('mine/', views.my_orders, name='my_orders'),
    path('<int:pk>/', views.order_detail, name='detail'),

    path('manage/', views.manage_orders, name='manage_list'),
    path('manage/<int:pk>/status/', views.update_order_status, name='update_status'),
]
