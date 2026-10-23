/* ==========================================================
   BRF Hvilan – språkval (svenska/engelska)
   - Sparar besökarens val i localStorage (nyckeln "lang") när
     man klickar på en länk med data-lang="sv" eller data-lang="en".
   - På de två startsidorna (index.html och en/index.html, märkta med
     data-startsida på <html>) skickas besökaren till sitt sparade språk.
     Undersidor styrs aldrig om, så att delade länkar alltid fungerar.
   Sidan fungerar som vanligt även om JavaScript eller localStorage saknas.
   ========================================================== */
(function () {
  var rot = document.documentElement;
  var startsida = rot.getAttribute('data-startsida');      // "sv" eller "en", bara på startsidorna
  var annanStartsida = rot.getAttribute('data-annan-startsida');

  var sparat = null;
  try {
    sparat = window.localStorage.getItem('lang');
  } catch (e) {
    sparat = null;
  }

  if (startsida && annanStartsida && (sparat === 'sv' || sparat === 'en') && sparat !== startsida) {
    window.location.replace(annanStartsida);
    return;
  }

  document.addEventListener('click', function (handelse) {
    var lank = handelse.target.closest ? handelse.target.closest('a[data-lang]') : null;
    if (!lank) {
      return;
    }
    try {
      window.localStorage.setItem('lang', lank.getAttribute('data-lang'));
    } catch (e) {
      /* Webbläsaren tillåter inte lagring – länken fungerar ändå. */
    }
  });
})();
