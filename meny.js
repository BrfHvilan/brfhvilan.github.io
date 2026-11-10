/* Mobilmeny: på smala skärmar fälls huvudmenyn ihop bakom knappen "Meny".
   Utan JavaScript visas menyn alltid utfälld, så sajten fungerar ändå. */
(function () {
  var knapp = document.querySelector(".menyknapp");
  var meny = document.getElementById("huvudmeny");
  if (!knapp || !meny) return;

  document.documentElement.classList.add("js-meny");
  knapp.hidden = false;

  function satt(oppen) {
    knapp.setAttribute("aria-expanded", String(oppen));
    meny.classList.toggle("oppen", oppen);
  }

  knapp.addEventListener("click", function () {
    satt(knapp.getAttribute("aria-expanded") !== "true");
  });

  // Escape stänger menyn och lämnar fokus på knappen
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && knapp.getAttribute("aria-expanded") === "true") {
      satt(false);
      knapp.focus();
    }
  });
})();
