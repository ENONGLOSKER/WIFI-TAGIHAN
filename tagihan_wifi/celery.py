import os
from celery import Celery

# Mengatur konfigurasi Django untuk Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tagihan_wifi.settings')

app = Celery('tagihan_wifi')

# Menggunakan konfigurasi Celery dari settings.py
# 'CELERY' adalah prefix dari semua variabel konfigurasi Celery di settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Memuat tugas dari file tasks.py di setiap aplikasi
app.autodiscover_tasks()