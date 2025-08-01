from django.urls import path
from . import views

app_name = 'tagihan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pelanggan/', views.pelanggan_list, name='pelanggan_list'),
    path('pelanggan/<int:pk>/', views.pelanggan_detail, name='pelanggan_detail'),
    path('tagihan/', views.tagihan_list, name='tagihan_list'),
    path('tagihan/<int:pk>/', views.tagihan_detail, name='tagihan_detail'),
    path('paket/', views.paket_list, name='paket_list'),
    path('paket/<int:pk>/', views.paket_detail, name='paket_detail'),
    path('pembayaran/', views.pembayaran_list, name='pembayaran_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('laporan/', views.laporan_view, name='laporan')
]
