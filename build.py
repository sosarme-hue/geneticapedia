#!/usr/bin/env python3
"""Geneticapedia · generador estático.

Uso: python3 build.py  ->  escribe la web en dist/
Contenido en src/es/**.md y src/en/**.md (cabecera --- clave: valor ---).
"""
import html, json, math, os, re, shutil
from datetime import date
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "dist")
SITE = "https://geneticapedia.com/"
TODAY = "2026-11-20"
MAIL = "partenopides@gmail.com"
import hashlib
V = hashlib.md5(b"".join(open(os.path.join(ROOT, "assets", f), "rb").read() for f in ("site.css", "app.js"))).hexdigest()[:8]

# ----- secciones -----
SECTIONS = {
    "es": [
        ("enfermedades", "Enfermedades", "Enfermedades y síndromes genéticos", "Fichas claras de enfermedades y síndromes genéticos, se hereden o no: causa, síntomas, herencia, diagnóstico, tratamiento y dónde informarse."),
        ("diagnostico", "Diagnóstico", "Del síntoma al resultado", "Pruebas cromosómicas y moleculares, cribado neonatal y prenatal, portadores, cómo leer un resultado y consejo genético."),
        ("tratamientos", "Tratamientos", "De la evidencia a la atención", "Tratamientos dirigidos y de soporte, terapia génica, CRISPR y farmacogenética: lo que ya funciona, lo que se investiga y los dilemas éticos."),
        ("personajes", "Personajes", "Las personas detrás de la genética", "Médicos, genetistas, bioquímicos y biólogos que hicieron avanzar la genética, de Mendel a CRISPR: qué descubrieron, cómo y por qué importa hoy."),
        ("lo-basico", "Lo básico", "ADN, genes y genoma", "Qué es el ADN, cómo se guarda la información genética y cómo se convierte en proteínas. El vocabulario para entender un informe."),
        ("herencia", "Herencia", "Cómo se heredan los rasgos", "De Mendel a la epigenética: patrones de herencia, penetrancia y por qué el riesgo no es destino."),
        ("genetica-y-cancer", "Genética y cáncer", "Genética y cáncer", "Cómo nace un tumor, qué cánceres se heredan, los síndromes de Lynch y Li-Fraumeni, la biopsia líquida y la oncología de precisión."),
        ("embarazo-y-reproduccion", "Embarazo y reproducción", "Embarazo y reproducción", "Planificar un embarazo cuando hay una enfermedad en la familia, el diagnóstico prenatal paso a paso, la FIV con diagnóstico preimplantacional y la donación de gametos."),
        ("preguntas-frecuentes", "Preguntas frecuentes", "Preguntas frecuentes", "Respuestas cortas y claras a las dudas más habituales sobre genética, herencia y pruebas genéticas."),
        ("enfermedades-raras", "Enfermedades raras", "Enfermedades raras en España", "Qué es una enfermedad rara, dónde se atienden en España, qué ayudas existen y a qué asociaciones acudir."),
        ("genetica-y-sociedad", "Genética y sociedad", "Genética y sociedad", "Leyes, privacidad de los datos genéticos, discriminación, patentes de genes y bases de datos policiales de ADN."),
        ("evolucion-humana", "Evolución humana", "Evolución y genética humana", "Lo que el ADN cuenta de nuestro origen: África, neandertales y denisovanos, Atapuerca y por qué no existen las razas biológicas."),
        ("genetica-forense", "Genética forense", "Genética forense", "Huellas genéticas, casos célebres, identificación de víctimas y genealogía genética para resolver casos antiguos."),
        ("plantas-y-animales", "Plantas y animales", "Genética de plantas y animales", "Transgénicos y edición genética de cultivos, el arroz dorado, la clonación animal y los mosquitos modificados contra la malaria."),
        ("rasgos-cotidianos", "Rasgos cotidianos", "La genética de cada día", "El color de los ojos, el grupo sanguíneo, la lactosa, el cilantro o la altura: qué hay de genético en los rasgos de todos los días."),
        ("para-profesores", "Para profesores", "Recursos para profesores", "Rutas de lectura por niveles, actividades prácticas para el aula y temas de debate con enlaces a los artículos de Geneticapedia."),
    ],
    "en": [
        ("diseases", "Conditions", "Genetic conditions and syndromes", "Clear fact sheets on genetic conditions and syndromes, inherited or not: cause, symptoms, inheritance, diagnosis, treatment and where to learn more."),
        ("diagnosis", "Diagnosis", "From symptoms to results", "Chromosome and molecular tests, newborn and prenatal screening, carrier testing, reading a result and genetic counselling."),
        ("treatments", "Treatments", "From evidence to care", "Targeted and supportive treatments, gene therapy, CRISPR and pharmacogenetics: what works, what is being studied and the ethical questions."),
        ("people", "People", "The people behind genetics", "Physicians, geneticists, biochemists and biologists who moved genetics forward, from Mendel to CRISPR."),
        ("basics", "Basics", "DNA, genes and genome", "What DNA is, how genetic information is stored and how it becomes proteins. The vocabulary you need to read a report."),
        ("heredity", "Heredity", "How traits are inherited", "From Mendel to epigenetics: inheritance patterns, penetrance and why risk is not destiny."),
        ("genetics-and-cancer", "Genetics and cancer", "Genetics and cancer", "How a tumour begins, which cancers are inherited, Lynch and Li-Fraumeni syndromes, liquid biopsy and precision oncology."),
        ("pregnancy-and-reproduction", "Pregnancy and reproduction", "Pregnancy and reproduction", "Planning a pregnancy when a condition runs in the family, prenatal diagnosis step by step, IVF with preimplantation testing and egg and sperm donation."),
        ("faq", "FAQ", "Frequently asked questions", "Short, clear answers to the most common questions about genetics, inheritance and genetic tests."),
        ("rare-diseases", "Rare diseases", "Rare diseases", "What a rare disease is, how care is organised in Spain and Europe, what support exists and where to find patient groups."),
        ("genetics-and-society", "Genetics and society", "Genetics and society", "Laws, genetic data privacy, discrimination, gene patents and police DNA databases."),
        ("human-evolution", "Human evolution", "Evolution and human genetics", "What DNA tells us about our origins: Africa, Neanderthals and Denisovans, Atapuerca and why biological races do not exist."),
        ("forensic-genetics", "Forensic genetics", "Forensic genetics", "DNA fingerprinting, famous cases, identifying victims and genetic genealogy to solve cold cases."),
        ("plants-and-animals", "Plants and animals", "Genetics of plants and animals", "GM and gene-edited crops, golden rice, animal cloning and modified mosquitoes against malaria."),
        ("everyday-traits", "Everyday traits", "Everyday genetics", "Eye colour, blood group, lactose, coriander or height: what is genetic about the traits we all share."),
        ("for-teachers", "For teachers", "Resources for teachers", "Reading routes by level, hands-on classroom activities and debate topics linked to Geneticapedia articles."),
    ],
}
EXTRA = {
    "es": [("historia", "Historia"), ("glosario", "Glosario"), ("quiz", "Quiz"), ("fuentes", "Fuentes"), ("blog", "Blog")],
    "en": [("history", "History"), ("glossary", "Glossary"), ("quiz", "Quiz"), ("sources", "Sources"), ("blog", "Blog")],
}
PROJECT = {
    "es": [("quien-esta-detras", "Quién está detrás"), ("enfoque-editorial", "Enfoque editorial"), ("aviso-legal", "Aviso legal"), ("privacidad", "Privacidad"), ("cookies", "Cookies")],
    "en": [("about", "About"), ("editorial-approach", "Editorial approach"), ("legal-notice", "Legal notice"), ("privacy", "Privacy"), ("cookies", "Cookies")],
}
# página equivalente en el otro idioma (ruta es -> ruta en)
PAIR = {"": "", "quien-esta-detras/": "about/", "enfoque-editorial/": "editorial-approach/", "aviso-legal/": "legal-notice/",
        "privacidad/": "privacy/", "cookies/": "cookies/", "historia/": "history/", "glosario/": "glossary/", "quiz/": "quiz/", "fuentes/": "sources/", "blog/": "blog/", "temas/": "topics/"}
