document.addEventListener("DOMContentLoaded", function () {
  var root = document.getElementById("konten");
  var form = document.getElementById("form-email");
  var musim = JSON.parse(document.getElementById("data-musim").textContent);

  /* --- Kirim email --- */
  function setGalat(id, pesan, input) {
    document.getElementById(id).textContent = pesan || "";
    if (input) input.setAttribute("aria-invalid", pesan ? "true" : "false");
  }
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var nama = form.elements.nama, email = form.elements.email;
    var adaGalat = false;
    setGalat("err-nama", "", nama); setGalat("err-email", "", email);
    if (!nama.value.trim()) { setGalat("err-nama", "Nama wajib diisi.", nama); adaGalat = true; }
    else if (nama.value.length > 50) { setGalat("err-nama", "Nama maksimal 50 karakter.", nama); adaGalat = true; }
    if (!email.value.trim()) { setGalat("err-email", "Email wajib diisi.", email); adaGalat = true; }
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) { setGalat("err-email", "Alamat email tidak valid.", email); adaGalat = true; }
    if (adaGalat) { (form.querySelector('[aria-invalid="true"]') || nama).focus(); return; }

    var tombol = document.getElementById("btn-kirim");
    tombol.disabled = true;
    fetch(root.dataset.emailUrl, {
      method: "POST", body: new FormData(form), headers: { "X-CSRFToken": AuraUI.csrf() }, credentials: "same-origin",
    })
      .then(function (r) { return r.json().then(function (j) { return { status: r.status, json: j }; }); })
      .then(function (res) {
        if (res.json.ok) {
          AuraUI.toast("Email terkirim", "Cek kotak masuk Anda.");
        } else if (res.json.galat) {
          setGalat("err-nama", res.json.galat.nama, nama); setGalat("err-email", res.json.galat.email, email);
        } else {
          AuraUI.toast("Email belum terkirim", res.json.pesan || "Coba lagi nanti.", true);
        }
      })
      .catch(function () { AuraUI.toast("Email belum terkirim", "Periksa koneksi internet Anda.", true); })
      .then(function () { tombol.disabled = false; });
  });

  /* --- Menu unduh --- */
  var btn = document.getElementById("btn-unduh"), menu = document.getElementById("menu-unduh");
  function tutup() { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); }
  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    menu.hidden = !menu.hidden;
    btn.setAttribute("aria-expanded", String(!menu.hidden));
    if (!menu.hidden) menu.querySelector("button").focus();
  });
  document.addEventListener("click", tutup);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { tutup(); btn.focus(); } });

  document.getElementById("unduh-pdf").addEventListener("click", function () { tutup(); window.print(); });
  document.getElementById("unduh-gambar").addEventListener("click", function () { tutup(); unduhGambar(); });

  /* --- Unduh gambar PNG (digambar di canvas, tanpa server) --- */
  function bulat(ctx, x, y, w, h, r) {
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  function unduhGambar() {
    var W = 1080, H = 1350, c = document.createElement("canvas");
    c.width = W; c.height = H;
    var ctx = c.getContext("2d");
    ctx.fillStyle = "#faf7f5"; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#683d5c"; ctx.font = "600 30px 'DM Sans', Arial, sans-serif"; ctx.fillText("AuraVibe", 72, 96);
    ctx.fillStyle = "#a8434c"; ctx.font = "700 22px 'DM Sans', Arial, sans-serif"; ctx.fillText("HASIL PERSONAL COLOR ANDA", 72, 190);
    ctx.fillStyle = "#2e252d"; ctx.font = "600 88px 'Playfair Display', Georgia, serif"; ctx.fillText(musim.nama, 72, 290);
    ctx.fillStyle = "#6f6468"; ctx.font = "26px 'DM Sans', Arial, sans-serif";
    ctx.fillText("Undertone: " + musim.undertone, 72, 345);

    function blok(judul, daftar, y, kolom, tinggi) {
      ctx.fillStyle = "#2e252d"; ctx.font = "600 32px 'DM Sans', Arial, sans-serif"; ctx.fillText(judul, 72, y);
      var lebar = (W - 144 - (kolom - 1) * 24) / kolom;
      daftar.forEach(function (w, i) {
        var x = 72 + (i % kolom) * (lebar + 24), yy = y + 30 + Math.floor(i / kolom) * (tinggi + 90);
        ctx.fillStyle = w[1]; bulat(ctx, x, yy, lebar, tinggi, 20); ctx.fill();
        ctx.strokeStyle = "rgba(0,0,0,.08)"; ctx.lineWidth = 2; ctx.stroke();
        ctx.fillStyle = "#2e252d"; ctx.font = "600 24px 'DM Sans', Arial, sans-serif"; ctx.fillText(w[0], x, yy + tinggi + 34);
        ctx.fillStyle = "#8a7e82"; ctx.font = "20px monospace"; ctx.fillText(w[1], x, yy + tinggi + 62);
      });
    }
    blok("Palet terbaik Anda", musim.palet, 450, 3, 120);
    blok("Warna yang sebaiknya dihindari", musim.hindari, 900, 4, 90);
    ctx.fillStyle = "#8b8084"; ctx.font = "20px 'DM Sans', Arial, sans-serif"; ctx.fillText("Foto Anda tidak disimpan oleh AuraVibe.", 72, H - 60);

    var a = document.createElement("a");
    a.download = "auravibe-" + musim.kelas + ".png";
    a.href = c.toDataURL("image/png");
    document.body.appendChild(a); a.click(); a.remove();
  }
});
