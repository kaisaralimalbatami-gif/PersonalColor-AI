from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from . import data, services
from .forms import KirimHasilForm

SESSION_KEY = "hasil_analisis"


def beranda(request):
    """Halaman utama: tombol "Unggah foto" dan "Gunakan kamera"."""
    return render(request, "analisis/beranda.html")


@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Masuk ke dashboard menggunakan akun staff Django."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("analisis:dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    form.fields["username"].widget.attrs.pop("autofocus", None)
    form.fields["username"].widget.attrs.update({
        "placeholder": "Masukkan username",
        "autocomplete": "username",
    })
    form.fields["password"].widget.attrs.update({
        "placeholder": "Masukkan kata sandi",
        "autocomplete": "current-password",
    })

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            form.add_error(None, "Akun ini tidak memiliki akses administrator.")
        else:
            login(request, user)
            return redirect("analisis:dashboard")

    return render(request, "analisis/admin/login.html", {"form": form})


@login_required(login_url="analisis:admin_login")
def dashboard(request):
    """Ringkasan admin; statistik pada tampilan saat ini adalah data pratinjau."""
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request, "analisis/admin/dashboard.html", {
        "admin_name": request.user.get_full_name() or request.user.get_username(),
        "tanggal_hari_ini": timezone.localdate(),
    })


@require_POST
@login_required(login_url="analisis:admin_login")
def admin_logout(request):
    if not request.user.is_staff:
        raise PermissionDenied
    logout(request)
    return redirect("analisis:admin_login")


def kamera(request):
    """Langkah 1 dari 3: ambil foto dengan kamera."""
    return render(request, "analisis/kamera.html")


@ensure_csrf_cookie
def proses(request):
    """Langkah 2 dari 3: foto dikirim ke API analisis oleh proses.js."""
    return render(request, "analisis/proses.html")


@require_POST
def api_analisis(request):
    """Terima foto, analisis di memori, simpan HASIL (bukan foto) di sesi."""
    foto = request.FILES.get("foto")
    if foto is None:
        return JsonResponse({"ok": False, "kode": "format"}, status=400)
    try:
        hasil = services.analisis_foto(foto.read(), path_model=getattr(settings, "MEDIAPIPE_FACE_MODEL", None))
    except services.AnalisisError as err:
        return JsonResponse({"ok": False, "kode": err.kode}, status=422 if err.kode != "server" else 500)
    request.session[SESSION_KEY] = hasil
    return JsonResponse({"ok": True})


@ensure_csrf_cookie
def hasil(request):
    """Langkah 3 dari 3: tampilkan hasil analisis dari sesi."""
    ringkas = request.session.get(SESSION_KEY)
    if not ringkas or ringkas.get("musim") not in data.MUSIM:
        return redirect("analisis:beranda")
    return render(request, "analisis/hasil.html", {
        "musim": data.MUSIM[ringkas["musim"]],
        "undertone": ringkas["undertone"].capitalize(),
        "kecerahan": ringkas["kecerahan"],
        "kontras": ringkas["kontras"],
        "form": KirimHasilForm(),
    })


@require_POST
def kirim_email(request):
    """Kirim ringkasan hasil ke email pengguna. Nama dan email tidak disimpan."""
    ringkas = request.session.get(SESSION_KEY)
    if not ringkas or ringkas.get("musim") not in data.MUSIM:
        return JsonResponse({"ok": False, "pesan": "Hasil analisis tidak ditemukan."}, status=400)
    form = KirimHasilForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "galat": {k: v[0] for k, v in form.errors.items()}}, status=400)
    musim = data.MUSIM[ringkas["musim"]]
    isi = render(request, "analisis/email/hasil_email.txt", {
        "nama": form.cleaned_data["nama"], "musim": musim,
        "undertone": ringkas["undertone"].capitalize(),
    }).content.decode()
    try:
        send_mail(f"Hasil personal color Anda: {musim['nama']}", isi, None, [form.cleaned_data["email"]])
    except Exception:
        return JsonResponse({"ok": False, "pesan": "Email belum dapat dikirim. Coba lagi nanti."}, status=502)
    return JsonResponse({"ok": True})


@require_GET
def analisis_baru(request):
    """Hapus hasil dari sesi lalu kembali ke halaman utama."""
    request.session.pop(SESSION_KEY, None)
    return redirect("analisis:beranda")


def error(request):
    """Halaman Error: kode kesalahan dibaca dari query string (daftar putih)."""
    kode = request.GET.get("kode", "server")
    if kode not in data.KESALAHAN:
        kode = "server"
    judul, pesan, tips = data.KESALAHAN[kode]
    return render(request, "analisis/error.html", {"judul": judul, "pesan": pesan, "tips": tips, "kode": kode},
                  status=200)