for (a, *_), (b, *_) in zip(SECTIONS["es"], SECTIONS["en"]):
    PAIR[a + "/"] = b + "/"

T = {
    "es": dict(skip="Saltar al contenido", menu="Menú", other="English", otherlang="en", tagline="El ADN, explicado con claridad.",
               desc="Enciclopedia de genética en castellano: ADN, herencia, pruebas genéticas, enfermedades hereditarias, CRISPR, historia y glosario. Con fuentes y escrita por un médico.",
               foot="Enciclopedia divulgativa de genética: ciencia, salud y sociedad. No ofrece diagnóstico ni consejo genético individual.",
               help="¿Te preocupa una enfermedad en tu familia? Habla con tu médico de familia: puede derivarte a una <b>unidad de genética clínica</b> o de consejo genético.",
               sec="Secciones", proj="Proyecto", net="Red de webs", read="Leer →", upd="Actualizado", refs="Fuentes",
               err="¿Has visto un error? Escríbenos a", by="Texto: Alejandro Rosàs, médico de familia", rev="Revisión", toc="En este artículo",
               author="Creada por Alejandro Rosàs, médico de familia con más de 38 años de experiencia en atención primaria, especialista en Medicina Preventiva y Salud Pública (col. 28574, Barcelona).",
               lic='© 2026 Alejandro Rosàs · Contenido bajo licencia <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.es" rel="license noopener" style="display:inline">CC BY-NC 4.0</a>, salvo indicación en contrario',
               more="En esta sección", related="Lecturas relacionadas", seeall="Ver todo", home="Inicio", disclaimer="Información divulgativa. No sustituye la valoración de un profesional sanitario ni el consejo genético.",
               posts="Entradas recientes", allposts="Todas las entradas", locale="es_ES"),
    "en": dict(skip="Skip to content", menu="Menu", other="Español", otherlang="es", tagline="DNA, clearly explained.",
               desc="A genetics encyclopedia for everyone: DNA, heredity, genetic testing, inherited diseases, CRISPR, history and glossary. Sourced, written by a doctor.",
               foot="An encyclopedia of genetics for the general public: science, health and society. It does not provide diagnosis or individual genetic counselling.",
               help="Worried about a condition that runs in your family? Talk to your family doctor, who can refer you to a <b>clinical genetics</b> or genetic counselling service.",
               sec="Sections", proj="Project", net="Sister sites", read="Read →", upd="Updated", refs="Sources",
               err="Spotted a mistake? Write to", by="Text: Alejandro Rosàs, family physician", rev="Reviewed by", toc="In this article",
               author="Created by Alejandro Rosàs, a family physician with over 38 years in primary care and a specialist in Preventive Medicine and Public Health (licence 28574, Barcelona).",
               lic='© 2026 Alejandro Rosàs · Content licensed under <a href="https://creativecommons.org/licenses/by-nc/4.0/" rel="license noopener" style="display:inline">CC BY-NC 4.0</a> unless otherwise stated',
               more="In this section", related="Related reading", seeall="See all", home="Home", disclaimer="General information only. It does not replace advice from a health professional or genetic counselling.",
               posts="Latest posts", allposts="All posts", locale="en_GB"),
}
NETWORK = [("Medicapedia", "https://medicapedia.org"), ("Farmacos.ai", "https://farmacos.ai"), ("Psycholopedia", "https://psycholopedia.com"),
           ("Newtonpedia", "https://newtonpedia.com"), ("Escolapedia", "https://escolapedia.com"), ("Enciclopedias.si", "https://enciclopedias.si")]

