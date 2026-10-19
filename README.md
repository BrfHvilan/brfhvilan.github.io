# BRF Hvilan – hemsida

En enkel hemsida i ren HTML och CSS. Den behöver inga program, ramverk eller databaser:
filerna kan öppnas direkt i webbläsaren och laddas upp som de är till ett webbhotell.

## Filer och mappar

| Fil / mapp        | Innehåll                                                   |
|-------------------|------------------------------------------------------------|
| `index.html`      | Startsidan – om föreningen, bild och de 3 senaste nyheterna |
| `aktuellt.html`   | Alla nyheter från styrelsen, nyaste överst                 |
| `maklare.html`    | Faktaruta och dokument för mäklare                         |
| `medlemmar.html`  | Trivselregler, felanmälan, tvättstuga, sopor, parkering, FAQ |
| `dokument.html`   | Lista med PDF-länkar                                       |
| `kontakt.html`    | Kontaktuppgifter och felanmälan                            |
| `style.css`       | Utseendet (färger, typsnitt, mobilanpassning) för alla sidor |
| `dokument/`       | Här ska alla PDF-filer ligga                               |
| `bilder/`         | Här ska bilder ligga                                       |

## Öppna sidan

Dubbelklicka på `index.html`. Den öppnas i din vanliga webbläsare. Alla länkar mellan
sidorna fungerar direkt från datorn.

## Redigera

Öppna `.html`-filerna i en textredigerare, t.ex. **Visual Studio Code** (gratis) eller
Anteckningar. Använd inte Word – det förstör koden.

Spara filen och tryck **F5** i webbläsaren för att se ändringen.

> Ändra bara text *mellan* taggarna, t.ex. `<p>Det här är text</p>`. Rör inte
> `<` `>` eller det som står inne i dem om du inte vet vad det gör.

### 1. Fyll i uppgifterna som saknas

Allt som står inom **[hakparenteser]** är platshållare som ska ersättas. Sök efter `[`
i varje fil (Ctrl+F) så hittar du dem. Ta bort hakparenteserna när du fyller i.

Exempel: `Byggår: [X]` → `Byggår: 1928`

Uppgifter som finns på **alla** sidor (sidfoten: adress, org.nr, e-post, telefon) måste
ändras i alla sex filerna. Tips i VS Code: *Edit → Replace in Files* (Ctrl+Shift+H)
ersätter i alla filer på en gång.

### 2. Lägga in en nyhet efter styrelsemötet

1. Öppna `aktuellt.html`.
2. Hitta `<ul class="nyheter">`. Kopiera ett helt nyhetsblock:
   ```html
   <li class="nyhet">
     <time datetime="2026-10-15">15 oktober 2026</time>
     <h2>Rubrik</h2>
     <p>Text om nyheten.</p>
   </li>
   ```
3. Klistra in det **direkt under** `<ul class="nyheter">` så att det hamnar överst.
4. Ändra datum, rubrik och text. `datetime="ÅÅÅÅ-MM-DD"` är för datorer och sökmotorer,
   texten mellan taggarna är det besökaren ser.
5. Vill du ha flera stycken, lägg till fler `<p>…</p>`-rader i blocket.
6. Öppna `index.html` och gör samma sak under **Senaste nytt** – men ta bort det
   *nedersta* blocket så att det alltid är 3 nyheter där. (På startsidan används `<h3>`
   i stället för `<h2>`.)
7. Uppdatera "Senast uppdaterad" i sidfoten om ni använder den.

### 3. Lägga upp ett dokument (PDF)

1. Lägg PDF-filen i mappen `dokument/`. Använd **små bokstäver, inga mellanslag och
   inga å/ä/ö** i filnamnet, t.ex. `arsredovisning-2025.pdf`.
2. Öppna `dokument.html`, kopiera en befintlig rad, t.ex.
   ```html
   <li><a href="dokument/arsredovisning-2025.pdf">Årsredovisning 2025 <span class="typ">PDF</span></a></li>
   ```
   och ändra filnamn och text.
3. **Ny årsredovisning?** Ändra även länken under *Dokument* på `maklare.html`, så att
   mäklarna alltid får den senaste.

Kontrollera att länken fungerar genom att klicka på den i webbläsaren.

### 4. Byta bild på startsidan

Bilden visas i sin naturliga storlek till höger om texten om föreningen (i mobilen
ovanför texten). Den beskärs aldrig och blir aldrig större än den är.

1. Lägg bilden i mappen `bilder/`, t.ex. `bilder/huset.jpg`. Max ca 450 px bred passar
   bra bredvid texten. Håll den under 300 kB (komprimera på t.ex. squoosh.app).
2. I `index.html`, ändra `src="bilder/fasad.jpg"` till den nya filen, och ändra
   `width` och `height` till bildens mått i pixlar.
3. Ändra `alt="…"` till en kort beskrivning av bilden (läses upp för synskadade) och
   texten i `<figcaption>`.

### 5. Uppdatera faktarutan för mäklare

Faktarutan finns i `maklare.html` mellan `<dl>` och `</dl>`. Varje rad är ett par:

```html
<dt>Hiss</dt>
<dd>Ja</dd>
```

`<dt>` är rubriken, `<dd>` är värdet. Ny rad = kopiera ett par och ändra. Gå igenom
rutan efter varje stämma och när avgifter, renoveringar eller underhållsplan ändras.

### 6. Ändra menyn

Menyn finns överst i varje fil mellan `SIDHUVUD` och `SLUT SIDHUVUD`, och sidfoten
mellan `SIDFOT` och `SLUT SIDFOT`. De måste ändras **i alla sex filerna** så att de ser
likadana ut. `aria-current="page"` markerar vilken sida man är på – den ska stå på
olika länkar i olika filer.

### 7. Ändra färger

Färgerna står överst i `style.css`:

```css
--gron: #2E5E4E;   /* huvudfärg */
--text: #222222;
```

## Publicera

Ladda upp **alla** filer och mappar (inkl. `style.css`, `bilder/` och `dokument/`)
till webbhotellets webbmapp (ofta `public_html` eller `www`) med webbhotellets
filhanterare eller ett FTP-program, t.ex. FileZilla. Behåll samma mappstruktur.
`index.html` blir startsidan automatiskt.

Efter varje uppdatering laddar du bara upp de filer du har ändrat.

Tänk på att allt som läggs på hemsidan är offentligt. Lägg inte upp protokoll med
personuppgifter, medlemsförteckningar eller annat som inte ska vara publikt.

## Checklista efter styrelsemöte

- [ ] Ny nyhet i `aktuellt.html`
- [ ] Samma nyhet i `index.html`, ta bort den äldsta av de tre
- [ ] Nya dokument i `dokument/` och länk i `dokument.html`
- [ ] Ändringar i faktarutan i `maklare.html` (avgift, underhåll, renoveringar)
- [ ] Ny styrelse? Uppdatera `kontakt.html`
- [ ] "Senast uppdaterad" i sidfoten
- [ ] Ladda upp ändrade filer
