from django.urls import path
from . import views

app_name = 'tagihan_app'

urlpatterns = [
    path('', views.index, name='index'),
]
