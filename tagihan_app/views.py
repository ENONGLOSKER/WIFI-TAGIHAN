from re import S
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from typing import Dict, List, Optional
from uuid import UUID
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime
from .models import Tagihan, Pembayaran, Pelanggan, Paket, Lokasi
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractYear
from datetime import datetime, timedelta
from .forms import PelangganForm, PembayaranForm
from decimal import Decimal

# Constants
ITEMS_PER_PAGE = 10
RECENT_CUSTOMERS_LIMIT = 10
MONTHS_FOR_REPORT = 6

def calculate_summary_stats() -> Dict[str, float]:
    """Calculate summary statistics for billing and payments."""
    tagihan_agg = Tagihan.objects.aggregate(
        total_tagihan=Sum('jumlah_tagihan'),
        total_terbayar=Sum('jumlah_terbayar')
    )
    total_pembayaran = Pembayaran.objects.aggregate(total=Sum('jumlah_pembayaran'))['total'] or 0

    # pelanggan akftif, tidak aktif, suspend
    pelanggan_aktif = Pelanggan.objects.filter(status='aktif').count()
    pelanggan_belum_lunas = Pelanggan.objects.filter(status='tidak_aktif').count
    pelanggan_suspend = Pelanggan.objects.filter(status='suspend').count()
    
    return {
        'total_tagihan': tagihan_agg['total_tagihan'] or 0,
        'total_terbayar': tagihan_agg['total_terbayar'] or 0,
        'total_belum_lunas': tagihan_agg['total_tagihan'] - tagihan_agg['total_terbayar'] if tagihan_agg['total_tagihan'] else 0,
        'total_pembayaran': total_pembayaran,
        'jumlah_tagihan': Tagihan.objects.count(),
        'jumlah_pembayaran': Pembayaran.objects.count(),
        'jumlah_belum_lunas': Tagihan.objects.filter(status='belum_lunas').count(),
        'total_pelanggan': Pelanggan.objects.all().count(),
        'pelanggan_aktif': pelanggan_aktif,
        'pelanggan_tidak_aktif': pelanggan_belum_lunas,
        'pelanggan_suspend': pelanggan_suspend,
    }

