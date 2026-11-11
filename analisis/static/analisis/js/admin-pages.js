document.addEventListener("DOMContentLoaded", function () {
  const search = document.getElementById("user-search");
  if (search) {
    const list = document.getElementById("users-list");
    const count = document.getElementById("users-count");
    const empty = document.getElementById("users-empty");
    const initialTotal = list.querySelectorAll("[data-user-row]").length;

    function updateUsers() {
      const query = search.value.trim().toLocaleLowerCase("id");
      let visible = 0;
      list.querySelectorAll("[data-user-row]").forEach(function (row) {
        const matches = row.textContent.toLocaleLowerCase("id").includes(query);
        row.hidden = !matches;
        if (matches) visible += 1;
      });
      count.textContent = visible + " dari " + list.querySelectorAll("[data-user-row]").length + " pengguna";
      empty.hidden = visible !== 0;
      if (!query && list.querySelectorAll("[data-user-row]").length === initialTotal) {
        count.textContent = initialTotal + " dari " + initialTotal + " pengguna";
      }
    }

    search.addEventListener("input", updateUsers);
    list.addEventListener("click", function (event) {
      const button = event.target.closest("[data-delete-user]");
      if (!button) return;
      if (!window.confirm("Hapus pengguna ini dari daftar contoh?")) return;
      button.closest("[data-user-row]").remove();
      updateUsers();
    });
  }

  const seasonButtons = document.querySelectorAll("[data-season-select]");
  if (seasonButtons.length) {
    function selectSeason(key) {
      seasonButtons.forEach(function (button) {
        const selected = button.dataset.seasonSelect === key;
        button.classList.toggle("is-selected", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
      document.querySelectorAll("[data-reference-season]").forEach(function (section) {
        section.hidden = section.dataset.referenceSeason !== key;
      });
    }

    seasonButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        selectSeason(button.dataset.seasonSelect);
      });
    });

    document.querySelectorAll("[data-reference-season]").forEach(function (section) {
      const colorInput = section.querySelector('input[type="color"]');
      const hexOutput = section.querySelector("[data-color-hex]");
      const form = section.querySelector("[data-color-form]");
      const grid = section.querySelector("[data-color-grid]");
      const feedback = section.querySelector("[data-reference-feedback]");

      function updateColorCount() {
        const seasonButton = document.querySelector('[data-season-select="' + section.dataset.referenceSeason + '"]');
        seasonButton.querySelector("[data-color-count]").textContent = grid.querySelectorAll("[data-color-card]").length;
      }

      colorInput.addEventListener("input", function () {
        hexOutput.value = colorInput.value.toUpperCase();
        hexOutput.textContent = colorInput.value.toUpperCase();
      });

      form.addEventListener("submit", function (event) {
        event.preventDefault();
        const name = form.elements.name.value.trim();
        const color = colorInput.value.toUpperCase();
        if (!name) return;
        const card = document.createElement("article");
        card.className = "reference-color-card";
        card.dataset.colorCard = "";
        card.innerHTML = '<span class="reference-color-card__swatch" data-color-swatch></span>' +
          '<strong data-color-name></strong><div class="reference-color-card__bottom">' +
          '<code data-color-value></code><span class="reference-color-actions">' +
          '<button type="button" data-edit-color aria-label="Ubah warna" title="Ubah warna">♢</button>' +
          '<button type="button" data-remove-color aria-label="Hapus warna" title="Hapus warna">♧</button>' +
          "</span></div>";
        card.querySelector("[data-color-name]").textContent = name;
        card.querySelector("[data-color-value]").textContent = color;
        card.querySelector("[data-color-swatch]").style.setProperty("--swatch-color", color);
        grid.append(card);
        updateColorCount();
        form.reset();
        colorInput.value = "#B55F42";
        hexOutput.value = "#B55F42";
        hexOutput.textContent = "#B55F42";
        feedback.textContent = "Warna ditambahkan untuk pratinjau ini.";
      });

      grid.addEventListener("click", function (event) {
        const button = event.target.closest("button");
        if (!button) return;
        const card = button.closest("[data-color-card]");
        if (button.hasAttribute("data-remove-color")) {
          card.remove();
          updateColorCount();
          feedback.textContent = "Warna dihapus dari pratinjau ini.";
          return;
        }
        if (button.hasAttribute("data-edit-color")) {
          const name = window.prompt("Nama warna:", card.querySelector("[data-color-name]").textContent);
          if (name === null) return;
          const color = window.prompt("Kode warna HEX:", card.querySelector("[data-color-value]").textContent);
          if (color === null) return;
          if (!/^#[0-9a-f]{6}$/i.test(color.trim())) {
            feedback.textContent = "Kode warna harus berupa HEX, contoh #B55F42.";
            return;
          }
          const normalizedColor = color.trim().toUpperCase();
          card.querySelector("[data-color-name]").textContent = name.trim() || "Warna tanpa nama";
          card.querySelector("[data-color-value]").textContent = normalizedColor;
          card.querySelector(".reference-color-card__swatch").style.setProperty("--swatch-color", normalizedColor);
          feedback.textContent = "Warna diperbarui untuk pratinjau ini.";
        }
      });

      section.querySelectorAll("[data-reference-tab]").forEach(function (tab) {
        tab.addEventListener("click", function () {
          const selectedView = tab.dataset.referenceTab;
          section.querySelectorAll("[data-reference-tab]").forEach(function (otherTab) {
            const selected = otherTab === tab;
            otherTab.classList.toggle("is-active", selected);
            otherTab.setAttribute("aria-selected", String(selected));
          });
          section.querySelectorAll("[data-reference-view]").forEach(function (view) {
            view.hidden = view.dataset.referenceView !== selectedView;
          });
        });
      });
    });
  }

  const rangeButtons = document.querySelectorAll("[data-stat-range]");
  if (rangeButtons.length) {
    const chart = document.querySelector("[data-stat-chart]");
    const columns = Array.from(chart.querySelectorAll(".bar-column"));
    const yLabels = Array.from(document.querySelectorAll(".bar-chart__y span"));
    const subtitle = document.querySelector("[data-chart-subtitle]");
    const average = document.querySelector("[data-average]");
    const averageUnit = document.querySelector("[data-average-unit]");
    const title = document.getElementById("trend-title");
    const labels = {
      monthly: ["Okt", "Nov", "Des", "Jan", "Feb", "Mar"],
      daily: ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab"],
    };
    const scaleLabels = {
      monthly: ["1000", "750", "500", "250", "0"],
      daily: ["200", "150", "100", "50", "0"],
    };

    function setRange(range) {
      const maximum = range === "monthly" ? 1000 : 200;
      rangeButtons.forEach(function (button) {
        button.setAttribute("aria-pressed", String(button.dataset.statRange === range));
      });
      columns.forEach(function (column, index) {
        const value = Number(column.dataset[range === "monthly" ? "month" : "day"]);
        column.querySelector("span").textContent = value;
        column.querySelector("i").style.setProperty("--bar-height", (value / maximum * 100) + "%");
        column.querySelector("small").textContent = labels[range][index];
      });
      yLabels.forEach(function (label, index) {
        label.textContent = scaleLabels[range][index];
      });
      chart.setAttribute("aria-label", range === "monthly" ? "Grafik contoh analisis bulanan" : "Grafik contoh analisis harian");
      title.textContent = range === "monthly" ? "Tren analisis bulanan" : "Tren analisis harian";
      subtitle.textContent = range === "monthly" ? "Jumlah foto yang berhasil diproses" : "Jumlah foto yang berhasil diproses setiap hari";
      average.textContent = range === "monthly" ? "692" : "143";
      averageUnit.textContent = range === "monthly" ? "/bulan" : "/hari";
    }

    rangeButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        setRange(button.dataset.statRange);
      });
    });
  }
});
