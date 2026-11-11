"""Pengujian analisis dan alur halaman pengguna.

Jalankan: python manage.py test analisis
Kelas AnalisisServiceTests memakai detektor palsu sehingga tidak membutuhkan model wajah.
"""
import cv2
import numpy as np
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from . import data, services


def foto_sintetis(bgr_kulit, ukuran=400, format=".jpg"):
    """Gambar latar abu dengan 'wajah' elips berwarna kulit di tengah."""
    img = np.full((ukuran, ukuran, 3), (200, 200, 200), np.uint8)
    cv2.ellipse(img, (ukuran // 2, ukuran // 2), (ukuran // 4, ukuran // 3), 0, 0, 360, bgr_kulit, -1)
    ok, buf = cv2.imencode(format, img)
    assert ok
    return buf.tobytes()


def detektor_tetap(ukuran=400):
    kotak = (ukuran // 4, ukuran // 6, ukuran // 2, int(ukuran * 0.66))
    return lambda bgr: [kotak]


class AnalisisServiceTests(SimpleTestCase):
    def test_kulit_hangat_gelap_menjadi_warm_autumn(self):
        hasil = services.analisis_foto(foto_sintetis((70, 120, 170)), detektor=detektor_tetap())
        self.assertEqual(hasil["undertone"], "hangat")
        self.assertEqual(hasil["musim"], "warm-autumn")

    def test_kulit_hangat_terang_menjadi_warm_spring(self):
        hasil = services.analisis_foto(foto_sintetis((160, 195, 235)), detektor=detektor_tetap())
        self.assertEqual(hasil["musim"], "warm-spring")

    def test_semua_musim_ada_di_data(self):
        for kunci in ("warm-spring", "cool-summer", "warm-autumn", "cool-winter"):
            self.assertIn(kunci, data.MUSIM)

    def test_tanpa_wajah(self):
        with self.assertRaises(services.AnalisisError) as ctx:
            services.analisis_foto(foto_sintetis((70, 120, 170)), detektor=lambda b: [])
        self.assertEqual(ctx.exception.kode, "tidak_ada_wajah")

    def test_dua_wajah(self):
        k = (100, 66, 200, 264)
        with self.assertRaises(services.AnalisisError) as ctx:
            services.analisis_foto(foto_sintetis((70, 120, 170)), detektor=lambda b: [k, k])
        self.assertEqual(ctx.exception.kode, "banyak_wajah")

    def test_format_tidak_didukung(self):
        with self.assertRaises(services.AnalisisError) as ctx:
            services.analisis_foto(b"GIF89a-bukan-jpg-atau-png", detektor=detektor_tetap())
        self.assertEqual(ctx.exception.kode, "format")

    def test_ukuran_terlalu_besar(self):
        with self.assertRaises(services.AnalisisError) as ctx:
            services.analisis_foto(b"\xff\xd8\xff" + b"0" * (services.MAKS_BYTES + 1), detektor=detektor_tetap())
        self.assertEqual(ctx.exception.kode, "ukuran")

    def test_klasifikasi_batas(self):
        self.assertEqual(services.klasifikasi_undertone(60), "hangat")
        self.assertEqual(services.klasifikasi_undertone(45), "dingin")
        self.assertEqual(services.klasifikasi_undertone(53), "netral")
        self.assertEqual(services.klasifikasi_kecerahan(70), "Terang")
        self.assertEqual(services.klasifikasi_kecerahan(40), "Gelap")


class HalamanTests(TestCase):
    def test_halaman_dapat_dibuka(self):
        for nama in ("beranda", "kamera", "proses", "error"):
            self.assertEqual(self.client.get(reverse(f"analisis:{nama}")).status_code, 200, nama)

    def test_hasil_tanpa_sesi_kembali_ke_beranda(self):
        self.assertRedirects(self.client.get(reverse("analisis:hasil")), reverse("analisis:beranda"))

    def test_hasil_dengan_sesi(self):
        s = self.client.session
        s["hasil_analisis"] = {"musim": "warm-autumn", "undertone": "hangat", "kecerahan": "Sedang", "kontras": "Sedang"}
        s.save()
        resp = self.client.get(reverse("analisis:hasil"))
        self.assertContains(resp, "Warm Autumn")
        self.assertContains(resp, "#B55F42")

    def test_kode_error_tidak_dikenal_memakai_default(self):
        self.assertContains(self.client.get(reverse("analisis:error") + "?kode=<script>"), "Terjadi kesalahan")

    def test_api_tanpa_foto(self):
        self.assertEqual(self.client.post(reverse("analisis:api_analisis")).status_code, 400)

    def test_kirim_email_valid_dan_tidak_valid(self):
        s = self.client.session
        s["hasil_analisis"] = {"musim": "warm-autumn", "undertone": "hangat", "kecerahan": "Sedang", "kontras": "Sedang"}
        s.save()
        url = reverse("analisis:kirim_email")
        self.assertEqual(self.client.post(url, {"nama": "", "email": "salah"}).status_code, 400)
        self.assertEqual(self.client.post(url, {"nama": "Divani", "email": "d@example.com"}).status_code, 200)


class DashboardAdminTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username="admin-ui",
            password="Secure-test-pass-123",
            is_staff=True,
        )

    def test_dashboard_memerlukan_login(self):
        response = self.client.get(reverse("analisis:dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('analisis:admin_login')}?next={reverse('analisis:dashboard')}",
        )

    def test_admin_dapat_login_dan_membuka_dashboard(self):
        login_response = self.client.post(reverse("analisis:admin_login"), {
            "username": "admin-ui",
            "password": "Secure-test-pass-123",
        })
        self.assertRedirects(login_response, reverse("analisis:dashboard"))
        dashboard_response = self.client.get(reverse("analisis:dashboard"))
        self.assertContains(dashboard_response, "Dashboard")
        self.assertContains(dashboard_response, "Data contoh")
        self.assertContains(dashboard_response, "Admin-Ui")
        self.assertNotContains(dashboard_response, "Tambah referensi")

    def test_tiga_halaman_admin_memerlukan_staff_dan_dapat_dibuka(self):
        routes = (
            ("admin_users", ("Data pengguna", "Alya Putri")),
            ("admin_references", ("Referensi warna", "Terracotta")),
            ("admin_statistics", ("Statistik penggunaan", "Tren analisis bulanan")),
        )
        for route, expected_content in routes:
            response = self.client.get(reverse(f"analisis:{route}"))
            self.assertRedirects(
                response,
                f"{reverse('analisis:admin_login')}?next={reverse(f'analisis:{route}')}",
            )
            self.client.force_login(self.admin)
            response = self.client.get(reverse(f"analisis:{route}"))
            self.assertEqual(response.status_code, 200, route)
            for content in expected_content:
                self.assertContains(response, content)
            self.client.logout()

    def test_pengguna_non_staff_tidak_dapat_login_admin(self):
        pengguna = get_user_model().objects.create_user(username="pengguna", password="User-pass-123")
        response = self.client.post(reverse("analisis:admin_login"), {
            "username": "pengguna",
            "password": "User-pass-123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tidak memiliki akses administrator")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.client.force_login(pengguna)
        for route in ("dashboard", "admin_users", "admin_references", "admin_statistics"):
            self.assertEqual(self.client.get(reverse(f"analisis:{route}")).status_code, 403, route)

    def test_logout_memerlukan_post_dan_mengakhiri_sesi_admin(self):
        self.client.force_login(self.admin)
        logout_response = self.client.post(reverse("analisis:admin_logout"))
        self.assertRedirects(logout_response, reverse("analisis:admin_login"))
        dashboard_response = self.client.get(reverse("analisis:dashboard"))
        self.assertEqual(dashboard_response.status_code, 302)
