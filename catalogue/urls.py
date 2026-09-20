from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.jewellery_list, name='list'),
    path('<int:pk>/', views.jewellery_detail, name='detail'),

    path('manage/', views.manage_catalogue, name='manage_list'),
    path('manage/add/', views.jewellery_create, name='create'),
    path('manage/<int:pk>/edit/', views.jewellery_edit, name='edit'),
    path('manage/<int:pk>/delete/', views.jewellery_delete, name='delete'),
    path('manage/category/add/', views.category_create, name='category_create'),
    path('manage/gold-rates/', views.gold_rate_list, name='gold_rates'),
]
