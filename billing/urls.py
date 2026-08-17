from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='cart'),
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/scan/', views.api_scan, name='api_scan'),
    path('api/clear/', views.api_clear, name='api_clear'),
    path('api/remove/', views.api_remove, name='api_remove'),
]