import math
import threading
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

# --- Batasan unggahan --------------------------------------------------------
MAKS_BYTES = 5 * 1024 * 1024          # 5 MB
SISI_MAKS = 1024                      # foto diperkecil agar analisis cepat
FORMAT_DIDUKUNG = ("jpeg", "png")

# --- Ambang batas (kalibrasi dengan data uji) --------------------------------
HUE_DINGIN_MAKS = 50.0                # sudut hue Lab <= ini  -> undertone dingin
HUE_HANGAT_MIN = 56.0                 # sudut hue Lab >= ini  -> undertone hangat
L_TERANG_MIN = 68.0                   # L* >= ini -> "Terang"
L_SEDANG_MIN = 55.0                   # L* >= ini -> "Sedang", di bawahnya "Gelap"
L_MUSIM_TERANG = 62.0                 # L* >= ini -> keluarga Spring/Summer
KONTRAS_TINGGI_MIN = 32.0             # selisih L* kulit vs area gelap wajah
KONTRAS_SEDANG_MIN = 20.0


class AnalisisError(Exception):
    """Kesalahan yang dapat ditampilkan ke pengguna. `kode` cocok dengan data.KESALAHAN."""

    def __init__(self, kode, pesan=""):
        super().__init__(pesan or kode)
        self.kode = kode


