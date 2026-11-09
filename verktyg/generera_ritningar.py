"""Genererar ritningssidorna för BRF Hvilan från mapparna med bygglovsritningar.

Kör från projektmappen:

    python verktyg/generera_ritningar.py
    python verktyg/generera_ritningar.py --kalla "C:/sökväg/till/mappen/med/vilan 16 och vilan 17"

Skriptet
  1. kopierar TIF- och PDF-originalen till dokument/ritningar/vilan-16/<kategori>/ (och vilan-17),
  2. gör en förlustfri 1-bitars PNG av varje TIF, en JPG-snabbvisning (max 3000 px bred)
     och en miniatyr (400 px bred) per ritning,
  3. skriver ritningar-vilan-16.html, ritningar-vilan-17.html och de engelska motsvarigheterna i en/.

Bilder som redan finns och är nyare än källfilen görs inte om, så det går snabbt att köra
skriptet igen när nya ritningar har lagts till i källmapparna. Sidhuvud och sidfot hämtas från
dokument.html respektive en/dokument.html, så de håller sig synkade med resten av sajten.
Kräver Python 3 och Pillow (pip install pillow).
"""

import argparse
import datetime
import html
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # ritningarna är upp till ca 12 500 × 9 000 px

REPO = Path(__file__).resolve().parent.parent
STANDARDKALLA = Path.home() / "OneDrive - Iniziato Consulting AB" / "Skrivbordet"
UTMAPP = REPO / "dokument" / "ritningar"

SNABB_MAXBREDD = 3000
MINIATYR_BREDD = 400
JPG_KVALITET = 80

FASTIGHETER = [
    {"nr": "16", "mapp": "vilan 16", "adress": "Roslagsgatan 37"},
    {"nr": "17", "mapp": "vilan 17", "adress": "Roslagsgatan 35"},
]

# (mappnamn, id, svensk rubrik, engelsk rubrik) i den ordning de visas
KATEGORIER = [
    ("Ursprungsritningar", "ursprungsritningar", "Ursprungsritningar (nybyggnad)",
     "Original drawings (new construction)"),
    ("Planritningar", "planritningar", "Planritningar", "Floor plans"),
    ("Fasader_fonster", "fasader-fonster", "Fasader och fönster", "Façades and windows"),
    ("Konstruktionsritningar", "konstruktionsritningar", "Konstruktionsritningar",
     "Structural drawings"),
    ("VVS_VA_ritningar", "vvs-va", "VVS- och VA-ritningar",
     "Plumbing, water and drainage drawings"),
    ("Ventilation_ritningar", "ventilation", "Ventilationsritningar", "Ventilation drawings"),
    ("Rokkanaler_eldstader", "rokkanaler-eldstader", "Rökkanaler och eldstäder",
     "Flues and fireplaces"),
    ("Lagenhetsrenoveringar", "lagenhetsrenoveringar",
     "Lägenhetsrenoveringar (bygglovsritningar för enskilda lägenheter)",
     "Apartment renovations (building permit drawings for individual apartments)"),
]

# Hus i Lagenhetsrenoveringar: (filnamnsprefix, svensk rubrik, engelsk rubrik)
HUS = [
    ("Gatuhus", "Gatuhus", "Street building (Gatuhus)"),
    ("Gardshus", "Gårdshus", "Courtyard building (Gårdshus)"),
    ("Okant-hus", "Okänt hus", "Building not specified"),
]

# Svenska tecken återställs bara i visade titlar, aldrig i filnamn
SVENSKA_ORD = [
    ("vaster", "väster"), ("oster", "öster"), ("soder", "söder"), ("kallare", "källare"),
    ("fonster", "fönster"), ("lagenhet", "lägenhet"), ("vaning", "våning"),
    ("gardshus", "gårdshus"), ("rokkanal", "rökkanal"),
]

MANADER_SV = ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti",
              "september", "oktober", "november", "december"]
MANADER_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]


# ---------------------------------------------------------------- titlar

def aterstall_svenska(text):
    for utan, med in SVENSKA_ORD:
        def ersatt(m, med=med):
            return med[0].upper() + med[1:] if m.group(0)[0].isupper() else med
        text = re.sub(utan, ersatt, text, flags=re.IGNORECASE)
    return text


def titel_fran(delar):
    return aterstall_svenska(" ".join(delar)) if delar else "(utan beskrivning)"


