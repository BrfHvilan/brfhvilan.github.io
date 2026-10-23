/* ==========================================================
   BRF Hvilan – formulär för att välja arbetsgrupp
   Formuläret skickar ingenting från sajten. När man klickar på
   knappen öppnas besökarens eget mejlprogram (mailto) med ett
   färdigt mejl till styrelsen. Inget sparas.
   Texterna väljs efter sidans språk (<html lang="sv"> eller "en").
   ========================================================== */
(function () {
  var ADRESS = 'styrelsenhvilan@gmail.com';

  var TEXTER = {
    sv: {
      amne: 'Arbetsgrupp: ',
      inledning: 'Hej, jag vill ingå i ',
      namn: 'Namn: ',
      lagenhet: 'Lägenhetsnummer: ',
      meddelande: 'Meddelande: ',
      felNamn: 'Fyll i ditt namn.',
      felGrupp: 'Välj en arbetsgrupp.',
      ofullstandigt: 'Formuläret är inte komplett. Rätta det som är markerat och försök igen.',
      oppnas: 'Ditt mejlprogram öppnas nu med ett färdigt mejl. Kontrollera innehållet och tryck på Skicka i mejlprogrammet.'
    },
    en: {
      amne: 'Working group: ',
      inledning: 'Hi, I would like to join the ',
      namn: 'Name: ',
      lagenhet: 'Apartment number: ',
      meddelande: 'Message: ',
      felNamn: 'Please enter your name.',
      felGrupp: 'Please choose a working group.',
      ofullstandigt: 'The form is not complete. Please correct the highlighted fields and try again.',
      oppnas: 'Your email program will now open with a ready-made email. Check the content and press Send in your email program.'
    }
  };

  var t = TEXTER[document.documentElement.lang === 'en' ? 'en' : 'sv'];

  function visaFel(felElement, text) {
    felElement.textContent = text;
    felElement.hidden = !text;
  }

  var formular = document.querySelectorAll('form[data-arbetsgrupp-formular]');

  Array.prototype.forEach.call(formular, function (form) {
    var namnFalt = form.querySelector('[name="namn"]');
    var lagenhetFalt = form.querySelector('[name="lagenhet"]');
    var meddelandeFalt = form.querySelector('[name="meddelande"]');
    var gruppFaltset = form.querySelector('fieldset');
    var namnFel = form.querySelector('[data-fel="namn"]');
    var gruppFel = form.querySelector('[data-fel="grupp"]');
    var status = form.querySelector('.formular-status');

    form.addEventListener('submit', function (handelse) {
      handelse.preventDefault();

      var namn = namnFalt.value.trim();
      var valdGrupp = form.querySelector('[name="grupp"]:checked');
      var forstaFel = null;

      if (!namn) {
        namnFalt.setAttribute('aria-invalid', 'true');
        visaFel(namnFel, t.felNamn);
        forstaFel = namnFalt;
      } else {
        namnFalt.removeAttribute('aria-invalid');
        visaFel(namnFel, '');
      }

      if (!valdGrupp) {
        gruppFaltset.setAttribute('aria-invalid', 'true');
        visaFel(gruppFel, t.felGrupp);
        forstaFel = forstaFel || form.querySelector('[name="grupp"]');
      } else {
        gruppFaltset.removeAttribute('aria-invalid');
        visaFel(gruppFel, '');
      }

      if (forstaFel) {
        status.textContent = t.ofullstandigt;
        forstaFel.focus();
        return;
      }

      var grupp = valdGrupp.value;
      var brodtext = [
        t.inledning + grupp + '.',
        '',
        t.namn + namn,
        t.lagenhet + lagenhetFalt.value.trim(),
        t.meddelande + meddelandeFalt.value.trim()
      ].join('\r\n');

      status.textContent = t.oppnas;
      window.location.href = 'mailto:' + ADRESS +
        '?subject=' + encodeURIComponent(t.amne + grupp) +
        '&body=' + encodeURIComponent(brodtext);
    });
  });
})();
