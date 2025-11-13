# forms.py
from django import forms
from .models import Pelanggan, Pembayaran
from django.core.exceptions import ValidationError
from django.utils import timezone

class PelangganForm(forms.ModelForm):
    class Meta:
        model = Pelanggan
        fields = [
            'nama', 'alamat', 'kontak', 'lokasi', 'paket',
            'username_pppoe', 'tanggal_bergabung', 'catatan', 'status'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.TextInput(attrs={'class': 'form-control'}),
            'kontak': forms.TextInput(attrs={'class': 'form-control'}),
            'lokasi': forms.Select(attrs={'class': 'form-select'}),
            'paket': forms.Select(attrs={'class': 'form-select'}),
            'username_pppoe': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_bergabung': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_nama(self):
        nama = self.cleaned_data.get('nama', '').strip()
        if not nama:
            raise ValidationError("Nama wajib diisi.")
        if len(nama) < 3:
            raise ValidationError("Nama minimal 3 karakter.")
        return nama

    def clean_kontak(self):
        kontak = self.cleaned_data.get('kontak', '').strip()
        if not kontak.isdigit():
            raise ValidationError("Kontak hanya boleh berisi angka.")
        if len(kontak) < 10:
            raise ValidationError("Nomor kontak minimal 10 digit.")
        return kontak

    def clean_username_pppoe(self):
        username = self.cleaned_data.get('username_pppoe', '').strip()
        if not username:
            raise ValidationError("Username PPPoE wajib diisi.")
        if Pelanggan.objects.filter(username_pppoe=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Username PPPoE sudah digunakan pelanggan lain.")
        return username

    def clean_tanggal_bergabung(self):
        tanggal = self.cleaned_data.get('tanggal_bergabung')
        if tanggal and tanggal > timezone.now().date():
            raise ValidationError("Tanggal bergabung tidak boleh di masa depan.")
        return tanggal

    def clean(self):
        cleaned_data = super().clean()
        # Tambahkan validasi antar field di sini jika perlu
        return cleaned_data

class PembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = [
            'tagihan', 'pelanggan', 'jumlah_pembayaran', 'tanggal_pembayaran',
            'metode_pembayaran', 'keterangan','bukti_pembayaran'
        ]
        widgets = {
            'tagihan': forms.Select(attrs={'class': 'form-select'}),
            'pelanggan': forms.Select(attrs={'class': 'form-select'}),
            'jumlah_pembayaran': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tanggal_pembayaran': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'metode_pembayaran': forms.Select(attrs={'class': 'form-select'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'bukti_pembayaran': forms.FileInput(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_jumlah_pembayaran(self):
        jumlah = self.cleaned_data.get('jumlah_pembayaran')
        if jumlah is None or jumlah <= 0:
            raise ValidationError("Jumlah pembayaran harus lebih dari 0.")
        return jumlah

    def clean_tanggal_pembayaran(self):
        tanggal = self.cleaned_data.get('tanggal_pembayaran')
        if tanggal:
            # Konversi ke date jika bertipe datetime
            if hasattr(tanggal, 'date'):
                tanggal = tanggal.date()
            if tanggal > timezone.now().date():
                raise ValidationError("Tanggal pembayaran tidak boleh di masa depan.")
        return tanggal

    def clean(self):
        cleaned_data = super().clean()
        # Validasi tambahan antar field jika diperlukan
        return cleaned_data
