# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime
from .models import Pelanggan, Tagihan, Pembayaran, Lokasi, Paket
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    return render(request,'index.html')

@login_required
def dashboard(request):
    """View untuk halaman dashboard"""
    # Data ringkasan
    total_pendapatan_bulan_ini = Tagihan.objects.filter(
        periode_bulan__month=timezone.now().month,
        periode_bulan__year=timezone.now().year,
        status='lunas'
    ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
    
    total_tagihan_bulan_ini = Tagihan.objects.filter(
        periode_bulan__month=timezone.now().month,
        periode_bulan__year=timezone.now().year
    ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
    
    pelanggan_aktif = Pelanggan.objects.filter(status='aktif').count()
    pelanggan_belum_lunas = Pelanggan.objects.filter(status='belum_lunas').count()
    pelanggan_suspend = Pelanggan.objects.filter(status='suspend').count()
    
    # Data untuk grafik pendapatan per bulan (contoh 6 bulan terakhir)
    pendapatan_per_bulan = []
    labels_bulan = []
    for i in range(5, -1, -1):  # 6 bulan terakhir
        bulan = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
        total = Tagihan.objects.filter(
            periode_bulan__month=bulan.month,
            periode_bulan__year=bulan.year,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        pendapatan_per_bulan.append(float(total))
        labels_bulan.append(bulan.strftime('%b %Y'))
    
    # Data untuk grafik pendapatan per lokasi
    pendapatan_per_lokasi = []
    labels_lokasi = []
    for lokasi in Lokasi.objects.all():
        total_lokasi = Tagihan.objects.filter(
            pelanggan__lokasi=lokasi,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        if total_lokasi > 0:  # Hanya tampilkan lokasi dengan pendapatan
            pendapatan_per_lokasi.append(float(total_lokasi))
            labels_lokasi.append(lokasi.nama)
    
    # Data untuk grafik status pelanggan
    status_counts = [
        Pelanggan.objects.filter(status='aktif').count(),
        Pelanggan.objects.filter(status='belum_lunas').count(),
        Pelanggan.objects.filter(status='suspend').count(),
    ]
    
    # Data tabel pelanggan terbaru/belum lunas
    pelanggan_list = Pelanggan.objects.filter(
        Q(status='belum_lunas') | Q(status='suspend')
    ).order_by('-id')[:10] # 10 terbaru
    
    context = {
        'total_pendapatan_bulan_ini': total_pendapatan_bulan_ini,
        'total_tagihan_bulan_ini': total_tagihan_bulan_ini,
        'pelanggan_aktif': pelanggan_aktif,
        'pelanggan_belum_lunas': pelanggan_belum_lunas,
        'pelanggan_suspend': pelanggan_suspend,
        'pendapatan_per_bulan': pendapatan_per_bulan,
        'labels_bulan': labels_bulan,
        'pendapatan_per_lokasi': pendapatan_per_lokasi,
        'labels_lokasi': labels_lokasi,
        'status_counts': status_counts,
        'pelanggan_list': pelanggan_list,
    }
    
    return render(request, 'dashboard.html', context)

# PELANGGAN /////////////////////////////////////////////////////////////////////////
@login_required
def pelanggan_list(request):
    """View untuk halaman daftar pelanggan"""
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    lokasi_filter = request.GET.get('lokasi')
    
    pelanggan_list = Pelanggan.objects.all()
    
    if query:
        pelanggan_list = pelanggan_list.filter(
            Q(nama__icontains=query) | 
            Q(username_pppoe__icontains=query)
        )
    
    if status_filter:
        pelanggan_list = pelanggan_list.filter(status=status_filter)
        
    if lokasi_filter:
        pelanggan_list = pelanggan_list.filter(lokasi__id=lokasi_filter)
    
    # Untuk filter dropdown
    lokasi_choices = Lokasi.objects.all()

    # untuk pagination
    paginator = Paginator(pelanggan_list, 10)  # 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    lokasi_choices = Lokasi.objects.all()

    
    
    context = {
        'pelanggan_list': page_obj,  # gunakannya untuk looping
        'page_obj': page_obj, # untuk pagination
        'lokasi_choices': lokasi_choices,
        'query': query,
        'status_filter': status_filter,
        'lokasi_filter': lokasi_filter,
    }
    
    return render(request, 'pelanggan/list.html', context)

@login_required
def pelanggan_detail(request, pk):
    """View untuk halaman detail pelanggan"""
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    tagihan_list = Tagihan.objects.filter(pelanggan=pelanggan).order_by('-periode_bulan')
    
    context = {
        'pelanggan': pelanggan,
        'tagihan_list': tagihan_list,
    }
    
    return render(request, 'pelanggan/detail.html', context)

# TAGIHAN //////////////////////////////////////////////////////////////////////////
@login_required
def tagihan_list(request):
    """View untuk halaman daftar tagihan"""
    status_filter = request.GET.get('status')
    bulan_filter = request.GET.get('bulan')
    
    tagihan_list = Tagihan.objects.all().order_by('-periode_bulan', '-tanggal_tagihan')
    
    if status_filter:
        tagihan_list = tagihan_list.filter(status=status_filter)
        
    if bulan_filter:
        try:
            tahun, bulan = map(int, bulan_filter.split('-'))
            tagihan_list = tagihan_list.filter(
                periode_bulan__year=tahun,
                periode_bulan__month=bulan
            )
        except ValueError:
            pass  # Abaikan filter jika format salah
    
    # Untuk filter dropdown
    bulan_choices = Tagihan.objects.dates('periode_bulan', 'month', order='DESC')

    paginator = Paginator(tagihan_list, 10)  # 10 per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tagihan_list': page_obj,
        'page_obj': page_obj,
        'bulan_choices': bulan_choices,
        'status_filter': status_filter,
        'bulan_filter': bulan_filter,
    }
    
    return render(request, 'tagihan/list.html', context)

# PEMBAYARAN ///////////////////////////////////////////////////////////////////////
@login_required
def daftar_pembayaran(request):
    """View untuk halaman daftar pembayaran"""
    # Filter dan pencarian bisa ditambahkan sesuai kebutuhan
    pembayaran_list = Pembayaran.objects.select_related('tagihan__pelanggan').order_by('-tanggal_pembayaran')
    
    context = {
        'pembayaran_list': pembayaran_list,
    }
    
    return render(request, 'daftar_pembayaran.html', context)

# PAKET ///////////////////////////////////////////////////////////////////////////
@login_required
def paket_list(request):
    """View untuk halaman daftar paket"""
    paket_list = Paket.objects.all()
    
    context = {
        'paket_list': paket_list,
    }
    
    return render(request, 'paket/list.html', context)

@login_required
def paket_detail(request, pk):
    """View untuk halaman detail paket"""
    paket = get_object_or_404(Paket, pk=pk)
    
    # Ambil pelanggan yang menggunakan paket ini
    pelanggan_list = paket.pelanggan_set.all()
    
    context = {
        'paket': paket,
        'pelanggan_list': pelanggan_list,
    }
    
    return render(request, 'paket/detail.html', context)

# API Views untuk Chart.js (opsional, jika menggunakan AJAX)
@login_required
def api_pendapatan_per_bulan(request):
    """API endpoint untuk data pendapatan per bulan"""
    data = []
    labels = []
    for i in range(11, -1, -1):  # 12 bulan terakhir
        bulan = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
        total = Tagihan.objects.filter(
            periode_bulan__month=bulan.month,
            periode_bulan__year=bulan.year,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        data.append(float(total))
        labels.append(bulan.strftime('%b %Y'))
    
    return JsonResponse({
        'labels': labels,
        'data': data,
    })

@login_required
def api_pendapatan_per_lokasi(request):
    """API endpoint untuk data pendapatan per lokasi"""
    data = []
    labels = []
    for lokasi in Lokasi.objects.all():
        total = Tagihan.objects.filter(
            pelanggan__lokasi=lokasi,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        if total > 0:
            data.append(float(total))
            labels.append(lokasi.nama)
    
    return JsonResponse({
        'labels': labels,
        'data': data,
    })

@login_required
def api_status_pelanggan(request):
    """API endpoint untuk data status pelanggan"""
    counts = [
        Pelanggan.objects.filter(status='aktif').count(),
        Pelanggan.objects.filter(status='belum_lunas').count(),
        Pelanggan.objects.filter(status='suspend').count(),
    ]
    
    return JsonResponse({
        'labels': ['Aktif', 'Belum Lunas', 'Suspend'],
        'data': counts,
    })