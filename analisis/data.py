MUSIM = {
    "warm-spring": {
        "nama": "Warm Spring",
        "kelas": "spring",
        "deskripsi": "Warna hangat, ringan, dan jernih yang membuat rona wajah tampak segar.",
        "undertone": "Hangat",
        "tags": ["Hangat", "Cerah", "Ringan"],
        "palet": [
            ("Peach Bloom", "#F2A492"), ("Warm Coral", "#EF7568"), ("Butter Cream", "#F5D477"),
            ("Fresh Leaf", "#8CA76C"), ("Aqua Mint", "#6BB7B2"), ("Camel Sand", "#D9B38C"),
        ],
        "hindari": [
            ("Jet Black", "#1F1F23"), ("Icy Blue", "#C1E4F2"),
            ("Dusty Mauve", "#8E7A8C"), ("Optic White", "#FFFFFF"),
        ],
        "hindari_catatan": "Warna gelap pekat atau terlalu dingin dapat meredupkan kesegaran wajah Anda.",
        "fashion": [
            ("Smart casual", "Padukan blazer peach, atasan ivory, dan celana camel yang ringan."),
            ("Aksesori", "Pilih emas muda, rose gold, atau mutiara krem."),
            ("Material terbaik", "Pilih katun, linen tipis, dan sifon dengan hasil akhir cerah."),
        ],
        "ringkasan": "Karakter palet Anda memancarkan kesan segar, ramah, dan penuh energi.",
    },
    "cool-summer": {
        "nama": "Cool Summer",
        "kelas": "summer",
        "deskripsi": "Warna sejuk, lembut, dan sedikit muted yang menyatu harmonis dengan rona wajah.",
        "undertone": "Dingin",
        "tags": ["Sejuk", "Lembut", "Muted"],
        "palet": [
            ("Dusty Rose", "#C98C9D"), ("Powder Blue", "#8FB4C5"), ("Soft Navy", "#536D84"),
            ("Lavender Mist", "#AAA0BD"), ("Stone Taupe", "#A99D95"), ("Rose Quartz", "#E3B7C4"),
        ],
        "hindari": [
            ("Rust Orange", "#C8602F"), ("Mustard", "#D4A12A"),
            ("Olive Drab", "#7A7A3A"), ("Warm Black", "#2A2019"),
        ],
        "hindari_catatan": "Warna hangat yang terlalu jenuh dapat membuat kulit tampak kemerahan.",
        "fashion": [
            ("Smart casual", "Padukan kemeja powder blue, cardigan dusty rose, dan celana soft navy."),
            ("Aksesori", "Pilih perak, white gold, atau mutiara dengan kilau lembut."),
            ("Material terbaik", "Pilih katun halus, rajut tipis, dan satin dengan hasil akhir matte lembut."),
        ],
        "ringkasan": "Karakter palet Anda memancarkan kesan tenang, anggun, dan bersahaja.",
    },
    "warm-autumn": {
        "nama": "Warm Autumn",
        "kelas": "autumn",
        "deskripsi": "Warna hangat, kaya, dan sedikit muted menyatu paling harmonis dengan rona alami wajah Anda.",
        "undertone": "Hangat",
        "tags": ["Hangat", "Kaya", "Earthy"],
        "palet": [
            ("Terracotta", "#B55F42"), ("Rust", "#9F4B33"), ("Mustard", "#C3973E"),
            ("Olive", "#6F7641"), ("Espresso", "#4A372D"), ("Warm Teal", "#3D7772"),
        ],
        "hindari": [
            ("Icy Blue", "#C1E4F2"), ("Cool Lilac", "#BCB1DA"),
            ("Neon Pink", "#FF3F83"), ("Optic White", "#FFFFFF"),
        ],
        "hindari_catatan": "Warna dingin atau terlalu terang dapat membuat rona hangat Anda terlihat pucat.",
        "fashion": [
            ("Smart casual", "Padukan outer terracotta, inner warm ivory, dan celana espresso."),
            ("Aksesori", "Pilih antique gold, kulit cokelat, atau tortoiseshell."),
            ("Material terbaik", "Pilih suede, linen, rajut, dan satin dengan hasil akhir matte."),
        ],
        "ringkasan": "Karakter palet Anda memancarkan kesan hangat, bersahaja, elegan, dan menenangkan.",
    },
    "cool-winter": {
        "nama": "Cool Winter",
        "kelas": "winter",
        "deskripsi": "Warna sejuk, tegas, dan berkontras tinggi yang mempertegas karakter wajah Anda.",
        "undertone": "Dingin",
        "tags": ["Sejuk", "Kontras", "Tegas"],
        "palet": [
            ("True Red", "#C31F43"), ("Deep Navy", "#202B4A"), ("Pure White", "#F4F0E9"),
            ("Royal Plum", "#543354"), ("Charcoal", "#333538"), ("Emerald", "#0E7C66"),
        ],
        "hindari": [
            ("Camel", "#C19A6B"), ("Peach", "#F2B8A0"),
            ("Mustard", "#C9A227"), ("Olive", "#7B7B3F"),
        ],
        "hindari_catatan": "Warna earthy yang pudar dapat membuat wajah tampak kusam di samping kontras alami Anda.",
        "fashion": [
            ("Smart casual", "Padukan blazer deep navy, atasan putih bersih, dan aksen true red."),
            ("Aksesori", "Pilih perak, platinum, atau batu dengan kilau tajam."),
            ("Material terbaik", "Pilih wol halus, satin, dan kulit dengan hasil akhir tegas."),
        ],
        "ringkasan": "Karakter palet Anda memancarkan kesan tegas, elegan, dan berkelas.",
    },
}

# Pesan untuk halaman Error (kode -> judul, pesan, tips)
KESALAHAN = {
    "tidak_ada_wajah": (
        "Wajah tidak terdeteksi",
        "Kami tidak menemukan wajah pada foto Anda.",
        ["Pastikan cahaya merata dan tidak membelakangi sumber cahaya.",
         "Hadapkan wajah lurus ke kamera dan jangan tertutup masker atau rambut.",
         "Gunakan foto tanpa filter agar warna kulit tetap natural."],
    ),
    "banyak_wajah": (
        "Terdeteksi lebih dari satu wajah",
        "Analisis hanya dapat dilakukan pada satu wajah.",
        ["Gunakan foto yang hanya memuat wajah Anda.",
         "Ambil foto dari jarak dekat agar wajah mengisi panduan."],
    ),
    "format": (
        "Format foto tidak didukung",
        "AuraVibe hanya menerima foto berformat JPG, JPEG, atau PNG.",
        ["Simpan ulang foto sebagai JPG atau PNG, lalu unggah kembali."],
    ),
    "ukuran": (
        "Ukuran foto terlalu besar",
        "Ukuran foto maksimal 5 MB.",
        ["Gunakan foto dengan resolusi lebih kecil atau ambil foto langsung dengan kamera."],
    ),
    "jaringan": (
        "Terjadi kesalahan jaringan",
        "Foto belum dapat dikirim untuk dianalisis.",
        ["Periksa koneksi internet Anda, lalu coba lagi."],
    ),
    "server": (
        "Terjadi kesalahan",
        "Analisis tidak dapat diselesaikan saat ini.",
        ["Coba lagi beberapa saat lagi."],
    ),
}
