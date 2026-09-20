from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('add/', views.inventory_create, name='create'),
    path('<int:pk>/adjust/', views.inventory_adjust, name='adjust'),
]
