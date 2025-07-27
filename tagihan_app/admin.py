from django.contrib import admin
from .models import Pelanggan, Tagihan, Pembayaran, Lokasi, Paket

# Register your models here.
admin.site.register(Pelanggan)
admin.site.register(Tagihan)
admin.site.register(Pembayaran)
admin.site.register(Lokasi)
admin.site.register(Paket)