def vaning_text(vaning, sprak):
    if vaning == "BV":
        return "BV" if sprak == "sv" else "Ground floor (BV)"
    m = re.fullmatch(r"(\d+)tr", vaning)
    if m:
        return f"{m.group(1)} tr" if sprak == "sv" else f"Floor {m.group(1)} tr"
    return vaning


def vaning_ordning(vaning):
    if vaning == "BV":
        return 0
    m = re.fullmatch(r"(\d+)tr", vaning)
    return int(m.group(1)) if m else 99


# ---------------------------------------------------------------- inventering

def inventera(kategorimapp, ar_lagenhet):
    """Returnerar ritningarna i en kategorimapp och vilka källfiler som hör till varje."""
    filer = sorted(p for p in kategorimapp.iterdir() if p.is_file())
    original = [p for p in filer if p.suffix.lower() in (".tif", ".pdf")]
    jpgar = [p for p in filer if p.suffix.lower() == ".jpg"]
    anvanda = set()
    ritningar = []

    for orig in original:
        bas = orig.stem
        if orig.suffix.lower() == ".tif":
            hor_till = [j for j in jpgar if j.stem.startswith(bas + "_")]
        else:
            hor_till = [j for j in jpgar
                        if j.stem == bas or re.fullmatch(re.escape(bas) + r"_sid\d+", j.stem)]
        anvanda.update(hor_till)
        ritningar.append(tolka(orig, hor_till, ar_lagenhet))

    for jpg in jpgar:
        if jpg not in anvanda:
            ritningar.append(tolka(jpg, [], ar_lagenhet))
            anvanda.add(jpg)

    okanda = [p for p in filer if p.suffix.lower() not in (".tif", ".pdf", ".jpg")]
    return ritningar, okanda


def tolka(kalla, jpgar, ar_lagenhet):
    typ = kalla.suffix.lower().lstrip(".")  # tif, pdf eller jpg
    delar = kalla.stem.split("_")
    r = {"kalla": kalla, "typ": typ, "kallfiler": [kalla] + list(jpgar),
         "hus": None, "vaning": None, "ar": None, "diarie": None, "arkiv": None, "sidor": 0}

    if ar_lagenhet:
        r["hus"], r["vaning"], r["ar"] = delar[0], delar[1], delar[2]
        delar = delar[3:]

    if typ == "tif":
        beskrivning = jpgar[0].stem[len(kalla.stem) + 1:].split("_") if jpgar else []
        if len(delar) == 1:
            r["arkiv"] = delar[0]
        else:
            r["diarie"], r["arkiv"] = "_".join(delar[:-1]), delar[-1]
        r["forsta_sida"] = None
    elif typ == "pdf":
        r["diarie"], beskrivning = delar[0], delar[1:]
        sidor = sorted(jpgar, key=lambda j: int(re.search(r"_sid(\d+)$", j.stem).group(1))
                       if re.search(r"_sid(\d+)$", j.stem) else 0)
        r["sidor"] = len(sidor)
        r["forsta_sida"] = sidor[0] if sidor else None
    else:  # ritning som bara finns som JPG
        r["diarie"], r["arkiv"], beskrivning = delar[0], delar[1], delar[2:]
        r["forsta_sida"] = kalla

    r["titel"] = titel_fran(beskrivning)
    return r


# ---------------------------------------------------------------- bilder

def ar_aktuell(mal, kalla):
    return mal.exists() and mal.stat().st_mtime >= kalla.stat().st_mtime


def skala(bild, bredd):
    if bild.width <= bredd:
        return bild.copy()
    hojd = round(bild.height * bredd / bild.width)
    return bild.resize((bredd, hojd), Image.LANCZOS)


def skapa_bilder(r, malmapp):
    """Kopierar original och gör PNG, snabbvisning och miniatyr. Returnerar filnamnen."""
    kalla = r["kalla"]
    bas = kalla.stem
    namn = {"snabb": f"{bas}_visning.jpg", "miniatyr": f"{bas}_miniatyr.jpg",
            "png": None, "original": None}

    if r["typ"] in ("tif", "pdf"):
        namn["original"] = kalla.name
        mal = malmapp / kalla.name
        if not (mal.exists() and mal.stat().st_size == kalla.stat().st_size):
            shutil.copy2(kalla, mal)

    if r["typ"] == "tif":
        namn["png"] = f"{bas}.png"
        bildkalla = kalla
    else:
        bildkalla = r["forsta_sida"]

    behov = [malmapp / namn["snabb"], malmapp / namn["miniatyr"]]
    if namn["png"]:
        behov.append(malmapp / namn["png"])
    if bildkalla is None or all(ar_aktuell(p, bildkalla) for p in behov):
        return namn

    with Image.open(bildkalla) as bild:
        bild.load()
        if namn["png"]:
            # Förlustfri 1-bitars PNG direkt från TIF-filen
            bild.convert("1", dither=Image.Dither.NONE).save(
                malmapp / namn["png"], optimize=True, dpi=bild.info.get("dpi", (300, 300)))
        gra = bild.convert("L")
    snabb = skala(gra, SNABB_MAXBREDD)
    snabb.save(malmapp / namn["snabb"], quality=JPG_KVALITET, optimize=True, progressive=True)
    skala(snabb, MINIATYR_BREDD).save(malmapp / namn["miniatyr"], quality=JPG_KVALITET,
                                     optimize=True)
    return namn


