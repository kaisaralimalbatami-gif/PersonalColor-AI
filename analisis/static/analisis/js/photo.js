/* Persiapan foto di browser: validasi, perkecil, lalu titipkan ke sessionStorage.
   Foto tidak pernah disimpan permanen; proses.js menghapusnya setelah analisis. */
window.AuraPhoto = (function () {
  var KUNCI = "auravibe_foto";
  var MAKS_BYTES = 5 * 1024 * 1024;
  var SISI_MAKS = 1024;
  var TIPE = ["image/jpeg", "image/png"];

  function validasi(file) {
    if (!file || TIPE.indexOf(file.type) === -1) return { kode: "format", pesan: "Format tidak didukung. Gunakan JPG, JPEG, atau PNG." };
    if (file.size > MAKS_BYTES) return { kode: "ukuran", pesan: "Ukuran foto maksimal 5 MB." };
    return null;
  }

  function muat(file) {
    if (window.createImageBitmap) {
      return createImageBitmap(file, { imageOrientation: "from-image" });
    }
    return new Promise(function (ok, gagal) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () { URL.revokeObjectURL(url); ok(img); };
      img.onerror = function () { URL.revokeObjectURL(url); gagal(new Error("gagal")); };
      img.src = url;
    });
  }

  // Perkecil foto ke maksimal 1024 px dan ubah ke JPEG (data URL).
  function siapkan(file) {
    return muat(file).then(function (img) {
      var w = img.width, h = img.height, skala = Math.min(1, SISI_MAKS / Math.max(w, h));
      var c = document.createElement("canvas");
      c.width = Math.round(w * skala);
      c.height = Math.round(h * skala);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      return c.toDataURL("image/jpeg", 0.9);
    });
  }

  function simpan(dataUrl) {
    try { sessionStorage.setItem(KUNCI, dataUrl); return true; } catch (e) { return false; }
  }
  function ambil() { try { return sessionStorage.getItem(KUNCI); } catch (e) { return null; } }
  function hapus() { try { sessionStorage.removeItem(KUNCI); } catch (e) { /* abaikan */ } }

  // Alur lengkap: validasi -> perkecil -> simpan. Mengembalikan Promise<{ok, kode, pesan}>.
  function proses(file) {
    var galat = validasi(file);
    if (galat) return Promise.resolve({ ok: false, kode: galat.kode, pesan: galat.pesan });
    return siapkan(file).then(function (dataUrl) {
      return simpan(dataUrl) ? { ok: true } : { ok: false, kode: "ukuran", pesan: "Foto tidak dapat diproses di perangkat ini." };
    }).catch(function () {
      return { ok: false, kode: "format", pesan: "Foto tidak dapat dibaca. Coba foto lain." };
    });
  }

  function dataUrlKeBlob(dataUrl) {
    var bagian = dataUrl.split(","), mime = bagian[0].match(/:(.*?);/)[1];
    var bin = atob(bagian[1]), arr = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    return new Blob([arr], { type: mime });
  }

  return { proses: proses, ambil: ambil, hapus: hapus, simpan: simpan, ke_blob: dataUrlKeBlob };
})();
