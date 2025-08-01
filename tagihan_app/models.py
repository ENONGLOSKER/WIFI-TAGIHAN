# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Paket(models.Model):
    """Model untuk paket internet"""
    JENIS_PAKET_CHOICES = [
        ('device', 'Device'),
        ('pppoe', 'PPPoE'),
    ]
    
    nama = models.CharField(max_length=100)
    jenis_paket = models.CharField(max_length=10, choices=JENIS_PAKET_CHOICES)
    jumlah_device = models.IntegerField(null=True, blank=True)  # Untuk paket device
    kecepatan_mbps = models.IntegerField(null=True, blank=True)  # Untuk paket PPPoE
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nama

class Lokasi(models.Model):
    """Model untuk lokasi pelanggan"""
    nama = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nama

class Pelanggan(models.Model):
    """Model untuk data pelanggan"""
    nama = models.CharField(max_length=200)
    alamat = models.TextField(blank=True, null=True)
    kontak = models.CharField(max_length=50, blank=True, null=True)
    lokasi = models.ForeignKey(Lokasi, on_delete=models.SET_NULL, null=True, blank=True)
    paket = models.ForeignKey(Paket, on_delete=models.SET_NULL, null=True, blank=True)
    username_pppoe = models.CharField(max_length=100, blank=True, null=True)
    tanggal_bergabung = models.DateField(default=timezone.now)
    catatan = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('suspend', 'Suspend'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    
    def __str__(self):
        return self.nama
    
    @property
    def jumlah_device(self):
        """Mengambil jumlah device dari paket jika jenisnya device"""
        if self.paket and self.paket.jenis_paket == 'device':
            return self.paket.jumlah_device
        return None
    
    @property
    def kecepatan_pppoe(self):
        """Mengambil kecepatan dari paket jika jenisnya PPPoE"""
        if self.paket and self.paket.jenis_paket == 'pppoe':
            return self.paket.kecepatan_mbps
        return None

class Tagihan(models.Model):
    """Model untuk tagihan bulanan pelanggan"""
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    tanggal_tagihan = models.DateField(default=timezone.now)
    periode_bulan = models.DateField() 
    jumlah_tagihan = models.DecimalField(max_digits=10, decimal_places=2)
    jumlah_terbayar = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Tambahkan ini
    tanggal_jatuh_tempo = models.DateField()
    
    STATUS_TAGIHAN_CHOICES = [
        ('lunas', 'Lunas'),
        ('belum_lunas', 'Belum Lunas'),
        ('sebagian_terbayar', 'Sebagian Terbayar'), # Tambahkan ini
        ('tertunggak', 'Tertunggak'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_TAGIHAN_CHOICES, default='belum_lunas')
    
    def __str__(self):
        return f"{self.pelanggan.nama} - {self.periode_bulan.strftime('%B %Y')}"

class Pembayaran(models.Model):
    """Model untuk pencatatan pembayaran"""
    tagihan = models.ForeignKey(Tagihan, on_delete=models.CASCADE, null=True, blank=True) # Bisa null jika pembayaran di muka/deposit
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    tanggal_pembayaran = models.DateTimeField(default=timezone.now)
    jumlah_pembayaran = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pembayaran_choices = [
        ('tunai', 'Tunai'),
        ('transfer_bank', 'Transfer Bank'),
        ('ewallet', 'E-Wallet'),
        ('kartu_kredit', 'Kartu Kredit'),
    ]
    metode_pembayaran = models.CharField(max_length=50, choices=metode_pembayaran_choices)
    keterangan = models.TextField(blank=True, null=True)
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', null=True, blank=True) # untuk bukti fisik
    
    def __str__(self):
        return f"Pembayaran {self.pelanggan.nama} - {self.tanggal_pembayaran.strftime('%d-%m-%Y')} - Rp {self.jumlah_pembayaran}"