document.addEventListener("DOMContentLoaded", function () {
  var status = document.getElementById("upload-status");
  var input = document.getElementById("photo-input");
  if (!input) return;
  var pesanAwal = status.textContent;

  // Label tombol dapat diaktifkan dengan keyboard (Enter/Spasi).
  document.querySelectorAll('label.button[for="photo-input"]').forEach(function (l) {
    l.setAttribute("role", "button");
    l.setAttribute("tabindex", "0");
    l.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
    });
  });

  input.addEventListener("change", function () {
    var file = input.files && input.files[0];
    if (!file) return;
    status.textContent = "Menyiapkan foto…";
    AuraPhoto.proses(file).then(function (hasil) {
      if (!hasil.ok) {
        status.textContent = pesanAwal;
        input.value = "";
        AuraUI.toast("Foto tidak dapat dipakai", hasil.pesan, true);
        return;
      }
      AuraUI.toast("Foto berhasil diunggah", "Menuju proses analisis…");
      window.location.href = document.body.dataset.prosesUrl || "/proses/";
    });
  });
});
