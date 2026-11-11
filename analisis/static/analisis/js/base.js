window.AuraUI = (function () {
  function toast(judul, isi, galat) {
    var region = document.getElementById("toast-region");
    if (!region) return;
    var el = document.createElement("div");
    el.className = "toast" + (galat ? " toast--error" : "");
    var s = document.createElement("strong");
    s.textContent = judul;
    el.appendChild(s);
    if (isi) el.appendChild(document.createTextNode(isi));
    region.appendChild(el);
    setTimeout(function () { el.remove(); }, 3000);   // hilang otomatis 3 detik
  }

  function csrf() {
    var m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  // Label berfungsi sebagai tombol: dapat dipicu dengan Enter/Spasi.
  function labelBisaDiketik() {
    document.querySelectorAll('label[role="button"]').forEach(function (l) {
      l.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); l.click(); }
      });
    });
  }
  document.addEventListener("DOMContentLoaded", labelBisaDiketik);

  return { toast: toast, csrf: csrf };
})();
