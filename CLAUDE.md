# BRF Hvilan – hemsida

Statisk sajt i ren HTML och CSS (plus `sprak.js` för språkval), publicerad med GitHub Pages på https://brfhvilan.se.

- Språkväljaren (rutan "Välj språk" / "Choose language" med flaggor) finns på båda startsidorna, `index.html` och `en/index.html`, och ska hållas synkad mellan dem; växlaren SV | EN i sidhuvudet finns på alla sidor och pekar på motsvarande sida i det andra språket.
- Ritningssidorna (`ritningar-vilan-16.html`, `ritningar-vilan-17.html` och samma i `en/`) och bilderna i `dokument/ritningar/` genereras med `python verktyg/generera_ritningar.py` (kräver Pillow) från mapparna "vilan 16" och "vilan 17"; ändra dem inte för hand. Roslagsgatan 37 = Vilan 16, Roslagsgatan 35 = Vilan 17.
- Arbetsgrupperna har tre knappar "Gå med i grupp" / "Join group" (`div.grupper`) som länkar till respektive grupps WhatsApp-grupp; grupper utan länk visas som grå `span.knapp.knapp-inaktiv`. Knapparna finns på `index.html`, `medlemmar.html`, `en/index.html` och `en/medlemmar.html` och ska vara likadana på alla fyra. Det finns inget formulär.