# ---------------------------------------------------------------- HTML

def esc(text):
    return html.escape(text, quote=True)


def dagens_datum(sprak):
    d = datetime.date.today()
    if sprak == "sv":
        return f"{d.day} {MANADER_SV[d.month - 1]} {d.year}"
    return f"{d.day} {MANADER_EN[d.month - 1]} {d.year}"


def sidhuvud_och_sidfot(sprak, sidnamn):
    dokument = (REPO / ("dokument.html" if sprak == "sv" else "en/dokument.html")).read_text(
        encoding="utf-8")
    huvud = re.search(r"  <!-- ===== SIDHUVUD.*?SLUT SIDHUVUD ===== -->", dokument, re.S).group(0)
    fot = re.search(r"  <!-- ===== SIDFOT.*?SLUT SIDFOT ===== -->", dokument, re.S).group(0)
    huvud = huvud.replace('href="dokument.html" aria-current="page"',
                          'href="dokument.html" aria-current="true"')
    if sprak == "sv":
        huvud = huvud.replace('href="en/dokument.html"', f'href="en/{sidnamn}"')
        fot = re.sub(r"Senast uppdaterad: [^<]+", "Senast uppdaterad: " + dagens_datum("sv"), fot)
    else:
        huvud = huvud.replace('href="../dokument.html"', f'href="../{sidnamn}"')
        fot = re.sub(r"Last updated: [^<]+", "Last updated: " + dagens_datum("en"), fot)
    return huvud, fot


def ritning_html(r, namn, bildbas, sprak):
    mapp = bildbas
    snabb = f"{mapp}/{namn['snabb']}"
    miniatyr_fil = r["miniatyrfil"]
    with Image.open(miniatyr_fil) as m:
        b, h = m.size

    meta = []
    if r["hus"]:
        meta.append(vaning_text(r["vaning"], sprak))
        meta.append(r["ar"])
    if r["diarie"]:
        meta.append(("Diarienummer " if sprak == "sv" else "Case no. ") + r["diarie"])
    if r["arkiv"]:
        meta.append(("Arkivnummer " if sprak == "sv" else "Archive no. ") + r["arkiv"])
    if r["sidor"] > 1:
        meta.append(f"{r['sidor']} sidor" if sprak == "sv" else f"{r['sidor']} pages")

    t = {"sv": ("Visa (snabb)", "Visa i full upplösning", "Original"),
         "en": ("Quick view", "View in full resolution", "Original")}[sprak]
    lankar = [f'<a href="{esc(snabb)}">{t[0]}</a>']
    if namn["png"]:
        lankar.append(f'<a href="{esc(mapp + "/" + namn["png"])}">{t[1]}</a>')
    if namn["original"]:
        lankar.append(f'<a href="{esc(mapp + "/" + namn["original"])}">'
                      f'{t[2]} ({r["typ"].upper()})</a>')
    elif sprak == "sv":
        lankar.append('<span class="ritning-not">Endast visningskopia finns</span>')
    else:
        lankar.append('<span class="ritning-not">Only a viewing copy is available</span>')

    return (
        '          <li class="ritning">\n'
        f'            <a href="{esc(snabb)}" tabindex="-1" aria-hidden="true">'
        f'<img src="{esc(mapp + "/" + namn["miniatyr"])}" alt="" width="{b}" height="{h}" '
        'loading="lazy"></a>\n'
        f'            <p class="ritning-titel" lang="sv">{esc(r["titel"])}</p>\n'
        f'            <p class="ritning-meta">{esc(" · ".join(meta))}</p>\n'
        f'            <p class="ritning-lankar">{" ".join(lankar)}</p>\n'
        '          </li>\n'
    )


