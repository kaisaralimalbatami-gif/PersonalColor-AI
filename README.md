# PersonalColor-AI (AuraVibe)

Aplikasi web Personal Color Analysis berbasis OpenCV dan MediaPipe.

## Menjalankan

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate        # tabel sesi (hasil analisis disimpan di sesi, foto tidak disimpan)
python manage.py runserver
```

Buka http://127.0.0.1:8000/

## Halaman pengguna

| Langkah | URL | Template | Keterangan |
|---|---|---|---|
| Halaman Utama | `/` | `beranda.html` | Tombol "Unggah foto" dan "Gunakan kamera" |
| 1 dari 3 | `/kamera/` | `kamera.html` | Pratinjau kamera, panduan wajah, tombol rana, Unggah |
| 2 dari 3 | `/proses/` | `proses.html` | Foto dikirim ke `/api/analisis/`, tahapan analisis ditampilkan |
| 3 dari 3 | `/hasil/` | `hasil.html` | Musim, undertone, palet, fashion, kirim email, unduh PNG/PDF |
| Error | `/error/?kode=...` | `error.html` | `tidak_ada_wajah`, `banyak_wajah`, `format`, `ukuran`, `jaringan`, `server` |

Kode analisis ada di `analisis/services.py` (tanpa Django, mudah diuji). Data palet ada di `analisis/data.py`.
Foto hanya diproses di memori; yang disimpan di sesi hanya hasil (musim, undertone, kecerahan, kontras).

## Detektor wajah

`services.ambil_detektor()` memilih yang pertama tersedia: MediaPipe `solutions` (versi lama),
MediaPipe Tasks (butuh `analisis/model_wajah/blaze_face_short_range.tflite`), lalu Haar cascade OpenCV.

## Pengujian

```bash
python manage.py test analisis
```

## Kalibrasi

Ambang undertone, kecerahan, dan kontras ada di bagian atas `analisis/services.py`.
Kalibrasi dengan data uji tim sebelum dipakai untuk validasi akurasi.
