from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tagihan_app.models import Pelanggan, Tagihan # Pastikan Anda mengimpor models dari aplikasi Anda

class Command(BaseCommand):
    """
    Management Command untuk membuat tagihan otomatis bagi semua pelanggan aktif.
    
    Command ini dirancang untuk dijalankan secara periodik, misalnya setiap
    tanggal 14 setiap bulan, menggunakan cron job atau task scheduler lainnya.
    """
    help = 'Membuat tagihan otomatis untuk semua pelanggan aktif setiap bulan.'

    def handle(self, *args, **options):
        # Mendapatkan tanggal saat ini
        today = timezone.now().date()
        
        # Menentukan periode tagihan (bulan berjalan)
        # Contoh: Jika hari ini 14 Agustus, periode_bulan akan menjadi 1 Agustus
        periode_bulan = today.replace(day=1)
        
        # Menentukan tanggal jatuh tempo (contoh: 10 hari setelah tanggal tagihan)
        tanggal_jatuh_tempo = today + timedelta(days=10)
        
        self.stdout.write(f"Mulai membuat tagihan otomatis untuk periode {periode_bulan.strftime('%B %Y')}...")
        
        # Mencari semua pelanggan yang memiliki status 'aktif' dan paket
        # Menggunakan .select_related() untuk mengambil data paket secara efisien
        pelanggan_aktif = Pelanggan.objects.filter(status='aktif').select_related('paket')
        
        tagihan_dibuat = 0
        tagihan_sudah_ada = 0

        for pelanggan in pelanggan_aktif:
            # Memeriksa apakah pelanggan memiliki paket
            if not pelanggan.paket:
                self.stdout.write(self.style.WARNING(f"Pelanggan '{pelanggan.nama}' tidak memiliki paket. Dilewati."))
                continue

            # Memeriksa apakah tagihan untuk pelanggan ini pada bulan ini sudah ada
            if not Tagihan.objects.filter(pelanggan=pelanggan, periode_bulan=periode_bulan).exists():
                try:
                    # Membuat objek Tagihan baru
                    Tagihan.objects.create(
                        pelanggan=pelanggan,
                        tanggal_tagihan=today,
                        periode_bulan=periode_bulan,
                        jumlah_tagihan=pelanggan.paket.harga,
                        tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                        status='belum_lunas'
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Berhasil membuat tagihan untuk '{pelanggan.nama}'."))
                    tagihan_dibuat += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Gagal membuat tagihan untuk '{pelanggan.nama}'. Error: {e}"))
            else:
                self.stdout.write(f"🏷️ Tagihan untuk '{pelanggan.nama}' pada bulan ini sudah ada. Dilewati.")
                tagihan_sudah_ada += 1
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"Proses selesai. Tagihan baru dibuat: {tagihan_dibuat}. Tagihan sudah ada: {tagihan_sudah_ada}.")