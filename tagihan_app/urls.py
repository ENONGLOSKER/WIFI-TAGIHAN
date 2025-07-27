from django.urls import path
from . import views

app_name = 'tagihan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pelanggan/', views.pelanggan_list, name='pelanggan_list'),
    path('pelanggan/<int:pk>/', views.pelanggan_detail, name='pelanggan_detail'),
    path('tagihan/', views.tagihan_list, name='tagihan_list'),
    path('paket/', views.paket_list, name='paket_list'),
]