esc = html.escape


def prefix(path):
    """'' -> './', 'a/' -> '../', 'a/b/' -> '../../' (path relative to site root, lang dir included)."""
    d = path.count("/")
    return "./" if d == 0 else "../" * d


AVAIL = {"es": None, "en": None}


def avail(lang):
    if AVAIL[lang] is None:
        a = set()
        for s in SECTIONS[lang]:
            d = os.path.join(SRC, lang, s[0])
            if os.path.isdir(d) and any(f.endswith(".md") for f in os.listdir(d)):
                a.add(s[0])
        if os.path.exists(os.path.join(SRC, lang, "datos.py")):
            a.update(u for u, _ in EXTRA[lang] if u != "blog")
        bd = os.path.join(SRC, lang, "blog")
        if os.path.isdir(bd) and any(f.endswith(".md") for f in os.listdir(bd)):
            a.add("blog")
        AVAIL[lang] = a
    return AVAIL[lang]


NAV_MAIN = [0, 1, 2]
NAV_LABEL = {"es": {"diagnostico": "Pruebas genéticas"}, "en": {"diagnosis": "Genetic tests"}}
NAV_GROUPS = {
    "es": [("Ciencia básica", [4, 5, 14, 11, 13]), ("Salud y familia", [9, 6, 7, 8]),
           ("Historia y sociedad", ["historia", 3, 10, 12]), ("Recursos", ["glosario", "quiz", "blog", 15, "fuentes"])],
    "en": [("Core science", [4, 5, 14, 11, 13]), ("Health and family", [9, 6, 7, 8]),
           ("History and society", ["history", 3, 10, 12]), ("Resources", ["glossary", "quiz", "blog", 15, "sources"])],
}
NAV_TX = {"es": ("Explorar", "Historia", "Todos los temas", "temas", "Buscar"),
          "en": ("Explore", "History", "All topics", "topics", "Search")}


def nav(lang, r):
    base = r + ("en/" if lang == "en" else "")
    av = avail(lang)
    secs = SECTIONS[lang]
    ext = dict(EXTRA[lang])
    explore, hist, alltxt, allurl, srch = NAV_TX[lang]
    hist_u = EXTRA[lang][0][0]

    def item(k):
        if isinstance(k, int):
            s = secs[k]
            lbl = NAV_LABEL[lang].get(s[0], s[1]) if k in NAV_MAIN else s[1]
            return (s[0], lbl) if s[0] in av else None
        return (k, ext[k]) if k in av or k in ("fuentes", "sources") else None

    top = [item(i) for i in NAV_MAIN] + [(hist_u, hist) if hist_u in av else None]
    links = "".join(f'<a class="mtop" href="{base}{u}/">{esc(t)}</a>' for u, t in filter(None, top))
    cols = ""
    for title, keys in NAV_GROUPS[lang]:
        its = [x for x in map(item, keys) if x]
        lis = "".join(f'<li><a href="{base}{u}/">{esc(t)}</a></li>' for u, t in its)
        cols += f'<div class="mcol"><p class="mh">{esc(title)}</p><ul>{lis}</ul></div>'
    panel = (f'<div class="mega" id="mega"><div class="mgrid">{cols}</div>'
             f'<p class="mall"><a href="{base}{allurl}/">{alltxt} →</a></p></div>')
    btn = f'<button class="mbtn" type="button" aria-expanded="false" aria-controls="mega">{explore}</button>'
    return links + btn + panel


def page(lang, path, title, desc, body, *, ldtype="WebPage", extra_ld=None, full_title=False, alt=None, og_type="website"):
    """path: relative to site root, ending with '/' or '' for home or '404.html'."""
    t = T[lang]
    r = prefix(path)
    base = r + ("en/" if lang == "en" else "")
    url = SITE + path
    if len(desc) > 160:
        cutd = desc[:157].rsplit(" ", 1)[0].rstrip(",;:·—-")
        desc = cutd + "…"
    if alt is None:
        rel = path[3:] if lang == "en" else path
        if lang == "es":
            alt = ("en/" + PAIR[rel]) if rel in PAIR else None
            seg = PAIR.get(rel, "").strip("/").split("/")[0]
            proj = [u for u, _ in PROJECT["en"]]
            if alt and seg and seg not in avail("en") and seg not in proj and seg != "topics":
                alt = None
        else:
            inv = {v: k for k, v in PAIR.items()}
            alt = inv.get(rel)
    es_url = en_url = None
    if lang == "es":
        es_url, en_url = path, alt
    else:
        es_url, en_url = alt, path
    hreflang = ""
    if es_url is not None and en_url is not None:
        hreflang = (f'<link rel="alternate" hreflang="es" href="{SITE}{es_url}"><link rel="alternate" hreflang="en" href="{SITE}{en_url}">'
                    f'<link rel="alternate" hreflang="x-default" href="{SITE}{es_url}">')
    other_href = r + (en_url if lang == "es" else es_url) if (es_url is not None and en_url is not None) else r + ("en/" if lang == "es" else "")
    ft = title if full_title or len(title) > 48 else f"{title} · Geneticapedia"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "#org", "name": "Geneticapedia", "url": SITE, "logo": SITE + "assets/favicon.svg"},
        {"@type": "WebSite", "@id": SITE + "#web", "name": "Geneticapedia", "url": SITE, "inLanguage": ["es", "en"], "publisher": {"@id": SITE + "#org"}},
        dict({"@type": ldtype, "@id": url + "#page", "url": url, "name": title, "description": desc, "inLanguage": lang,
              "isPartOf": {"@id": SITE + "#web"}, "dateModified": TODAY}, **(extra_ld or {}))]}
    sections_links = "".join(f'<a href="{base}{s[0]}/">{esc(s[1])}</a>' for s in SECTIONS[lang] if s[0] in avail(lang)) + "".join(f'<a href="{base}{u}/">{esc(n)}</a>' for u, n in EXTRA[lang] if u in avail(lang))
    proj_links = "".join(f'<a href="{base}{u}/">{esc(n)}</a>' for u, n in PROJECT[lang])
    net_links = "".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in NETWORK)
    rss = f'<link rel="alternate" type="application/rss+xml" title="Geneticapedia" href="{base}blog/feed.xml">' if "blog" in avail(lang) else ""
    noindex = '<meta name="robots" content="noindex">' if path.endswith("404.html") else ""
    canon = "" if noindex else f'<link rel="canonical" href="{url}">'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(ft)}</title>
