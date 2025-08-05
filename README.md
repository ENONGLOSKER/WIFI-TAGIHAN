
<div class="" align="center">
    <p>Penyedia Layanan Internet</p>
    <h1>BUKAL NET</h1>
    <span>✨⭐⭐⭐✨</span>
    <hr>
    <img src="/static/img/UI/home.png" alt="spk">
    <br>
    <img src="/static/img/UI/login.png" alt="spk">
    <br>
    <img src="/static/img/UI/dashboard.png" alt="spk">
    <br>
</div>

## Setup Project
<strong>Instalasi</strong>

- 📍&nbsp;&nbsp;[Install Python (Python Official)](https://www.python.org/)
- 📗&nbsp;&nbsp;Clone repository
```bash
git https://github.com/ENONGLOSKER/WIFI-TAGIHAN.git
```
- 📁&nbsp;&nbsp;Masuk ke Folder
```bash
cd tagihan_wifi
```
- 📁&nbsp;&nbsp;Install requirements
```bash
pip install -r requirement.txt
```
- 📁&nbsp;&nbsp;NYALAKAN REDIS
```bash
redis-server 
```
- 📁&nbsp;&nbsp;TERMINAL 1 Run Server
```bash
python manage.py runserver
```
- 📁&nbsp;&nbsp;TERMINAL 2 WORKER
```bash
celery -A tagihan_wifi worker --loglevel=info -P solo
```
- 📁&nbsp;&nbsp;TERMINAL 2 BEAT
```bash
celery -A tagihan_wifi beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
<br>

pip install celery redis django-celery-beat

## FunForCode
#Elqusairi