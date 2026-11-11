document.addEventListener("DOMContentLoaded", function () {
  var root = document.getElementById("konten");
  var d = root.dataset;
  var chips = document.querySelectorAll("#chips .chip");
  var status = document.getElementById("proses-status");
  var MIN_TAMPIL = 2400;   // ms, agar tahapan terbaca jelas

  var dataUrl = AuraPhoto.ambil();
  if (!dataUrl) { window.location.replace(d.berandaUrl); return; }   // tidak ada foto -> kembali

  function setTahap(n) {
    chips.forEach(function (c, i) {
      c.classList.toggle("is-done", i < n - 1);
      c.classList.toggle("is-active", i === n - 1);
    });
  }
  function selesaikan() { chips.forEach(function (c) { c.classList.remove("is-active"); c.classList.add("is-done"); }); }

  function keError(kode) {
    AuraPhoto.hapus();
    window.location.replace(d.errorUrl + "?kode=" + encodeURIComponent(kode));
  }

  var mulai = Date.now();
  setTahap(1);
  var t2 = setTimeout(function () { setTahap(2); }, 900);
  var t3 = setTimeout(function () { setTahap(3); }, 1700);

  var form = new FormData();
  form.append("foto", AuraPhoto.ke_blob(dataUrl), "foto.jpg");

  fetch(d.apiUrl, { method: "POST", body: form, headers: { "X-CSRFToken": AuraUI.csrf() }, credentials: "same-origin" })
    .then(function (r) { return r.json().catch(function () { return { ok: false, kode: "server" }; }); })
    .then(function (hasil) {
      var sisa = Math.max(0, MIN_TAMPIL - (Date.now() - mulai));
      setTimeout(function () {
        clearTimeout(t2); clearTimeout(t3);
        if (!hasil.ok) { keError(hasil.kode || "server"); return; }
        selesaikan();
        status.textContent = "Analisis selesai.";
        AuraPhoto.hapus();                        // foto dihapus dari penyimpanan browser
        window.location.replace(d.hasilUrl);
      }, sisa);
    })
    .catch(function () { clearTimeout(t2); clearTimeout(t3); keError("jaringan"); });
});