<meta name="description" content="{esc(desc)}">{noindex}
{canon}
{hreflang}
<meta property="og:title" content="{esc(ft)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Geneticapedia"><meta property="og:url" content="{url}"><meta property="og:locale" content="{t['locale']}"><meta name="twitter:card" content="summary_large_image"><meta property="og:image" content="{SITE}assets/og-geneticapedia.png">
<meta name="theme-color" content="#24448a">
{rss}
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+4:opsz,wght@8..60,600&display=swap">
<link rel="stylesheet" href="{r}assets/site.css?v={V}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{base}" aria-label="Geneticapedia"><span class="sym" aria-hidden="true"><img src="{r}assets/favicon.svg" alt="" width="26" height="26" style="display:block"></span>Geneticapedia</a>
  <button class="burger" type="button" aria-expanded="false" aria-controls="menu">{t['menu']}</button>
  <nav class="menu" id="menu" aria-label="{t['sec']}">{nav(lang, r)}</nav>
  <a class="lang" href="{other_href}" hreflang="{t['otherlang']}" lang="{t['otherlang']}" aria-label="{t['other']}" title="{t['other']}">{t['otherlang'].upper()}</a>
</div></header>

<main id="main">
{body}
</main>
<footer class="foot"><div class="wrap">
  <div class="cols">
    <div><a class="brand" href="{base}"><span class="sym" aria-hidden="true"><img src="{r}assets/favicon.svg" alt="" width="26" height="26" style="display:block"></span>Geneticapedia</a><p style="margin-top:10px">{t['foot']}</p><div class="help">{t['help']}</div></div>
    <div><h2 class="fh">{t['sec']}</h2>{sections_links}</div>
    <div><h2 class="fh">{t['proj']}</h2>{proj_links}</div>
    <div><h2 class="fh">{t['net']}</h2>{net_links}</div>
  </div>
  <p style="margin:22px 0 0">{t['author']} <a style="display:inline" href="{base}{PROJECT[lang][0][0]}/">{PROJECT[lang][0][1]}</a></p><p style="margin:6px 0 0">{t['tagline']}</p><p style="margin:6px 0 0">{t['lic']}</p>