def lista_html(poster, bildbas, sprak):
    rader = "".join(ritning_html(r, n, f"{bildbas}/{r['kategorimapp']}", sprak) for r, n in poster)
    return f'        <ul class="ritningar">\n{rader}        </ul>\n'


def antal_text(n, sprak):
    if sprak == "sv":
        return f"{n} ritning" if n == 1 else f"{n} ritningar"
    return f"{n} drawing" if n == 1 else f"{n} drawings"


def skriv_sida(fast, kategorier, sprak):
    nr, adress = fast["nr"], fast["adress"]
    annan = next(f for f in FASTIGHETER if f is not fast)
    sidnamn = f"ritningar-vilan-{nr}.html"
    annan_sida = f"ritningar-vilan-{annan['nr']}.html"
    prefix = "" if sprak == "sv" else "../"
    bildbas = f"{prefix}dokument/ritningar/vilan-{nr}"
    huvud, fot = sidhuvud_och_sidfot(sprak, sidnamn)
    totalt = sum(len(p) for _, p in kategorier)

    if sprak == "sv":
        titel = f"Ritningar – {adress} (Vilan {nr})"
        beskrivning = f"Bygglovsritningar för {adress} (fastigheten Vilan {nr}), BRF Hvilan."
        ingress = (f"Här finns {antal_text(totalt, 'sv')} för {adress}, som är fastigheten "
                   f"Vilan {nr}. Ritningarna kommer från Stockholms stads bygglovsarkiv.")
        ruta = (f"Föreningen består av två fastigheter: <strong>Roslagsgatan 37 är Vilan 16</strong> "
                f"och <strong>Roslagsgatan 35 är Vilan 17</strong>. Den här sidan gäller "
                f"{adress} (Vilan {nr}). Ritningarna för {annan['adress']} (Vilan {annan['nr']}) "
                f'finns på <a href="{annan_sida}">en egen sida</a>. TIF och PDF är originalen från '
                f"arkivet, PNG och JPG är visningskopior. Klicka på en miniatyr för att se ritningen.")
        tillbaka = '<a href="dokument.html">← Tillbaka till Dokument</a>'
        innehall = "Innehåll"
        skip, lang_attr = "Hoppa till innehållet", "sv"
        toc_label = "Innehåll på sidan"
    else:
        titel = f"Drawings – {adress} (Vilan {nr})"
        beskrivning = f"Building permit drawings for {adress} (the property Vilan {nr}), BRF Hvilan."
        ingress = (f"This page contains {antal_text(totalt, 'en')} for {adress}, which is the "
                   f"property Vilan {nr}. The drawings come from the City of Stockholm's building "
                   f"permit archive and have Swedish titles.")
        ruta = (f"The cooperative consists of two properties: <strong>Roslagsgatan 37 is Vilan 16</strong> "
                f"and <strong>Roslagsgatan 35 is Vilan 17</strong>. This page covers {adress} "
                f"(Vilan {nr}). The drawings for {annan['adress']} (Vilan {annan['nr']}) are on "
                f'<a href="{annan_sida}">a separate page</a>. TIF and PDF files are the originals '
                f"from the archive; PNG and JPG files are viewing copies. Click a thumbnail to view "
                f"the drawing.")
        tillbaka = '<a href="dokument.html">← Back to Documents</a>'
        innehall = "Contents"
        skip, lang_attr = "Skip to content", "en"
        toc_label = "Contents of this page"

    toc = "".join(
        f'          <li><a href="#{k[1]}">{esc(k[2] if sprak == "sv" else k[3])}</a> '
        f"({antal_text(len(p), sprak)})</li>\n" for k, p in kategorier)

    sektioner = []
    for k, poster in kategorier:
        rubrik = k[2] if sprak == "sv" else k[3]
        del_html = (f'      <details class="ritningskategori" id="{k[1]}" open>\n'
                    f'        <summary><h2>{esc(rubrik)} <span class="antal">'
                    f"({antal_text(len(poster), sprak)})</span></h2></summary>\n")
        if not poster:
            del_html += ("        <p>Inga ritningar i den här kategorin.</p>\n" if sprak == "sv"
                         else "        <p>No drawings in this category.</p>\n")
        elif k[0] == "Lagenhetsrenoveringar":
            for prefix_hus, hus_sv, hus_en in HUS:
                i_hus = [(r, n) for r, n in poster if r["hus"] == prefix_hus]
                if i_hus:
                    del_html += f"        <h3>{esc(hus_sv if sprak == 'sv' else hus_en)}</h3>\n"
                    del_html += lista_html(i_hus, bildbas, sprak)
            ovriga = [(r, n) for r, n in poster if r["hus"] not in [h[0] for h in HUS]]
            if ovriga:
                del_html += "        <h3>Övrigt</h3>\n" if sprak == "sv" else "        <h3>Other</h3>\n"
                del_html += lista_html(ovriga, bildbas, sprak)
        else:
            del_html += lista_html(poster, bildbas, sprak)
        del_html += "      </details>\n"
        sektioner.append(del_html)

    sida = f"""<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BRF Hvilan – {esc(titel)}</title>
  <meta name="description" content="{esc(beskrivning)}">
  <link rel="stylesheet" href="{prefix}style.css">
  <script src="{prefix}sprak.js"></script>
</head>
<body>
  <!-- GENERERAD SIDA: ändra inte för hand. Kör python verktyg/generera_ritningar.py i stället. -->
  <a class="hoppa" href="#innehall">{skip}</a>

{huvud}

  <main id="innehall">
    <div class="wrap">
      <p class="meta">{tillbaka}</p>
      <h1>{esc(titel)}</h1>
      <p class="ingress">{ingress}</p>

      <div class="ruta">
        <p>{ruta}</p>
      </div>

      <nav class="innehallsforteckning" aria-label="{toc_label}">
        <h2>{innehall}</h2>
        <ul>
{toc}        </ul>
      </nav>

{"".join(sektioner)}    </div>
  </main>

{fot}
</body>
</html>
"""
    malfil = REPO / sidnamn if sprak == "sv" else REPO / "en" / sidnamn
    malfil.write_text(sida, encoding="utf-8", newline="\n")
    return malfil


