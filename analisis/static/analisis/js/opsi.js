document.addEventListener("DOMContentLoaded", function () {
  const status = document.getElementById("upload-status");
  const photoInputs = document.querySelectorAll('input[type="file"]');
  const defaultMessage = status.textContent;

  photoInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      const file = input.files && input.files[0];
      if (!file) return;

      if (!file.type.startsWith("image/")) {
        status.textContent = "Pilih file gambar agar bisa melanjutkan.";
        input.value = "";
        return;
      }

      status.textContent = "Foto dipilih: " + file.name + ". Foto belum dikirim atau disimpan.";
      photoInputs.forEach(function (otherInput) {
        if (otherInput !== input) otherInput.value = "";
      });
    });
  });

  window.addEventListener("focus", function () {
    if (photoInputs.length && Array.from(photoInputs).every(function (input) { return !input.files.length; })) {
      status.textContent = defaultMessage;
    }
  });
});