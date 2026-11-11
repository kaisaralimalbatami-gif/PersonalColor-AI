from django.urls import path
from . import views

app_name = "analisis"

urlpatterns = [
    path("", views.beranda, name="beranda"),
    path("kamera/", views.kamera, name="kamera"),
    path("proses/", views.proses, name="proses"),
    path("api/analisis/", views.api_analisis, name="api_analisis"),
    path("hasil/", views.hasil, name="hasil"),
    path("hasil/email/", views.kirim_email, name="kirim_email"),
    path("baru/", views.analisis_baru, name="baru"),
    path("error/", views.error, name="error"),
]