</div></footer>
<script src="{r}assets/app.js?v={V}" defer></script>
</body>
</html>
"""


def write(path, content):
    fp = os.path.join(OUT, path if path.endswith(".html") or "." in os.path.basename(path) else os.path.join(path, "index.html"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)


def read_md(fp):
    raw = open(fp, encoding="utf-8").read()
    meta = {}
    if raw.startswith("---"):
        head, raw = raw[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw.strip()


IMG = json.load(open(os.path.join(SRC, "imagenes.json"), encoding="utf-8")) if os.path.exists(os.path.join(SRC, "imagenes.json")) else {}


def credit(fn, lang="es"):
    c = IMG.get(fn)
    if not c:
        return ""
    lic = f'<a href="{esc(c["license_url"])}" rel="license noopener">{esc(c["license"])}</a>' if c.get("license_url") else esc(c["license"])
    art = c["artist"]
    if len(art) % 2 == 0 and art[:len(art) // 2] == art[len(art) // 2:]:
        art = art[:len(art) // 2]
    art = re.sub(r"^Unknown author\s*Unknown author$", "Unknown author", art)
    if lang == "es":
        art = art.replace("Unknown author", "Autor desconocido")
    if lang == "en":
        art = art.replace("Autor desconocido", "Unknown author").replace("obra derivada", "derivative work").replace("artículo de", "article by").replace("Subido por", "Uploaded by")
        lic = lic.replace("Public domain", "Public domain")
    else:
        lic = lic.replace(">Public domain<", ">Dominio público<").replace("Public domain", "Dominio público").replace(">No restrictions<", ">Sin restricciones<").replace(">Copyrighted free use<", ">Uso libre con copyright<")
    return f'<span class="credit">{"Imagen" if lang == "es" else "Image"}: {esc(art)} · {lic} · <a href="{esc(c["page"])}" rel="noopener">{esc(c.get("source", "Wikimedia Commons"))}</a></span>'


def has_img(fn):
    return bool(fn) and (os.path.exists(os.path.join(ROOT, "assets", "img", fn)) or bool(IMG.get(fn, {}).get("url")))


def isrc(fn, r="@@R@@"):
    u = IMG.get(fn, {}).get("url")
    return esc(u) if u else f"{r}assets/img/{fn}"


_DIM = {}


def wh_attr(fn):
    c = IMG.get(fn, {})
    if c.get("w") and c.get("h"):
        return f' width="{c["w"]}" height="{c["h"]}"'
    p = os.path.join(ROOT, "assets", "img", fn)
    if fn not in _DIM:
        _DIM[fn] = None
        if os.path.exists(p) and not fn.endswith(".svg"):
            try:
                from PIL import Image
                with Image.open(p) as im:
                    _DIM[fn] = im.size
            except Exception:
                pass
    d = _DIM[fn]
    return f' width="{d[0]}" height="{d[1]}"' if d else ""


def figure(fn, alt, cap, lang, cls="fig"):
    if not has_img(fn):
        return ""
    wh = wh_attr(fn)
    return f'<figure class="{cls}"><img src="{isrc(fn)}" alt="{esc(alt)}"{wh} loading="lazy" decoding="async"><figcaption>{esc(cap)} {credit(fn, lang)}</figcaption></figure>'


def figs(text, lang):
    def rep(m):
        parts = [x.strip() for x in m.group(1).split("|")]
        fn, alt = parts[0], parts[1]
        cap = parts[2] if len(parts) > 2 else ""
        return "\n" + figure(fn, alt, cap, lang) + "\n"
    return re.sub(r"^!fig (.+)$", rep, text, flags=re.M)


def md(text, lang):
    text = figs(text, lang)
    h = markdown.markdown(text, extensions=["tables", "attr_list", "sane_lists"])
    # lista de fuentes con estilo .refs
    ref = T[lang]["refs"]
    h = re.sub(rf"(<h2[^>]*>{ref}</h2>\s*)<ol>", r'\1<ol class="refs">', h)
    # llamadas a las fuentes: [[2]] o [[1,3]] -> número enlazado a la lista de fuentes
    def _cite(m):
        ns = [x.strip() for x in m.group(1).split(",")]
        return '<sup class="cite">' + ",".join(f'<a href="#ref-{x}" aria-label="{ref} {x}">{x}</a>' for x in ns) + "</sup>"
    h = re.sub(r"\s?\[\[(\d+(?:\s*,\s*\d+)*)\]\]", _cite, h)
    if '<ol class="refs">' in h:
        a_ = h.index('<ol class="refs">'); b_ = h.index("</ol>", a_)
        k_ = iter(range(1, 999))
        h = h[:a_] + re.sub(r"<li>", lambda m: f'<li id="ref-{next(k_)}">', h[a_:b_]) + h[b_:]
    h = re.sub(r"<table>", '<div class="table-scroll"><table>', h).replace("</table>", "</table></div>")
    # enlaces externos
    h = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" rel="noopener">', h)
    # anclas en los apartados, para el índice
    used = set()
    def _hid(m):
        import unicodedata
        base = unicodedata.normalize("NFD", strip_tags(m.group(1)).lower())
        base = re.sub(r"[^a-z0-9]+", "-", "".join(c for c in base if unicodedata.category(c) != "Mn")).strip("-")[:60] or "apartado"
        k, n = base, 2
        while k in used:
            k, n = f"{base}-{n}", n + 1
        used.add(k)
        return f'<h2 id="{k}">{m.group(1)}</h2>'
    h = re.sub(r"<h2>(.*?)</h2>", _hid, h)
    return h


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def fecha(d, lang):
    y, m, dd = d[:4], int(d[5:7]), int(d[8:10])
    return f"{dd} de {MESES[m - 1]} de {y}" if lang == "es" else f"{dd} {MONTHS[m - 1]} {y}"


def strip_tags(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def load_section(lang, slug):
    d = os.path.join(SRC, lang, slug)
    items = []
    if not os.path.isdir(d):
        return items
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md"):
            meta, body = read_md(os.path.join(d, fn))
            meta["slug"] = fn[3:-3] if re.match(r"\d\d-", fn) else fn[:-3]
            meta["num"] = fn[:2] if re.match(r"\d\d-", fn) else fn[:-3]
            meta["body"] = body
            items.append(meta)
    return items


_GLOS = {}
_GLOS_SKIP = {"adn", "arn", "gen", "genoma", "proteína", "síndrome", "mutación", "enzima", "cromosoma", "dna", "rna", "gene", "genome", "protein", "syndrome", "mutation", "enzyme", "chromosome", "clon", "clone", "vector", "locus"}


def glos_terms(lang):
    if lang not in _GLOS:
        import runpy, html as _h
        from build_extra import slugify as _sl
        fp = os.path.join(SRC, lang, "datos.py")
        terms = []
        if os.path.exists(fp):
            for term, d in runpy.run_path(fp)["GLOSARIO"]:
                if term.lower() in _GLOS_SKIP or len(term) < 3:
                    continue
                plain = _h.unescape(re.sub(r"<[^>]+>", "", d)).replace(" Leer más.", "").replace(" Read more.", "").strip()
                if len(plain) > 160:
                    plain = plain[:157].rsplit(" ", 1)[0] + "…"
                terms.append((term, _sl(term), plain))
        terms.sort(key=lambda x: -len(x[0]))
        _GLOS[lang] = terms
    return _GLOS[lang]


def glos_link(h, lang, maxn=14):
    """Enlaza la primera aparición de cada término del glosario en párrafos y listas."""
    gl = "../../glosario/" if lang == "es" else "../../glossary/"
    terms = glos_terms(lang)
    if not terms:
        return h
    parts = re.split(r"(<[^>]+>)", h)
    block = {"a": 0, "h": 0, "skip": 0}
    inside = 0
    used = set()
    n = 0
    for i, part in enumerate(parts):
        if part.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", part)
            tag = m.group(1).lower() if m else ""
            close = part.startswith("</")
            dlt = -1 if close else 1
            if tag == "a": block["a"] += dlt
            elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"): block["h"] += dlt
            elif tag in ("table", "figcaption", "code", "pre", "aside", "blockquote", "summary"): block["skip"] += dlt
            elif tag in ("p", "li") and not part.endswith("/>"): inside += dlt
            continue
        if n >= maxn or inside <= 0 or any(v > 0 for v in block.values()) or not part.strip():
            continue
        for term, slug, plain in terms:
            if slug in used or n >= maxn:
                continue
            rx = re.compile(r"(?<![\w-])(" + re.escape(term) + r")(?![\w-])", re.I)
            mm = rx.search(part)
            if not mm:
                continue
            a = f'<a class="gl" href="{gl}#{slug}" title="{esc(plain)}">{mm.group(1)}</a>'
            parts[i] = part = part[:mm.start()] + "\x00" + str(len(used)) + "\x00" + part[mm.end():]
            used.add(slug)
            parts[i] = part
            parts[i] = parts[i]
            globals().setdefault("_GLREP", {})[(i, len(used) - 1)] = a
            n += 1
        # sustituir marcadores
        def rep(m2, i=i):
            return globals()["_GLREP"][(i, int(m2.group(1)))]
        parts[i] = re.sub(r"\x00(\d+)\x00", rep, parts[i])
    return "".join(parts)


TITLES = {}


def article_page(lang, sec, item, siblings, search):
    t = T[lang]
    lp = "en/" if lang == "en" else ""
    path = f"{lp}{sec[0]}/{item['slug']}/"
    r = prefix(path)
    base = r + lp
    body_html = glos_link(md(item["body"], lang), lang)
    disc = f'<p class="disclaim">{t["disclaimer"]}</p>' if item.get("health") == "si" else ""
    hero = ficha = ""
    if item.get("vida"):
        rows = ([("Vida", "vida"), ("País", "pais"), ("Campo", "campo"), ("Aportación clave", "aporte"), ("Reconocimientos", "premio")] if lang == "es" else
                [("Life", "vida"), ("Country", "pais"), ("Field", "campo"), ("Key contribution", "aporte"), ("Honours", "premio")])
        img = f'<img src="{isrc(item["img"])}" alt="{esc(item["title"])}"{wh_attr(item["img"])} loading="lazy" decoding="async">' if has_img(item.get("img")) else ""
        cred = f'<p class="fcred">{credit(item["img"], lang)}</p>' if has_img(item.get("img")) else ""
        ficha = f'<div class="box ficha">{img}<h2 class="bh">{esc(item["title"])}</h2><dl>' + "".join(f'<dt>{a}</dt><dd>{esc(item[k])}</dd>' for a, k in rows if item.get(k)) + f'</dl>{cred}</div>'
    elif item.get("img"):
        hero = figure(item["img"], item.get("img_alt", item["title"]), item.get("img_pie", ""), lang, "fig hero")
    rel, seen = [], {f"{sec[0]}/{item['slug']}"}
    for a_, b_ in re.findall(r"\]\((?:\.\./\.\./([a-z0-9-]+)/|\.\./)([a-z0-9-]+)/\)", item["body"]):
        k_ = f"{a_ or sec[0]}/{b_}"
        if k_ not in seen and (lang, k_) in TITLES:
            seen.add(k_); rel.append(k_)
    if sec[0] in ("enfermedades", "diseases"):
        k_ = "herencia/patrones-de-herencia" if lang == "es" else "heredity/inheritance-patterns"
        if k_ not in seen and (lang, k_) in TITLES:
            seen.add(k_); rel.insert(0, k_)
    rel = [k for k in rel if not k.startswith(("personajes/", "people/"))] + [k for k in rel if k.startswith(("personajes/", "people/"))]
    if len(rel) < 4:
        ix = next((n for n, s in enumerate(siblings) if s["slug"] == item["slug"]), 0)
        for s in siblings[ix + 1:] + siblings[:ix]:
            k_ = f"{sec[0]}/{s['slug']}"
            if k_ not in seen and len(rel) < 4:
                seen.add(k_); rel.append(k_)
    sib = "".join(f'<li><a href="{base}{k}/"><small>{esc(TITLES[(lang, k)][1])}</small>{esc(TITLES[(lang, k)][0])}</a></li>' for k in rel[:5])
    allrel = f'<p class="allrel"><a href="{base}{sec[0]}/">{(("Ver todas las enfermedades" if lang == "es" else "See all conditions") if sec[0] in ("enfermedades", "diseases") else t["seeall"] + ": " + esc(sec[1]))} →</a></p>'

    crumbs = f'<nav class="crumbs" aria-label="breadcrumb"><a href="{base}">{t["home"]}</a> › <a href="{base}{sec[0]}/">{esc(sec[1])}</a></nav>'
    upd = item.get("updated", TODAY)
    rev = f' · <span class="rev">{t["rev"]}: {esc(item["revisor"])}{", " + esc(item["revisor_rol"]) if item.get("revisor_rol") else ""}</span>' if item.get("revisor") else ""
    byline = f'<p class="byline"><a href="{base}{PROJECT[lang][0][0]}/">{t["by"]}</a> · {t["upd"]}: <time datetime="{upd}">{fecha(upd, lang)}</time>{rev}</p>'
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
    toc = (f'<nav class="toc" aria-label="{t["toc"]}"><p class="toch">{t["toc"]}</p><ol>' + "".join(f'<li><a href="#{i}">{strip_tags(h)}</a></li>' for i, h in heads) + "</ol></nav>") if len(heads) >= 3 else ""
    lead_html = toc + hero + body_html
    if heads and strip_tags(heads[0][1]) in ("En pocas palabras", "At a glance", "Respuesta corta", "Short answer"):
        cut2 = body_html.find("<h2 ", body_html.find("<h2 ") + 4)
        if cut2 > 0:
            lead_html = f'<div class="sumbox">{body_html[:cut2]}</div>{toc}{hero}{body_html[cut2:]}'
    body = f"""<header class="phead wrap">{crumbs}<span class="eyebrow">{esc(sec[1])}</span><h1>{esc(item['title'])}</h1><p class="lead">{esc(item['desc'])}</p>{byline}</header>