# --- Decode foto --------------------------------------------------------------
def _jenis_gambar(data: bytes):
    if data[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return None


def decode_foto(data: bytes) -> np.ndarray:
    """Validasi dan decode byte foto menjadi array BGR yang sudah diperkecil."""
    if not data or len(data) > MAKS_BYTES:
        raise AnalisisError("ukuran")
    if _jenis_gambar(data) not in FORMAT_DIDUKUNG:
        raise AnalisisError("format")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise AnalisisError("format")
    tinggi, lebar = img.shape[:2]
    skala = SISI_MAKS / max(tinggi, lebar)
    if skala < 1:
        img = cv2.resize(img, (int(lebar * skala), int(tinggi * skala)), interpolation=cv2.INTER_AREA)
    return img


# --- Deteksi wajah ------------------------------------------------------------
_kunci = threading.Lock()   # detektor MediaPipe tidak aman dipakai paralel


def _detektor_mediapipe_solutions():
    """MediaPipe versi lama (mp.solutions). Mengembalikan None jika tidak tersedia."""
    try:
        import mediapipe as mp
        if not hasattr(mp, "solutions"):
            return None
        fd = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    except Exception:
        return None

    def deteksi(bgr):
        tinggi, lebar = bgr.shape[:2]
        hasil = fd.process(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        kotak = []
        for d in hasil.detections or []:
            b = d.location_data.relative_bounding_box
            kotak.append((int(b.xmin * lebar), int(b.ymin * tinggi), int(b.width * lebar), int(b.height * tinggi)))
        return kotak

    return deteksi


def _detektor_mediapipe_tasks(path_model):
    """MediaPipe versi baru (Tasks API). Perlu berkas model .tflite (blaze_face_short_range)."""
    if not path_model or not Path(path_model).is_file():
        return None
    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mpt
        from mediapipe.tasks.python import vision
        opsi = vision.FaceDetectorOptions(
            base_options=mpt.BaseOptions(model_asset_path=str(path_model)),
            min_detection_confidence=0.5,
        )
        fd = vision.FaceDetector.create_from_options(opsi)
    except Exception:
        return None

    def deteksi(bgr):
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        hasil = fd.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        return [(d.bounding_box.origin_x, d.bounding_box.origin_y, d.bounding_box.width, d.bounding_box.height)
                for d in hasil.detections]

    return deteksi


def _detektor_haar():
    """Cadangan terakhir: Haar cascade bawaan OpenCV."""
    path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not path.is_file():
        return None
    klas = cv2.CascadeClassifier(str(path))
    if klas.empty():
        return None

    def deteksi(bgr):
        abu = cv2.equalizeHist(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY))
        sisi_min = max(48, min(abu.shape[:2]) // 8)
        return [tuple(int(v) for v in k) for k in klas.detectMultiScale(abu, 1.1, 5, minSize=(sisi_min, sisi_min))]

    return deteksi


@lru_cache(maxsize=4)
def ambil_detektor(path_model=None):
    """Pilih detektor wajah pertama yang tersedia: MediaPipe -> Haar OpenCV."""
    for pabrik in (_detektor_mediapipe_solutions, lambda: _detektor_mediapipe_tasks(path_model), _detektor_haar):
        d = pabrik()
        if d is not None:
            return d
    raise AnalisisError("server", "Tidak ada detektor wajah yang tersedia.")


def _kotak_valid(kotak, tinggi, lebar):
    hasil = []
    for x, y, w, h in kotak:
        x, y = max(0, x), max(0, y)
        w, h = min(w, lebar - x), min(h, tinggi - y)
        if w > 20 and h > 20:
            hasil.append((x, y, w, h))
    return hasil


# --- Sampel warna kulit -------------------------------------------------------
def _area_kulit(kotak):
    """Tiga area sampel (dahi, pipi kiri, pipi kanan) sebagai pecahan dari kotak wajah."""
    x, y, w, h = kotak

    def area(fx, fy, fw, fh):
        return (int(x + fx * w), int(y + fy * h), max(2, int(fw * w)), max(2, int(fh * h)))

    return [area(0.35, 0.12, 0.30, 0.12),    # dahi
            area(0.18, 0.55, 0.22, 0.16),    # pipi kiri
            area(0.60, 0.55, 0.22, 0.16)]    # pipi kanan


def _piksel_kulit(bgr, kotak):
    """Kumpulkan piksel kulit (BGR) dari area sampel dan buang bayangan/highlight."""
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    sampel = []
    for x, y, w, h in _area_kulit(kotak):
        patch = bgr[y:y + h, x:x + w].reshape(-1, 3)
        yc = ycrcb[y:y + h, x:x + w].reshape(-1, 3)
        mask = (yc[:, 1] >= 133) & (yc[:, 1] <= 180) & (yc[:, 2] >= 77) & (yc[:, 2] <= 135)
        mask &= (yc[:, 0] > 40) & (yc[:, 0] < 245)
        sampel.append(patch[mask])
    gabung = np.concatenate(sampel) if sampel else np.empty((0, 3), np.uint8)
    return gabung


def _ke_lab(bgr_piksel):
    """Konversi piksel BGR uint8 (N,3) ke Lab float: L 0-100, a/b nilai asli."""
    arr = (bgr_piksel.astype(np.float32) / 255.0).reshape(-1, 1, 3)
    return cv2.cvtColor(arr, cv2.COLOR_BGR2Lab).reshape(-1, 3)


def _kontras(bgr, kotak, L_kulit):
    """Perkiraan kontras: selisih L* kulit dengan area tergelap di pita mata-bibir."""
    x, y, w, h = kotak
    pita = bgr[y + int(0.25 * h): y + int(0.90 * h), x + int(0.15 * w): x + int(0.85 * w)]
    if pita.size == 0:
        return 0.0
    L = _ke_lab(pita.reshape(-1, 3))[:, 0]
    return float(max(0.0, L_kulit - np.percentile(L, 5)))


# --- Klasifikasi --------------------------------------------------------------
def klasifikasi_undertone(hue):
    if hue >= HUE_HANGAT_MIN:
        return "hangat"
    if hue <= HUE_DINGIN_MAKS:
        return "dingin"
    return "netral"


def klasifikasi_kecerahan(L):
    if L >= L_TERANG_MIN:
        return "Terang"
    if L >= L_SEDANG_MIN:
        return "Sedang"
    return "Gelap"


def klasifikasi_kontras(selisih):
    if selisih >= KONTRAS_TINGGI_MIN:
        return "Tinggi"
    if selisih >= KONTRAS_SEDANG_MIN:
        return "Sedang"
    return "Rendah"


def pilih_musim(undertone, hue, L):
    """Petakan undertone + kecerahan ke satu dari empat musim (kunci data.MUSIM)."""
    if undertone == "netral":   # netral: ikuti sisi yang lebih dekat
        undertone = "hangat" if hue >= (HUE_DINGIN_MAKS + HUE_HANGAT_MIN) / 2 else "dingin"
    terang = L >= L_MUSIM_TERANG
    if undertone == "hangat":
        return "warm-spring" if terang else "warm-autumn"
    return "cool-summer" if terang else "cool-winter"


# --- Fungsi utama -------------------------------------------------------------
def analisis_foto(data: bytes, path_model=None, detektor=None) -> dict:
    """Analisis foto (bytes) dan kembalikan hasil ringkas. Tidak menyimpan foto.

    `detektor` opsional: fungsi(bgr) -> daftar kotak (x, y, w, h); dipakai untuk pengujian.
    """
    bgr = decode_foto(data)
    tinggi, lebar = bgr.shape[:2]
    deteksi = detektor or ambil_detektor(str(path_model) if path_model else None)
    with _kunci:
        kotak = _kotak_valid(deteksi(bgr), tinggi, lebar)
    if not kotak:
        raise AnalisisError("tidak_ada_wajah")
    if len(kotak) > 1:
        # abaikan deteksi kecil (mis. false positive) bila ada satu wajah dominan
        kotak.sort(key=lambda k: k[2] * k[3], reverse=True)
        if kotak[1][2] * kotak[1][3] > 0.35 * kotak[0][2] * kotak[0][3]:
            raise AnalisisError("banyak_wajah")
    wajah = kotak[0]

    piksel = _piksel_kulit(bgr, wajah)
    if len(piksel) < 50:
        raise AnalisisError("tidak_ada_wajah")
    L, a, b = (float(v) for v in np.median(_ke_lab(piksel), axis=0))
    hue = math.degrees(math.atan2(b, a))
    selisih = _kontras(bgr, wajah, L)

    undertone = klasifikasi_undertone(hue)
    return {
        "musim": pilih_musim(undertone, hue, L),
        "undertone": undertone,
        "kecerahan": klasifikasi_kecerahan(L),
        "kontras": klasifikasi_kontras(selisih),
        # nilai mentah, berguna untuk kalibrasi dan pengujian
        "metrik": {"L": round(L, 1), "a": round(a, 1), "b": round(b, 1),
                   "hue": round(hue, 1), "kontras": round(selisih, 1)},
    }
