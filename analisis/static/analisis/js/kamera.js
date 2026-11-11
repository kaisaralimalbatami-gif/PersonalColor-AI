document.addEventListener("DOMContentLoaded", function () {
  var root = document.getElementById("konten");
  var prosesUrl = root.dataset.prosesUrl;
  var video = document.getElementById("video");
  var shutter = document.getElementById("shutter");
  var kamera = document.getElementById("camera");
  var live = document.getElementById("live");
  var flash = document.getElementById("flash");
  var kosong = document.getElementById("camera-empty");
  var kosongTeks = document.getElementById("camera-empty-text");
  var canvas = document.getElementById("canvas");
  var inputUnggah = document.getElementById("photo-input-kamera");
  var stream = null;

  function matikan() {
    if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
  }
  window.addEventListener("pagehide", matikan);

  function tampilkanKosong(pesan) {
    matikan();
    shutter.disabled = true;
    live.hidden = true;
    kosongTeks.textContent = pesan;
    kosong.hidden = false;
  }

  function mulai() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      tampilkanKosong("Browser ini tidak mendukung kamera (atau halaman tidak memakai HTTPS). Unggah foto dari perangkat Anda.");
      return;
    }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 960 } }, audio: false })
      .then(function (s) {
        stream = s;
        video.srcObject = s;
        return video.play();
      })
      .then(function () {
        shutter.disabled = false;
        live.hidden = false;
        kamera.classList.add("is-ready");
      })
      .catch(function (err) {
        var ditolak = err && (err.name === "NotAllowedError" || err.name === "SecurityError");
        tampilkanKosong(ditolak
          ? "Izin kamera ditolak. Izinkan akses kamera di browser, atau unggah foto dari perangkat Anda."
          : "Kamera tidak ditemukan atau sedang dipakai aplikasi lain. Unggah foto dari perangkat Anda.");
      });
  }

  function lanjut(dataUrl) {
    if (!AuraPhoto.simpan(dataUrl)) {
      AuraUI.toast("Foto tidak dapat diproses", "Coba unggah foto dari perangkat.", true);
      return;
    }
    matikan();
    window.location.href = prosesUrl;
  }

  shutter.addEventListener("click", function () {
    if (!video.videoWidth) return;
    shutter.disabled = true;
    flash.classList.remove("is-on");
    void flash.offsetWidth;
    flash.classList.add("is-on");
    var skala = Math.min(1, 1024 / Math.max(video.videoWidth, video.videoHeight));
    canvas.width = Math.round(video.videoWidth * skala);
    canvas.height = Math.round(video.videoHeight * skala);
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);   // tidak dicerminkan
    lanjut(canvas.toDataURL("image/jpeg", 0.9));
  });

  inputUnggah.addEventListener("change", function () {
    var file = inputUnggah.files && inputUnggah.files[0];
    if (!file) return;
    AuraPhoto.proses(file).then(function (hasil) {
      if (!hasil.ok) {
        inputUnggah.value = "";
        AuraUI.toast("Foto tidak dapat dipakai", hasil.pesan, true);
        return;
      }
      matikan();
      window.location.href = prosesUrl;
    });
  });

  mulai();
});