<div class="wrap article{' has-ficha' if ficha else ''}"><article class="prose">{disc}{lead_html}<p class="meta">{t['by']} · {t['upd']}: {item.get('updated', TODAY)} · {t['err']} <a href="mailto:{MAIL}">{MAIL}</a></p></article>
<aside class="aside">{ficha}<div class="box"><h2 class="bh">{t['related']}</h2><ul class="rel">{sib}</ul>{allrel}</div></aside></div>"""
    body = body.replace("@@R@@", r)
    ldtype = "MedicalWebPage" if item.get("health") == "si" else "Article"
    extra = {"headline": item["title"], "author": {"@type": "Person", "name": "Alejandro Rosàs", "jobTitle": "Médico de familia" if lang == "es" else "Family physician"}, "datePublished": item.get("updated", TODAY)}
    if ldtype == "MedicalWebPage":
        extra["lastReviewed"] = item.get("updated", TODAY)
    ptitle = item["title"] + (", biografía" if lang == "es" else ": biography") if item.get("vida") else item["title"]
    write(path, page(lang, path, ptitle, item["desc"], body, ldtype=ldtype, extra_ld=extra, og_type="article", alt=item.get("alt")))
    search.append({"t": item["title"], "d": item["desc"], "u": path[len(lp):], "k": sec[1], "n": strip_tags(body_html.replace("@@R@@", ""))[:600]})


TERMS = {
    "es": """<section class="wrap"><div class="terms"><div><h2 class="bh">Genético</h2><p>Causado por un cambio en los genes o en los cromosomas. No siempre se hereda: el síndrome de Down, por ejemplo, casi siempre aparece de nuevo en ese embarazo.</p></div><div><h2 class="bh">Hereditario</h2><p>Se transmite de padres a hijos a través de una variante presente en el óvulo o el espermatozoide, como la fibrosis quística o la enfermedad de Huntington.</p></div><div><h2 class="bh">Congénito</h2><p>Presente desde el nacimiento, sea o no de origen genético. Una infección durante el embarazo también puede causar un problema congénito.</p></div></div></section>""",
    "en": """<section class="wrap"><div class="terms"><div><h2 class="bh">Genetic</h2><p>Caused by a change in the genes or chromosomes. It is not always inherited: Down syndrome, for example, almost always arises anew in that pregnancy.</p></div><div><h2 class="bh">Inherited</h2><p>Passed from parents to children through a variant carried in the egg or sperm, such as cystic fibrosis or Huntington's disease.</p></div><div><h2 class="bh">Congenital</h2><p>Present from birth, whether or not it is genetic. An infection during pregnancy can also cause a congenital problem.</p></div></div></section>""",
}


