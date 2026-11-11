from django.urls import path
from . import views

app_name = "analisis"

urlpatterns = [
    path("", views.beranda, name="beranda"),
    path("dashboard/login/", views.admin_login, name="admin_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/pengguna/", views.admin_users, name="admin_users"),
    path("dashboard/referensi/", views.admin_references, name="admin_references"),
    path("dashboard/statistik/", views.admin_statistics, name="admin_statistics"),
    path("dashboard/logout/", views.admin_logout, name="admin_logout"),
    path("kamera/", views.kamera, name="kamera"),
    path("proses/", views.proses, name="proses"),
    path("api/analisis/", views.api_analisis, name="api_analisis"),
    path("hasil/", views.hasil, name="hasil"),
    path("hasil/email/", views.kirim_email, name="kirim_email"),
    path("baru/", views.analisis_baru, name="baru"),
    path("error/", views.error, name="error"),
]
