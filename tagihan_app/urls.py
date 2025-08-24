from django.urls import path
from . import views

app_name = 'tagihan_app'

urlpatterns = [
    # authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('laporan/', views.laporan_view, name='laporan'),
    # Home
    path('', views.index, name='index'),
    # dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # paket
    path('paket/', views.paket_list, name='paket_list'),
    path('paket/<int:pk>/', views.paket_detail, name='paket_detail'),
    # pelanggan
    path('pelanggan/', views.pelanggan_list, name='pelanggan_list'),
    path('pelanggan/<int:pk>/', views.pelanggan_detail, name='pelanggan_detail'),
    path('pelanggan/add/', views.pelanggan_add, name='pelanggan_add'),
    path('pelanggan/edit/<int:pk>/', views.pelanggan_update, name='pelanggan_update'),
    path('pelanggan/delete/<int:pk>/', views.pelanggan_delete, name='pelanggan_delete'),
    # pembayaran
    path('pembayaran/', views.pembayaran_list, name='pembayaran_list'),
    path('tagihan/<int:tagihan_id>/bayar/', views.bayar_tagihan, name='pembayaran_add'),
    path('pembayaran/edit/<int:pk>/', views.pembayaran_update, name='pembayaran_update'),
    path('pembayaran/delete/<int:pk>/', views.pembayaran_delete, name='pembayaran_delete'),
    # tagihan
    path('tagihan/', views.tagihan_list, name='tagihan_list'),
    path('tagihan/<int:pk>/', views.tagihan_detail, name='tagihan_detail'),
    # laporan
    path('laporan/', views.laporan_view, name='laporan_list'),
    path('laporan/cetak/', views.laporan_cetak, name='laporan_cetak'),

    
]
