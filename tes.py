from tagihan_app.models import Paket
paket_list = [
    ("Device 1", "device", 1, None, Decimal('50000')),
    ("Device 2", "device", 2, None, Decimal('80000')),
    ("Device 3", "device", 3, None, Decimal('100000')),
    ("Device 4", "device", 4, None, Decimal('130000')),
    ("Device 5", "device", 5, None, Decimal('160000')),
    ("PPPoE 5 Mbps", "pppoe", None, 5, Decimal('100000')),
    ("PPPoE 10 Mbps", "pppoe", None, 10, Decimal('150000')),
    ("PPPoE 20 Mbps", "pppoe", None, 20, Decimal('250000')),
    ("Device 6", "device", 6, None, Decimal('180000')),
    ("PPPoE 30 Mbps", "pppoe", None, 30, Decimal('350000')),
    ("Device 7", "device", 7, None, Decimal('200000')),
]
for nama, jenis, jml_device, kec_mbps, harga in paket_list:
    Paket.objects.get_or_create(
        nama=nama,
        defaults={
            'jenis_paket': jenis,
            'jumlah_device': jml_device,
            'kecepatan_mbps': kec_mbps,
            'harga': harga
        }
    )

print(f"Created {Paket.objects.count()} Paket records")