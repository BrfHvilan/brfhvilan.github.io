# BRF Hvilan – hemsida

Statisk sajt i ren HTML och CSS (plus `sprak.js` för språkval), publicerad med GitHub Pages på https://brfhvilan.se.

- Språkväljaren (rutan "Välj språk" / "Choose language" med flaggor) finns på båda startsidorna, `index.html` och `en/index.html`, och ska hållas synkad mellan dem; växlaren SV | EN i sidhuvudet finns på alla sidor och pekar på motsvarande sida i det andra språket.
- Formuläret för arbetsgrupper finns på `index.html`, `medlemmar.html`, `en/index.html` och `en/medlemmar.html` och ska vara likadant på alla fyra; logiken finns i `arbetsgrupp.js`, som bara öppnar besökarens mejlprogram (mailto) och aldrig skickar eller sparar något.