def section_index(lang, sec, items, search):
    t = T[lang]
    lp = "en/" if lang == "en" else ""
    path = f"{lp}{sec[0]}/"
    r = prefix(path)
    def thumb(it):
        if has_img(it.get("img")):
            return f'<img class="cimg" src="{isrc(it["img"], r)}" alt="" width="640" height="360" loading="lazy" decoding="async">'
        if it.get("vida"):
            ini = "".join(w[0] for w in it["title"].split()[:2])
            return f'<span class="cimg ph" aria-hidden="true">{esc(ini)}</span>'
        return ""
    def sub(it):
        return f'<span class="tag">{esc(it["vida"])}</span>' if it.get("vida") else ""
    cards = "".join(f'<a class="card{" person" if it.get("vida") else ""}" href="./{it["slug"]}/">{thumb(it)}<span class="num">{i:02d}</span>{sub(it)}<h2 class="ch">{esc(it["title"])}</h2><p>{esc(it["desc"])}</p><span class="more">{t["read"]}</span></a>' for i, it in enumerate(items, 1))
    terms = TERMS[lang] if sec[0] in ("enfermedades", "diseases") else ""
    body = f"""<header class="phead wrap"><span class="eyebrow">{esc(sec[1])}</span><h1>{esc(sec[2])}</h1><p class="lead">{esc(sec[3])}</p></header>
{terms}<section class="wrap section" style="padding-top:0"><div class="grid">{cards}</div></section>"""
    write(path, page(lang, path, sec[2], sec[3], body, ldtype="CollectionPage"))
    search.append({"t": sec[2], "d": sec[3], "u": path[len(lp):], "k": sec[1], "n": " ".join(i["title"] for i in items)})