# ---------------------------------------------------------------- huvudprogram

def main():
    tolkare = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    tolkare.add_argument("--kalla", type=Path, default=STANDARDKALLA,
                         help="mappen som innehåller 'vilan 16' och 'vilan 17'")
    args = tolkare.parse_args()

    sammanstallning = []
    for fast in FASTIGHETER:
        kallmapp = args.kalla / fast["mapp"]
        if not kallmapp.is_dir():
            sys.exit(f"Hittar inte {kallmapp}")
        okanda_mappar = sorted(p.name for p in kallmapp.iterdir()
                               if p.is_dir() and p.name not in [k[0] for k in KATEGORIER])
        kategorier = []
        for k in KATEGORIER:
            kmapp = kallmapp / k[0]
            malmapp = UTMAPP / f"vilan-{fast['nr']}" / k[0]
            malmapp.mkdir(parents=True, exist_ok=True)
            ritningar, okanda = inventera(kmapp, k[0] == "Lagenhetsrenoveringar") \
                if kmapp.is_dir() else ([], [])
            if okanda:
                print(f"  OBS: hoppar över filer som inte är TIF/PDF/JPG i {kmapp}: "
                      + ", ".join(p.name for p in okanda))
            if k[0] == "Lagenhetsrenoveringar":
                husordning = {h[0]: i for i, h in enumerate(HUS)}
                ritningar.sort(key=lambda r: (husordning.get(r["hus"], 99),
                                              vaning_ordning(r["vaning"]), r["ar"],
                                              r["kalla"].name.lower()))
            else:
                ritningar.sort(key=lambda r: r["kalla"].name.lower())
            poster = []
            for i, r in enumerate(ritningar, 1):
                print(f"\r  Vilan {fast['nr']} {k[0]}: {i}/{len(ritningar)}   ", end="", flush=True)
                namn = skapa_bilder(r, malmapp)
                r["kategorimapp"] = k[0]
                r["miniatyrfil"] = malmapp / namn["miniatyr"]
                poster.append((r, namn))
            if ritningar:
                print()
            kategorier.append((k, poster))
        for sprak in ("sv", "en"):
            print(f"  Skrev {skriv_sida(fast, kategorier, sprak).relative_to(REPO)}")
        sammanstallning.append((fast, kategorier, okanda_mappar))

    print("\nSammanställning")
    for fast, kategorier, okanda_mappar in sammanstallning:
        kallfiler = sum(len(r["kallfiler"]) for _, p in kategorier for r, _ in p)
        ritningar = sum(len(p) for _, p in kategorier)
        print(f"  Vilan {fast['nr']} ({fast['adress']}): {ritningar} ritningar från "
              f"{kallfiler} källfiler")
        for k, p in kategorier:
            print(f"    {k[2]:<68} {len(p):>4}")
        if okanda_mappar:
            print(f"    Ej kategorimappar, hoppades över: {', '.join(okanda_mappar)}")


if __name__ == "__main__":
    main()
