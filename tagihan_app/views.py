from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime
from .models import Pelanggan, Tagihan, Pembayaran, Lokasi, Paket
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'tagihan/index.html')

'''untuk tampilan dashboard yang menampilkan data ringkasan tagihan, pelanggan, dan pendapatan'''
@login_required
def dashboard(request):
    #data jumlah tagihan per bulan 
    total_pendapatan_bulan_ini = Tagihan.objects.filter(
        periode_bulan__month=timezone.now().month,
        periode_bulan_year=timezone.now().year,
        status='lunas'
    ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan_sum'] or 0

    total_tagihan_bulan_ini = Tagihan.object.filter(
        periode_bulan__month=timezone.now().month,
        periode_bulan_year=timezone.now().year
    ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan_sum'] or 0

    # data jumlah pelanggan berdasarkan status
    pelanggan_aktif = Pelanggan.objects.filter(status='aktif').count()
    pelanggan_belum_lunas = Pelanggan.objects.filter(status='belum_lunas').count()
    pelanggan_suspend = Pelanggan.objects.filter(status='suspend').count()

    # data untuk grafik pendapatan per bulan
    # data untuk grafik pendapatan per lokasi
    # data untuk grafik status pelanggan

    context = {
        'total_pendapatan_bulan_ini': total_pendapatan_bulan_ini,
    }

    return render(request, 'dashboard.html',context)

'''untuk tampilan pelanggan yang menampilkan daftar pelanggan dengan opsi filter dan pencarian'''
@login_required
def daftar_pelanggan(request):
    pelanggan_list = Pelanggan.objects.all()

    context = {
        'pelanggan_list': pelanggan_list,
    }
    return render(request, 'pelanggan/index.html', context)