def get_monthly_revenue_data(months: int = MONTHS_FOR_REPORT) -> tuple[List[float], List[str]]:
    """Get revenue data for the last specified months."""
    pendapatan_per_bulan = []
    labels_bulan = []
    
    for i in range(months - 1, -1, -1):
        bulan = timezone.now().replace(day=1) - timezone.timedelta(days=30 * i)
        total = Tagihan.objects.filter(
            periode_bulan__month=bulan.month,
            periode_bulan__year=bulan.year,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        pendapatan_per_bulan.append(float(total))
        labels_bulan.append(bulan.strftime('%b %Y'))
    
    return pendapatan_per_bulan, labels_bulan

def get_location_revenue_data() -> tuple[List[float], List[str]]:
    """Get revenue data by location."""
    pendapatan_per_lokasi = []
    labels_lokasi = []
    
    for lokasi in Lokasi.objects.all():
        total = Tagihan.objects.filter(
            pelanggan__lokasi=lokasi,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0
        
        if total > 0:
            pendapatan_per_lokasi.append(float(total))
            labels_lokasi.append(lokasi.nama)
    
    return pendapatan_per_lokasi, labels_lokasi

def index(request):
    """Render the index page."""
    return render(request, 'index.html')

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Username dan password harus diisi.')
            return render(request, 'auth/login.html')
            
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login berhasil!')
            return redirect('tagihan_app:dashboard')
            
        messages.error(request, 'Username atau password salah.')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logout berhasil.')
    return redirect('tagihan_app:index')

@login_required
def dashboard(request):
    """Render the dashboard with summary statistics."""
    current_month = timezone.now().month
    current_year = timezone.now().year

    total_pelanggan = calculate_summary_stats()

    tagihan_history = Tagihan.objects.select_related('pelanggan').order_by('status','-periode_bulan')[:7]

    # grafik
        # === Pendapatan per bulan ===
    payments_by_month = (
        Pembayaran.objects
        .annotate(month=TruncMonth('tanggal_pembayaran'))
        .values('month')
        .annotate(total=Sum('jumlah_pembayaran'))
        .order_by('month')
    )
    monthly_labels = [p['month'].strftime('%b %Y') for p in payments_by_month]
    monthly_totals = [int(p['total']) for p in payments_by_month]

    # === Pendapatan per lokasi ===
    payments_by_location = (
        Pembayaran.objects
        .values('pelanggan__lokasi__nama')
        .annotate(total=Sum('jumlah_pembayaran'))
        .order_by('pelanggan__lokasi__nama')
    )
    lokasi_labels = [p['pelanggan__lokasi__nama'] or "Tidak Diketahui" for p in payments_by_location]
    lokasi_totals = [int(p['total']) for p in payments_by_location]

    # === Status Pelanggan ===
    status_data = [
        Pelanggan.objects.filter(status='aktif').count(),
        Pelanggan.objects.filter(status='tidak_aktif').count(),
        Pelanggan.objects.filter(status='suspend').count()
    ]

    tahun_filter = request.GET.get('tahun', '')
    
    # Filter berdasarkan tahun terakhir
    if tahun_filter and tahun_filter.isdigit():
        tahun_mulai = datetime.now().year - int(tahun_filter) + 1
        payments_by_year = (
            Pembayaran.objects
            .annotate(year=ExtractYear('tanggal_pembayaran'))
            .filter(tanggal_pembayaran__year__gte=tahun_mulai)
            .values('year')
            .annotate(total=Sum('jumlah_pembayaran'))
            .order_by('year')
        )
    else:
        payments_by_year = (
            Pembayaran.objects
            .annotate(year=ExtractYear('tanggal_pembayaran'))
            .values('year')
            .annotate(total=Sum('jumlah_pembayaran'))
            .order_by('year')
        )

    year_labels = [str(p['year']) for p in payments_by_year]
    year_totals = [int(p['total']) for p in payments_by_year]

    
    context = {
        'total_pendapatan_bulan_ini': Tagihan.objects.filter(
            periode_bulan__month=current_month,
            periode_bulan__year=current_year,
            status='lunas'
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0,
        'total_tagihan_bulan_ini': Tagihan.objects.filter(
            periode_bulan__month=current_month,
            periode_bulan__year=current_year
        ).aggregate(Sum('jumlah_tagihan'))['jumlah_tagihan__sum'] or 0,
        'pelanggan_aktif': Pelanggan.objects.filter(status='aktif').count(),
        'pelanggan_belum_lunas': Pelanggan.objects.filter(status='belum_lunas').count(),
        'pelanggan_suspend': Pelanggan.objects.filter(status='suspend').count(),
        'pendapatan_per_bulan': get_monthly_revenue_data()[0],
        'labels_bulan': get_monthly_revenue_data()[1],
        'pendapatan_per_lokasi': get_location_revenue_data()[0],
        'labels_lokasi': get_location_revenue_data()[1],
        'status_counts': [
            Pelanggan.objects.filter(status='aktif').count(),
            Pelanggan.objects.filter(status='belum_lunas').count(),
            Pelanggan.objects.filter(status='suspend').count(),
        ],
        'pelanggan_list': Pelanggan.objects.filter(
            Q(status='belum_lunas') | Q(status='suspend')
        ).order_by('-id')[:RECENT_CUSTOMERS_LIMIT],
        **total_pelanggan,
        'tagihan_history': tagihan_history,
        # grafik
        "monthly_labels": monthly_labels,
        "monthly_totals": monthly_totals,
        "lokasi_labels": lokasi_labels,
        "lokasi_totals": lokasi_totals,
        "status_data": status_data,
        "year_labels": year_labels,
        "year_totals": year_totals,
        "tahun_filter": tahun_filter,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def pelanggan_list(request):
    """Render the customer list with filtering and pagination."""
    pelanggan_list = Pelanggan.objects.select_related('lokasi').all()
    
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    lokasi_filter = request.GET.get('lokasi', '')
    
    if query:
        pelanggan_list = pelanggan_list.filter(
            Q(nama__icontains=query) | 
            Q(username_pppoe__icontains=query)
        )
    
    if status_filter:
        pelanggan_list = pelanggan_list.filter(status=status_filter)
        
    if lokasi_filter:
        pelanggan_list = pelanggan_list.filter(lokasi__id=lokasi_filter)
    
    paginator = Paginator(pelanggan_list, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    sumary_states = calculate_summary_stats()
    
    context = {
        'pelanggan_list': page_obj,
        'page_obj': page_obj,
        'lokasi_choices': Lokasi.objects.all(),
        'query': query,
        'status_filter': status_filter,
        'lokasi_filter': lokasi_filter,
        **sumary_states,
    }
    
    return render(request, 'pelanggan/list.html', context)

@login_required
def pelanggan_detail(request, pk: UUID):
    """Render customer detail page."""
    pelanggan = get_object_or_404(Pelanggan.objects.select_related('lokasi', 'paket'), pk=pk)
    summary_stats = calculate_summary_stats()

    # Ambil semua tagihan pelanggan
    tagihan_list = Tagihan.objects.filter(pelanggan=pelanggan).order_by('-periode_bulan')
    # Ambil semua pembayaran yang terkait dengan tagihan pelanggan
    pembayaran_list = Pembayaran.objects.filter(tagihan__in=tagihan_list).order_by('-tanggal_pembayaran')

    context = {
        'pelanggan': pelanggan,
        'tagihan_list': tagihan_list,
        'pembayaran_list': pembayaran_list,
        **summary_stats,
    }

    return render(request, 'pelanggan/detail.html', context)

@login_required
def pelanggan_add(request):
    if request.method == 'POST':
        form = PelangganForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pelanggan Berhasil ditambahkan.")
            return redirect('tagihan_app:pelanggan_list') 
    else:
        messages.error(request, "Pelanggan Gagal ditambahkan.")
        form = PelangganForm()
    
    context = {
        'form': form,
        'title': 'Tambah Pelanggan',
    }
    
    return render(request, 'form/form.html', context)

@login_required
def pelanggan_update(request, pk):
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    if request.method == 'POST':
        form = PelangganForm(request.POST, instance=pelanggan)
        if form.is_valid():
            form.save()
            messages.success(request, "Pelanggan berhasil diupdate.")
            return redirect('tagihan_app:pelanggan_list')
        else:
            messages.error(request, "Gagal update pelanggan. Silakan cek data Anda.")
    else:
        form = PelangganForm(instance=pelanggan)
    context = {
        'form': form,
        'title': 'Edit Pelanggan',
        'pelanggan': pelanggan,
    }
    return render(request, 'form/form.html', context)

@login_required
def pelanggan_delete(request, pk):
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    pelanggan.delete()
    messages.success(request, "Pelanggan berhasil dihapus.")
    return redirect('tagihan_app:pelanggan_list')

@login_required
def paket_list(request):
    """Render package list page."""
    context = {
        'paket_list': Paket.objects.all(),
    }
    return render(request, 'paket/list.html', context)

@login_required
def paket_detail(request, pk: UUID):
    """Render package detail page."""
    paket = get_object_or_404(Paket, pk=pk)
    context = {
        'paket': paket,
        'pelanggan_list': paket.pelanggan_set.select_related('lokasi').all(),
    }
    return render(request, 'paket/detail.html', context)

@login_required
def tagihan_list(request):
    """Render billing list with filtering and pagination."""
    tagihan_list = Tagihan.objects.select_related('pelanggan__paket', 'pelanggan__lokasi').order_by('status', '-periode_bulan')
    
    status_filter = request.GET.get('status', '')
    bulan_filter = request.GET.get('bulan', '')
    
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
            messages.error(request, 'Format bulan tidak valid.')
    
    paginator = Paginator(tagihan_list, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    summary_stats = calculate_summary_stats()
    
    context = {
        'tagihan_list': page_obj,
        'page_obj': page_obj,
        'bulan_choices': Tagihan.objects.dates('periode_bulan', 'month', order='DESC'),
        'status_filter': status_filter,
        'bulan_filter': bulan_filter,
        **summary_stats,
    }
    
    return render(request, 'tagihan/list.html', context)

@login_required
def tagihan_detail(request, pk: UUID):
    """Render billing detail page."""
    tagihan = get_object_or_404(
        Tagihan.objects.select_related('pelanggan__paket', 'pelanggan__lokasi'),
        pk=pk
    )
    summary_stats = calculate_summary_stats()
    context = {
        'tagihan': tagihan,
        'pembayaran': Pembayaran.objects.filter(tagihan=tagihan).order_by('-tanggal_pembayaran'),
        **summary_stats,
    }
    return render(request, 'tagihan/detail.html', context)

@login_required
def pembayaran_list(request):
    """Render payment list with filtering and pagination."""
    pembayaran_list = Pembayaran.objects.select_related('pelanggan', 'tagihan').all()
    
    query = request.GET.get('q', '').strip()
    metode_filter = request.GET.get('metode', '')
    tanggal_filter = request.GET.get('tanggal', '')
    
    if query:
        pembayaran_list = pembayaran_list.filter(pelanggan__nama__icontains=query)
    
    if metode_filter:
        pembayaran_list = pembayaran_list.filter(metode_pembayaran=metode_filter)
    
    if tanggal_filter:
        try:
            pembayaran_list = pembayaran_list.filter(tanggal_pembayaran__date=tanggal_filter)
        except ValueError:
            messages.error(request, 'Format tanggal tidak valid.')
    
    paginator = Paginator(pembayaran_list, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    summary_stats = calculate_summary_stats()
    
    context = {
        'pembayaran_list': page_obj,
        'page_obj': page_obj,
        'query': query,
        'metode_filter': metode_filter,
        'tanggal_filter': tanggal_filter,
        **summary_stats,
    }
    
    return render(request, 'pembayaran/list.html', context)

@login_required
def bayar_tagihan(request, tagihan_id):
    tagihan = get_object_or_404(Tagihan, id=tagihan_id)
    
    if request.method == 'POST':
        jumlah = Decimal(request.POST.get('jumlah_pembayaran'))
        metode = request.POST.get('metode_pembayaran')
        keterangan = request.POST.get('keterangan', '')
        bukti = request.FILES.get('bukti_pembayaran')  # jika upload bukti

        # Buat pembayaran baru
        pembayaran = Pembayaran.objects.create(
            tagihan=tagihan,
            pelanggan=tagihan.pelanggan,
            jumlah_pembayaran=jumlah,
            metode_pembayaran=metode,
            keterangan=keterangan,
            bukti_pembayaran=bukti,
            tanggal_pembayaran=timezone.now()
        )

        # Update tagihan
        tagihan.jumlah_terbayar += jumlah

        if tagihan.jumlah_terbayar >= tagihan.jumlah_tagihan:
            tagihan.status = 'lunas'
        elif 0 < tagihan.jumlah_terbayar < tagihan.jumlah_tagihan:
            tagihan.status = 'sebagian_terbayar'
        else:
            tagihan.status = 'belum_lunas'

        tagihan.save()

        messages.success(request, "Pembayaran berhasil dicatat.")
        return redirect('tagihan_app:pembayaran_list')

    return render(request, 'form/pembayaran.html', {'tagihan': tagihan})

@login_required
def pembayaran_update(request, pk):
    pembayaran = get_object_or_404(Pembayaran, pk=pk)
    if request.method == 'POST':
        form = PembayaranForm(request.POST, instance=pembayaran)
        if form.is_valid():
            form.save()
            messages.success(request, "Pembayaran berhasil diupdate.")
            return redirect('tagihan_app:pembayaran_list')
        else:
            messages.error(request, "Gagal update pembayaran. Silakan cek data Anda.")
    else:
        form = PembayaranForm(instance=pembayaran)
    context = {
        'form': form,
        'title': 'Edit Pembayaran',
        'pembayaran': pembayaran,
    }
    return render(request, 'form/form.html', context)

@login_required
def pembayaran_delete(request, pk):
    pembayaran = get_object_or_404(Pembayaran, pk=pk)
    pembayaran.delete()
    messages.success(request, "Pembayaran berhasil dihapus.")
    return redirect('tagihan_app:pembayaran_list')

@login_required
def laporan_view(request):
    """Render report page with summary statistics."""
    context = calculate_summary_stats()
    return render(request, 'laporan/list.html', context)