def topics_page(lang, allsec, search):
    t = T[lang]
    lp = "en/" if lang == "en" else ""
    slug = "temas" if lang == "es" else "topics"
    path = f"{lp}{slug}/"
    title = "Todos los temas" if lang == "es" else "All topics"
    desc = ("Todas las secciones de Geneticapedia: salud, ciencia básica, historia, sociedad y la genética de cada día." if lang == "es"
            else "Every section of Geneticapedia: health, basic science, history, society and everyday genetics.")
    word = "artículos" if lang == "es" else "articles"
    cards = "".join(f'<a class="card" href="../{s[0]}/"><span class="num">{i:02d}</span><span class="tag">{esc(s[1])}</span><h3>{esc(s[2])}</h3><p>{esc(s[3])}</p><span class="more">{len(allsec.get(s[0], []))} {word} →</span></a>'
                    for i, s in enumerate([s for s in SECTIONS[lang] if allsec.get(s[0])], 1))
    body = f"""<header class="phead wrap"><span class="eyebrow">{"Mapa del sitio" if lang == "es" else "Site map"}</span><h1>{title}</h1><p class="lead">{desc}</p></header>
<section class="wrap section" style="padding-top:0"><div class="grid">{cards}</div></section>"""
    write(path, page(lang, path, title, desc, body, ldtype="CollectionPage"))
    search.append({"t": title, "d": desc, "u": path[len(lp):], "k": title, "n": ""})


def simple_page(lang, slug, search, eyebrow=None):
    lp = "en/" if lang == "en" else ""
    meta, body = read_md(os.path.join(SRC, lang, "pages", slug + ".md"))
    path = f"{lp}{slug}/"
    h = md(body, lang)
    out = f"""<header class="phead wrap"><span class="eyebrow">{esc(meta.get('eyebrow', ''))}</span><h1>{esc(meta['title'])}</h1><p class="lead">{esc(meta['desc'])}</p></header>
<div class="wrap narrow prose">{h}</div>"""
    write(path, page(lang, path, meta["title"], meta["desc"], out))
    search.append({"t": meta["title"], "d": meta["desc"], "u": path[len(lp):], "k": meta.get("eyebrow", ""), "n": strip_tags(h)[:400]})
    return meta


# ----- hélice SVG de la portada -----
def helix_svg():
    W, H, n = 520, 390, 15
    a = []
    for k in range(n):
        y = 20 + k * (H - 40) / (n - 1)
        ph = k * 0.55
        x1 = W / 2 + 120 * math.sin(ph)
        x2 = W / 2 - 120 * math.sin(ph)
        op = 0.35 + 0.65 * (math.cos(ph) + 1) / 2
        col = ["#2f58a8", "#a3305f", "#2f8a6b", "#c98a1c"][k % 4]
        a.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="7" stroke-linecap="round" opacity="{op:.2f}"/>')
    p1 = " ".join(f"{W/2 + 120*math.sin(i*0.55/4):.1f},{20 + i*(H-40)/((n-1)*4):.1f}" for i in range((n - 1) * 4 + 1))
    p2 = " ".join(f"{W/2 - 120*math.sin(i*0.55/4):.1f},{20 + i*(H-40)/((n-1)*4):.1f}" for i in range((n - 1) * 4 + 1))
    return (f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Doble hélice de ADN">'
            + "".join(a)
            + f'<polyline points="{p1}" fill="none" stroke="var(--accent)" stroke-width="9" stroke-linecap="round"/>'
            + f'<polyline points="{p2}" fill="none" stroke="var(--gold)" stroke-width="9" stroke-linecap="round"/></svg>')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    for f in os.listdir(os.path.join(ROOT, "static")):
        shutil.copy(os.path.join(ROOT, "static", f), OUT)
    urls = []
    import build_extra
    # emparejar artículos es <-> en por sección y número de archivo
    for (a, *_), (b, *_) in zip(SECTIONS["es"], SECTIONS["en"]):
        en_items = {i["num"]: i["slug"] for i in load_section("en", b)}
        for i in load_section("es", a):
            if i["num"] in en_items:
                PAIR[f"{a}/{i['slug']}/"] = f"{b}/{en_items[i['num']]}/"
    bes, ben = (sorted(f for f in os.listdir(os.path.join(SRC, x, "blog")) if f.endswith(".md")) if os.path.isdir(os.path.join(SRC, x, "blog")) else [] for x in ("es", "en"))
    for fe, fn_ in zip(bes, ben):
        en_slug = read_md(os.path.join(SRC, "es", "blog", fe))[0].get("en") or fn_[11:-3]
        PAIR[f"blog/{fe[11:-3]}/"] = f"blog/{en_slug}/"
    for lang in ("es", "en"):
        for sec in SECTIONS[lang]:
            for it in load_section(lang, sec[0]):
                TITLES[(lang, f"{sec[0]}/{it['slug']}")] = (it["title"], sec[1])
    for lang in ("es", "en"):
        search = []
        allsec = {}
        for sec in SECTIONS[lang]:
            items = load_section(lang, sec[0])
            allsec[sec[0]] = items
            if not items:
                continue
            section_index(lang, sec, items, search)
            for it in items:
                article_page(lang, sec, it, items, search)
        topics_page(lang, allsec, search)
        build_extra.build(lang, globals(), allsec, search)
        os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
        with open(os.path.join(OUT, "assets", f"search-{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(search, f, ensure_ascii=False)
    # sitemap
    for dp, dn, fn in os.walk(OUT):
        for f in fn:
            if f == "index.html":
                rel = os.path.relpath(os.path.join(dp, f), OUT).replace("\\", "/")[:-10]
                urls.append(rel)
    urls.sort(key=lambda u: (u.startswith("en/"), u.count("/"), u))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print(len(urls), "páginas")


if __name__ == "__main__":
    main()
