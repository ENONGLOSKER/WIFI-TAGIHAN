from django.contrib import admin
from .models import Pelanggan, Tagihan, Pembayaran, Lokasi, Paket

# Register your models here.

class PelangganAdmin(admin.ModelAdmin):
    list_display = ('nama', 'alamat', 'kontak', 'lokasi', 'paket', 'username_pppoe', 'tanggal_bergabung', 'status')
    search_fields = ('nama', 'alamat', 'kontak')
    list_filter = ('status', 'lokasi')

class TagihanAdmin(admin.ModelAdmin):
    list_display = ('pelanggan', 'tanggal_tagihan', 'periode_bulan', 'jumlah_tagihan', 'jumlah_terbayar', 'tanggal_jatuh_tempo', 'status')
    list_filter = ('status',)
    search_fields = ('pelanggan__nama',)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('pelanggan')
    
class PembayaranAdmin(admin.ModelAdmin):
    list_display = ('tagihan', 'tanggal_pembayaran', 'jumlah_pembayaran', 'metode_pembayaran')
    search_fields = ('tagihan__pelanggan__nama',)
    list_filter = ('metode_pembayaran',)


admin.site.register(Pelanggan, PelangganAdmin)
admin.site.register(Tagihan, TagihanAdmin)
admin.site.register(Pembayaran, PembayaranAdmin)
admin.site.register(Lokasi)
admin.site.register(Paket)
