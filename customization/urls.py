from django.urls import path
from . import views

app_name = 'customization'

urlpatterns = [
    path('new/', views.create_request, name='create'),
    path('mine/', views.my_requests, name='my_requests'),
    path('<int:pk>/', views.request_detail, name='detail'),
    path('<int:pk>/approve/', views.approve_request, name='approve'),

    path('manage/', views.manage_requests, name='manage_list'),
    path('manage/<int:pk>/review/', views.review_request, name='review'),
]
