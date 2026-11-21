"""Páginas especiales: portada, historia, glosario, quiz, blog, proyecto y 404."""
import html, json, os, re, runpy, unicodedata
from email.utils import format_datetime
from datetime import datetime, timezone

esc = html.escape


def slugify(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# Imagen de cada hito de la historia (por índice de HISTORIA; se usa la primera que exista)
HIST_IMG = {
    0: ["maizal.jpg"], 1: ["p-darwin.jpg", "oveja.jpg"], 2: ["p-mendel.jpg"], 3: ["p-miescher.jpg"], 4: ["p-de-vries.jpg"],
    5: ["p-garrod.jpg"], 6: ["p-johannsen.jpg", "info-herencia-@@L@@.svg"], 7: ["p-morgan.jpg"], 8: ["arbol-genealogico.jpg"],
    9: ["p-griffith.jpg", "watson-crick-mccarty.jpg"], 10: ["p-beadle.jpg", "info-gen-proteina-@@L@@.svg"], 11: ["p-avery.jpg"],
    12: ["p-mcclintock.jpg"], 13: ["p-chargaff.jpg", "p-crick.jpg"], 14: ["p-pauling.jpg"], 15: ["p-franklin.jpg", "rosalind-franklin.jpg"],
    16: ["p-watson.jpg", "p-crick.jpg"], 17: ["karyotype-t21.jpg"], 18: ["karyotype-t21.jpg"], 19: ["p-ochoa.jpg"],
    20: ["p-nirenberg.jpg", "p-khorana.jpg"], 21: ["p-monod.jpg", "info-gen-proteina-@@L@@.svg"], 22: ["p-guthrie.jpg", "bolsa-sangre.jpg"],
    23: ["p-mckusick.jpg"], 24: ["p-berg.jpg"], 25: ["p-sanger.jpg"], 26: ["p-mullis.jpg", "info-pcr-@@L@@.svg"],
    27: ["p-wexler.jpg"], 28: ["p-jeffreys.jpg"], 29: ["p-salas.jpg"], 30: ["p-tsui.jpg", "p-king.jpg"], 31: ["p-collins.jpg"],
    32: ["oveja.jpg"], 33: ["p-venter.jpg", "secuenciador.jpg"], 34: ["p-mojica.jpg"], 35: ["secuenciador.jpg"],
    36: ["neandertal-craneo.jpg", "embrion-celulas.jpg"], 37: ["p-doudna.jpg", "p-charpentier.jpg"], 38: ["fiv-embrion.jpg"],
    39: ["informe-genetico.jpg"], 40: ["falciforme-frotis.jpg"], 41: ["medicamentos-arn.jpg"],
}


# Preguntas del quiz de nivel ESO (por índice de QUIZ); el resto, Bachillerato
QUIZ_ESO = {7, 8, 11, 12, 13, 14, 15, 16, 17, 21, 23, 25, 28, 29, 30, 31, 32, 35, 40, 41, 43, 44}

L = {
    "es": dict(hist="historia", glos="glosario", quiz="quiz", blog="blog", fuentes="fuentes", res_url="diagnostico/como-leer-un-resultado-genetico/", fam_url="diagnostico/consejo-genetico/", src_note="Una fuente fiable no sustituye a tu equipo médico. Si un resultado o una noticia te preocupa, coméntalo en tu centro de salud.",
               eyebrow="La enciclopedia de la genética", h1="El ADN, <em>explicado con claridad.</em>",
               lead="Enfermedades hereditarias, pruebas genéticas y tratamientos explicados con claridad. Qué son los genes, cómo se heredan y hacia dónde va la medicina del ADN, con fuentes en cada página.",
               note="1953: Watson y Crick propusieron el modelo de la doble hélice, apoyándose en los datos de Franklin, Gosling, Wilkins y Chargaff. El ADN ya se conocía desde 1869, y desde 1944 se sabía que era el material hereditario.",
               ph="Busca una enfermedad, un gen, una prueba…", btn="Buscar", start="Explorar enfermedades →", play="Comprender las pruebas",
               trust=["Enfermedades", "Diagnóstico", "Tratamientos", "Historia, glosario y quiz", "Bilingüe · Con fuentes · Gratuita"],
               core_e="El núcleo de Geneticapedia", core_h="Enfermedades. Diagnóstico. Tratamiento.", core_p="Del gen a la consulta: lo que importa para las personas y sus familias.",
               res_h="Un resultado necesita<br>una explicación.", res_p="Una predisposición no es un destino. Una prueba negativa tiene límites. Una variante de significado incierto no es, por sí sola, un diagnóstico.", res_btn="Cómo leer un resultado",
               fam_e="Consejo genético", fam_h="Información para personas y familias", fam_p="Una prueba genética puede tener consecuencias para tus familiares, para tus decisiones reproductivas y para tu seguimiento. El consentimiento y la explicación de las incertidumbres forman parte de una buena atención.", fam_btn="Qué es el consejo genético",
               sci_e="Novedades y avances", sci_h="La investigación, con contexto", sci_p="Enlaces a las fuentes originales, con lo que conviene mirar en cada una. Ninguna noticia promete que un tratamiento esté disponible.",
               sci=[("Publicaciones recientes", "Distingue estudios de laboratorio, ensayos, revisiones y resultados preliminares.", "https://pubmed.ncbi.nlm.nih.gov/?term=medical+genetics&sort=date", "PubMed"),
                    ("Ensayos clínicos", "Revisa a quién incluye, en qué fase está, con qué se compara y qué resultados tiene.", "https://clinicaltrials.gov/search?cond=Genetic%20Diseases", "ClinicalTrials.gov"),
                    ("Medicamentos autorizados", "Comprueba la indicación, quién puede recibirlo y si está autorizado en España.", "https://cima.aemps.es/cima/", "AEMPS · CIMA")],
               consult="Consultar", fuentes_btn="Todas las fuentes →",
               fuentes_title="Fuentes y biblioteca", fuentes_desc="Dónde ampliar, contrastar y comprobar: fuentes fiables de genética para pacientes, familias y profesionales, con lo que conviene saber de cada una.",
               libros_h="Biblioteca de referencia", libros_p="Manuales en los que nos apoyamos para escribir y revisar los contenidos.",
               doors_e="Tres formas de entrar", doors_h="Comprender, decidir, descubrir",
               doors=[("Comprender", "Las bases", [("lo-basico/que-es-el-adn/", "Qué es el ADN"), ("lo-basico/genes-cromosomas-y-genoma/", "Genes, cromosomas y genoma"), ("herencia/", "Cómo se heredan los rasgos"), ("glosario/", "Glosario")]),
                      ("Decidir", "Genética y salud", [("diagnostico/paneles-exoma-y-genoma/", "Paneles, exoma y genoma"), ("diagnostico/pruebas-de-portadores-y-preimplantacional/", "Pruebas de portadores"), ("diagnostico/tests-geneticos-directos-al-consumidor/", "Tests de ancestría por correo"), ("diagnostico/consejo-genetico/", "Qué es el consejo genético")]),
                      ("Descubrir", "Ciencia y futuro", [("historia/", "Historia de la genética"), ("tratamientos/crispr-explicado/", "CRISPR explicado"), ("fuentes/", "Fuentes y biblioteca"), ("quiz/", "Quiz")])],
               map_e="Un mapa de la genética", map_h="¿Qué te gustaría comprender?", map_p="Cinco secciones, de lo más básico a lo más nuevo.",
               hist_e="Historia", hist_h="De los guisantes de Mendel al genoma completo", hist_btn="Ver la historia completa →",
               blog_e="Blog", blog_h="Entradas recientes", blog_btn="Todas las entradas →",
               who_t="Quién está detrás", who_h="Creada por un médico de familia",
               who_p="Alejandro Rosàs, médico de familia con <b>más de 38 años de experiencia en atención primaria</b> y especialista en Medicina Preventiva y Salud Pública. Colegiado en Barcelona, n.º 28574.",
               who_btn="Conocer al autor", ed_t="Genética con contexto", ed_h="Sin determinismo ni alarmismo",
               ed_p="Los genes cuentan, pero casi nunca lo deciden todo. Explicamos la evidencia, sus límites y las dudas éticas.", ed_btn="Nuestro enfoque editorial",
               hist_title="Historia de la genética", hist_desc="Una línea de tiempo de la genética, de la mejora de plantas y animales en la Antigüedad a CRISPR y el pangenoma humano.",
               glos_title="Glosario de genética", quiz_title="¿Cuánto sabes de genética?", blog_title="Blog de Geneticapedia",
               blog_desc="Novedades, explicaciones de noticias y preguntas frecuentes sobre genética, explicadas sin tecnicismos.",
               photo_alt="Maclyn McCarty estrecha la mano de Francis Crick, con James Watson entre ambos", photo_t="McCarty, Watson y Crick", photo_c="De izquierda a derecha: Maclyn McCarty, James Watson y Francis Crick. Foto: Marjorie McCarty, PLOS Biology (2005), CC BY 2.5. <a href=\"blog/avery-macleod-y-mccarty/\">La historia de la foto</a>",
               q_daily="Quiz diario", q_all="Todas", p404="Página no encontrada", p404d="La página que buscas no existe o ha cambiado de dirección.", back="Volver a la portada",
               date_fmt=lambda d: f"{int(d[8:10])} de {['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'][int(d[5:7])-1]} de {d[:4]}"),
    "en": dict(hist="history", glos="glossary", quiz="quiz", blog="blog", fuentes="sources", res_url="diagnosis/how-to-read-a-genetic-result/", fam_url="diagnosis/genetic-counselling/", src_note="A reliable source does not replace your care team. If a result or a news story worries you, talk to your doctor.",
               eyebrow="The encyclopedia of genetics", h1="DNA, <em>clearly explained.</em>",
               lead="Inherited conditions, genetic tests and treatments, clearly explained. What genes are, how they are inherited and where DNA medicine is heading, with sources on every page.",
               note="1953: Watson and Crick proposed the double-helix model, relying on data from Franklin, Gosling, Wilkins and Chargaff. DNA had been known since 1869, and since 1944 it was known to be the hereditary material.",
               ph="Search a condition, a gene, a test…", btn="Search", start="Explore conditions →", play="Understand the tests",
               trust=["Conditions", "Diagnosis", "Treatments", "History, glossary and quiz", "Bilingual · Sourced · Free"],
               core_e="The core of Geneticapedia", core_h="Conditions. Diagnosis. Treatment.", core_p="From the gene to the clinic: what matters to people and their families.",
               res_h="A result needs<br>an explanation.", res_p="A predisposition is not destiny. A negative test has limits. A variant of uncertain significance is not, on its own, a diagnosis.", res_btn="How to read a result",
               fam_e="Genetic counselling", fam_h="Information for people and families", fam_p="A genetic test can have consequences for your relatives, your reproductive decisions and your follow-up. Consent and an explanation of the uncertainties are part of good care.", fam_btn="What genetic counselling is",
               sci_e="News and advances", sci_h="Research, in context", sci_p="Links to original sources, with what to look for in each. No news story promises that a treatment is available.",
               sci=[("Recent publications", "Tell apart laboratory studies, trials, reviews and preliminary results.", "https://pubmed.ncbi.nlm.nih.gov/?term=medical+genetics&sort=date", "PubMed"),
                    ("Clinical trials", "Check who is included, which phase it is in, what it is compared with and what results it has.", "https://clinicaltrials.gov/search?cond=Genetic%20Diseases", "ClinicalTrials.gov"),
                    ("Authorised medicines", "Check the indication, who can receive it and whether it is authorised where you live.", "https://www.ema.europa.eu/en/medicines", "EMA")],
               consult="Look up", fuentes_btn="All sources →",
               fuentes_title="Sources and library", fuentes_desc="Where to read more, cross-check and verify: reliable genetics sources for patients, families and professionals, with what to know about each.",
               libros_h="Reference library", libros_p="Textbooks we rely on to write and review the content.",
               doors_e="Three ways in", doors_h="Understand, decide, discover",
               doors=[("Understand", "The basics", [("basics/what-is-dna/", "What is DNA"), ("basics/genes-chromosomes-and-genome/", "Genes, chromosomes and genome"), ("heredity/", "How traits are inherited"), ("glossary/", "Glossary")]),
                      ("Decide", "Genetics and health", [("diagnosis/panels-exome-and-genome/", "Panels, exome and genome"), ("diagnosis/carrier-and-preimplantation-testing/", "Carrier testing"), ("diagnosis/direct-to-consumer-genetic-tests/", "Mail-order ancestry kits"), ("diagnosis/genetic-counselling/", "What genetic counselling is")]),
                      ("Discover", "Science and the future", [("history/", "History of genetics"), ("treatments/crispr-explained/", "CRISPR explained"), ("sources/", "Sources and library"), ("quiz/", "Quiz")])],
               map_e="A map of genetics", map_h="What would you like to understand?", map_p="Five sections, from the very basics to the newest science.",
               hist_e="History", hist_h="From Mendel's peas to the complete genome", hist_btn="See the full history →",
               blog_e="Blog", blog_h="Latest posts", blog_btn="All posts →",
               who_t="About", who_h="Created by a family doctor",
               who_p="Alejandro Rosàs, a family physician with <b>over 38 years in primary care</b> and a specialist in Preventive Medicine and Public Health. Licensed in Barcelona, no. 28574.",
               who_btn="About the author", ed_t="Genetics in context", ed_h="No determinism, no alarmism",
               ed_p="Genes matter, but they rarely decide everything. We explain the evidence, its limits and the ethical questions.", ed_btn="Our editorial approach",
               hist_title="History of genetics", hist_desc="A timeline of genetics, from ancient plant and animal breeding to CRISPR and the human pangenome.",
               glos_title="Genetics glossary", quiz_title="How much do you know about genetics?", blog_title="Geneticapedia blog",
               blog_desc="News, explainers and frequently asked questions about genetics, without the jargon.",
               photo_alt="Maclyn McCarty shaking hands with Francis Crick, with James Watson between them", photo_t="McCarty, Watson and Crick", photo_c="Left to right: Maclyn McCarty, James Watson and Francis Crick. Photo: Marjorie McCarty, PLOS Biology (2005), CC BY 2.5. <a href=\"blog/avery-macleod-and-mccarty/\">The story behind the photo</a>",
               q_daily="Daily quiz", q_all="All", p404="Page not found", p404d="The page you are looking for does not exist or has moved.", back="Back to the home page",
               date_fmt=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%-d %B %Y")),
}


def build(lang, g, allsec, search):
    T, page, write, md, prefix, SECTIONS, SRC, TODAY, MAIL, SITE = (g[k] for k in ("T", "page", "write", "md", "prefix", "SECTIONS", "SRC", "TODAY", "MAIL", "SITE"))
    l = L[lang]
    t = T[lang]
    lp = "en/" if lang == "en" else ""
    if not os.path.exists(os.path.join(SRC, lang, "datos.py")):
        return build_lite(lang, g, search)
    data = runpy.run_path(os.path.join(SRC, lang, "datos.py"))

    # ---------- blog ----------
    posts = []
    bdir = os.path.join(SRC, lang, "blog")
    for fn in sorted(os.listdir(bdir), reverse=True):
        if fn.endswith(".md"):
            meta, body = g["read_md"](os.path.join(bdir, fn))
            meta["slug"] = fn[11:-3]
            meta["date"] = fn[:10]
            meta["body"] = body
            posts.append(meta)
    brief_l = "Noticia breve" if lang == "es" else "News in brief"
    for p in posts:
        path = f"{lp}blog/{p['slug']}/"
        h = g["glos_link"](md(p["body"], lang), lang)
        crumbs = f'<nav class="crumbs" aria-label="breadcrumb"><a href="../../">{t["home"]}</a> › <a href="../">Blog</a></nav>' if not lp else f'<nav class="crumbs" aria-label="breadcrumb"><a href="../../">{t["home"]}</a> › <a href="../">Blog</a></nav>'
        others = "".join(f'<li><a href="../{o["slug"]}/">{esc(o["title"])}</a></li>' for o in posts if o is not p)
        out = f"""<header class="phead wrap">{crumbs}<span class="eyebrow">Blog · {(brief_l + " · ") if p.get("tipo") == "breve" else ""}<time datetime="{p['date']}">{l['date_fmt'](p['date'])}</time></span><h1>{esc(p['title'])}</h1><p class="lead">{esc(p['desc'])}</p></header>
<div class="wrap article"><article class="prose">{h}<p class="meta">{t['by']} · {t['err']} <a href="mailto:{MAIL}">{MAIL}</a></p></article>
<aside class="aside"><div class="box"><h4>{t['posts']}</h4><ul>{others}</ul><p style="margin:10px 0 0"><a href="../">{t['allposts']} →</a></p></div></aside></div>"""
        write(path, page(lang, path, p["title"], p["desc"], out, ldtype="BlogPosting", og_type="article", alt=p.get("alt"),
                         extra_ld={"headline": p["title"], "datePublished": p["date"], "author": {"@type": "Person", "name": "Alejandro Rosàs"}}))
        search.append({"t": p["title"], "d": p["desc"], "u": path[len(lp):], "k": "Blog", "n": g["strip_tags"](h)[:400]})
    brief_l = "Noticia breve" if lang == "es" else "News in brief"
    def _kind(p):
        return "breve" if p.get("tipo") == "breve" else "art"
    cards = "".join(f'<a class="card" data-kind="{_kind(p)}" href="./{p["slug"]}/"><span class="tag">{(brief_l + " · ") if _kind(p) == "breve" else ""}{l["date_fmt"](p["date"])}</span><h3>{esc(p["title"])}</h3><p>{esc(p["desc"])}</p><span class="more">{t["read"]}</span></a>' for p in posts)
    bopts = [("all", "Todo"), ("breve", "Noticias breves"), ("art", "Artículos")] if lang == "es" else [("all", "All"), ("breve", "News in brief"), ("art", "Articles")]
    bchips = "".join(f'<button type="button" class="chip{" on" if k == "all" else ""}" data-k="{k}">{v}</button>' for k, v in bopts)
    bjs = """<script>(function(){var c=document.querySelectorAll('.bchips .chip'),a=document.querySelectorAll('.bgrid .card');c.forEach(function(b){b.addEventListener('click',function(){var k=b.getAttribute('data-k');c.forEach(function(x){x.classList.toggle('on',x===b)});a.forEach(function(e){e.style.display=(k==='all'||e.getAttribute('data-kind')===k)?'':'none'})})});var q=location.hash.slice(1);c.forEach(function(b){if(b.getAttribute('data-k')===q)b.click()})})();</script>"""
    path = f"{lp}blog/"
    write(path, page(lang, path, l["blog_title"], l["blog_desc"], f'<header class="phead wrap"><span class="eyebrow">Blog</span><h1>{l["blog_title"]}</h1><p class="lead">{l["blog_desc"]}</p><p><a href="./feed.xml">RSS</a></p><div class="tlchips bchips" role="group">{bchips}</div></header><section class="wrap section" style="padding-top:0"><div class="grid bgrid">{cards}</div></section>{bjs}', ldtype="Blog"))
    items = "".join(f"<item><title>{esc(p['title'])}</title><link>{SITE}{lp}blog/{p['slug']}/</link><guid>{SITE}{lp}blog/{p['slug']}/</guid><pubDate>{format_datetime(datetime.strptime(p['date'], '%Y-%m-%d').replace(hour=8, tzinfo=timezone.utc))}</pubDate><description>{esc(p['desc'])}</description></item>" for p in posts)
    rss = f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Geneticapedia</title><link>{SITE}{lp}</link><description>{esc(l["blog_desc"])}</description><language>{lang}</language>{items}</channel></rss>\n'
    write(f"{lp}blog/feed.xml", rss)

    # ---------- historia ----------
    tl = data["HISTORIA"]
    path = f"{lp}{l['hist']}/"
    def _yr(y):
        m = re.search(r"\d{4}", y)
        return int(m.group()) if m else 0
    eras = ([("all", "Todo"), ("e1", "Antes de 1900"), ("e2", "1900-1952"), ("e3", "1953-1989"), ("e4", "1990-2009"), ("e5", "2010-hoy")] if lang == "es"
            else [("all", "All"), ("e1", "Before 1900"), ("e2", "1900-1952"), ("e3", "1953-1989"), ("e4", "1990-2009"), ("e5", "2010-today")])
    def _era(y):
        n = _yr(y)
        return "e1" if n < 1900 else "e2" if n < 1953 else "e3" if n < 1990 else "e4" if n < 2010 else "e5"
    more_l = "Leer más" if lang == "es" else "Read more"
    def _span(y):
        ns = [int(v) for v in re.findall(r"\d{4}", y)]
        return (ns[0], ns[-1]) if ns else (0, 0)
    order = sorted(range(len(tl)), key=lambda i: _span(tl[i][0]))
    used_imgs = []
    def _thumb(i, x):
        cands = [f.replace("@@L@@", lang) for f in HIST_IMG.get(i, [])]
        fn = next((f for f in cands if g["has_img"](f)), None)
        if not fn:
            return ""
        if fn not in used_imgs:
            used_imgs.append(fn)
        c = g["IMG"].get(fn, {})
        wh = f' width="{c["w"]}" height="{c["h"]}"' if c.get("w") and c.get("h") else ""
        return f'<figure class="tlimg"><img src="{g["isrc"](fn, "../" * path.count("/"))}" alt="{esc(x[1])}"{wh} loading="lazy" decoding="async"></figure>'
    def _li(i):
        x = tl[i]
        return (f'<li id="h{i}">{_thumb(i, x)}<span class="y">{esc(x[0])}</span><h3>{esc(x[1])}</h3><p class="sum">{x[2]}</p>'
                + (f'<details class="det"><summary>{more_l}</summary><p>{x[3]}</p></details>' if len(x) > 3 else '') + '</li>')
    era_names = dict(eras)
    era_intro = ({"e1": "De la domesticación a Mendel y el descubrimiento del ADN.", "e2": "Nace la genética: cromosomas, genes y la búsqueda del material hereditario.",
                  "e3": "La doble hélice, el código genético y las primeras herramientas para leer y cortar el ADN.", "e4": "Genes de enfermedades, clonación y el primer genoma humano.",
                  "e5": "CRISPR, el genoma completo y la edición genética en pacientes."} if lang == "es" else
                 {"e1": "From domestication to Mendel and the discovery of DNA.", "e2": "Genetics is born: chromosomes, genes and the search for the hereditary material.",
                  "e3": "The double helix, the genetic code and the first tools to read and cut DNA.", "e4": "Disease genes, cloning and the first human genome.",
                  "e5": "CRISPR, the complete genome and gene editing in patients."})
    groups = {}
    for i in order:
        groups.setdefault(_era(tl[i][0]), []).append(i)
    # índice por épocas
    idx = "".join(f'<div class="eracard {k}"><a class="eh" href="#{k}"><span class="en">{esc(era_names[k])}</span><span class="ec">{len(groups.get(k, []))} {"hitos" if lang == "es" else "milestones"}</span></a><ul>'
                  + "".join(f'<li><a href="#h{i}"><b>{esc(tl[i][0])}</b> {esc(tl[i][1])}</a></li>' for i in groups.get(k, [])) + '</ul></div>'
                  for k, _ in eras if k != "all")
    secs = "".join(f'<section class="tlera" id="{k}" data-era="{k}"><h2 class="erah {k}">{esc(era_names[k])}</h2><p class="eraint">{era_intro[k]}</p><ol class="tl">'
                   + "".join(_li(i) for i in groups.get(k, [])) + '</ol></section>' for k, _ in eras if k != "all")
    chips = "".join(f'<button type="button" class="chip{" on" if k == "all" else ""}" data-era="{k}">{esc(v)}</button>' for k, v in eras)
    idx_h = "Las cinco épocas de un vistazo" if lang == "es" else "The five eras at a glance"
    flt = "Filtrar por época" if lang == "es" else "Filter by era"
    cred_h = "Créditos de las imágenes" if lang == "es" else "Image credits"
    creds = "".join(f"<li>{g['credit'](fn, lang)}</li>" for fn in used_imgs)
    refs = "".join(f"<li>{r}</li>" for r in data["HISTORIA_FUENTES"])
    js = """<script>(function(){var c=document.querySelectorAll('.tlchips .chip'),s=document.querySelectorAll('section.tlera');function f(e){c.forEach(function(x){x.classList.toggle('on',x.getAttribute('data-era')===e)});s.forEach(function(l){l.style.display=(e==='all'||l.getAttribute('data-era')===e)?'':'none'})}c.forEach(function(b){b.addEventListener('click',function(){f(b.getAttribute('data-era'))})});document.querySelectorAll('.eracard a').forEach(function(a){a.addEventListener('click',function(){f('all');var t=document.querySelector(a.getAttribute('href'));if(t){var x=t.querySelector('details');if(x&&t.tagName==='LI')x.open=true}})})})();</script>"""
    out = f"""<header class="phead wrap"><span class="eyebrow">{l['hist_e']}</span><h1>{l['hist_title']}</h1><p class="lead">{l['hist_desc']}</p></header>
<div class="wrap"><h2 class="idxh">{idx_h}</h2><div class="eragrid">{idx}</div></div>
<div class="wrap narrow"><div class="tlchips" role="group" aria-label="{flt}"><span class="flt">{flt}:</span>{chips}</div></div>
<div class="wrap narrow prose">{secs}<details class="credits"><summary>{cred_h}</summary><ul>{creds}</ul></details><h2>{t['refs']}</h2><ol class="refs">{refs}</ol><p class="meta">{t['by']} · {t['upd']}: {TODAY}</p></div>{js}"""
    write(path, page(lang, path, l["hist_title"], l["hist_desc"], out, ldtype="Article", extra_ld={"headline": l["hist_title"]}))
    search.append({"t": l["hist_title"], "d": l["hist_desc"], "u": path[len(lp):], "k": l["hist_e"], "n": " ".join(x[1] for x in tl)})

    # ---------- glosario ----------
    gl = sorted(data["GLOSARIO"], key=lambda x: slugify(x[0]))
    path = f"{lp}{l['glos']}/"
    letters = []
    blocks = ""
    cur = None
    for term, d in gl:
        L0 = slugify(term)[0].upper()
        if L0 != cur:
            if cur:
                blocks += "</dl>"
            cur = L0
            letters.append(L0)
            blocks += f'<h2 id="{L0}">{L0}</h2><dl class="gl-list">'
        _gl = data.get("GLOS_LINKS", {}) if isinstance(data, dict) else getattr(data, "GLOS_LINKS", {})
        if term in _gl and "<a " not in d:
            d = d + f' <a href="../{_gl[term]}">{"Leer más" if lang == "es" else "Read more"}</a>.'
        blocks += f'<dt id="{slugify(term)}">{esc(term)}</dt><dd>{d}</dd>'
        search.append({"t": term, "d": re.sub("<[^>]+>", "", d), "u": f"{l['glos']}/#{slugify(term)}", "k": t.get("glos", "Glosario" if lang == "es" else "Glossary")})
    blocks += "</dl>"
    gdesc = (f"{len(gl)} términos de genética explicados de forma breve y clara, de ADN a variante genética." if lang == "es"
             else f"{len(gl)} genetics terms explained briefly and clearly, from allele to X-linked.")
    nav = "".join(f'<a href="#{x}">{x}</a>' for x in letters)
    out = f"""<header class="phead wrap"><span class="eyebrow">{'Glosario' if lang=='es' else 'Glossary'}</span><h1>{l['glos_title']}</h1><p class="lead">{gdesc}</p></header>
<div class="wrap narrow prose"><p class="glletras" style="display:flex;flex-wrap:wrap;gap:6px 12px;font-weight:600">{nav}</p>{blocks}<p class="meta">{t['by']} · {t['upd']}: {TODAY}</p></div>"""
    write(path, page(lang, path, l["glos_title"], gdesc, out, ldtype="DefinedTermSet"))
    search.append({"t": l["glos_title"], "d": gdesc, "u": path[len(lp):], "k": "", "n": ""})

    # ---------- quiz ----------
    qs = [dict(x) for x in data["QUIZ"]]
    for i, x in enumerate(qs):
        x.setdefault("nivel", "eso" if i in QUIZ_ESO else "bach")
    temas = data["QUIZ_TEMAS"]
    path = f"{lp}quiz/"
    qdesc = (f"{len(qs)} preguntas con explicación. Juega al quiz diario de 10 preguntas, elige un tema o un nivel (ESO o Bachillerato)." if lang == "es"
             else f"{len(qs)} questions with explanations. Play the daily 10-question quiz, pick a topic or a level.")
    niv = [("n:eso", "Nivel ESO"), ("n:bach", "Nivel Bachillerato")] if lang == "es" else [("n:eso", "Level: ages 12-16"), ("n:bach", "Level: ages 16-18")]
    btns = f'<button class="on" data-m="diario">{l["q_daily"]}</button><button data-m="*">{l["q_all"]}</button>' + "".join(f'<button class="lvl" data-m="{k}">{v}</button>' for k, v in niv) + "".join(f'<button data-m="{k}">{esc(v)}</button>' for k, v in temas.items())
    out = f"""<header class="phead wrap"><span class="eyebrow">Quiz</span><h1>{l['quiz_title']}</h1><p class="lead">{qdesc}</p></header>
<div class="wrap narrow"><div class="filters" id="quiz-modes">{btns}</div>
<div class="quiz" id="bigquiz" data-all="{esc(json.dumps(qs, ensure_ascii=False))}"></div></div>"""
    write(path, page(lang, path, l["quiz_title"], qdesc, out))
    search.append({"t": l["quiz_title"], "d": qdesc, "u": path[len(lp):], "k": "Quiz", "n": ""})

    # ---------- proyecto ----------
    for slug, _ in g["PROJECT"][lang]:
        g["simple_page"](lang, slug, search)

    # ---------- fuentes ----------
    path = f"{lp}{l['fuentes']}/"
    groups = "".join(f'<h2>{esc(gname)}</h2><dl class="gl-list">' + "".join(f'<dt><a href="{u}" rel="noopener">{esc(nm)}</a> ↗</dt><dd>{esc(dd)}</dd>' for nm, u, dd in items) + "</dl>" for gname, items in data["FUENTES"])
    libros = "".join(f"<li>{b}</li>" for b in data["LIBROS"])
    out = f"""<header class="phead wrap"><span class="eyebrow">{t['refs']}</span><h1>{l['fuentes_title']}</h1><p class="lead">{l['fuentes_desc']}</p></header>
<div class="wrap narrow prose"><div class="note">{l['src_note']}</div>{groups}<h2>{l['libros_h']}</h2><p>{l['libros_p']}</p><ul>{libros}</ul><p class="meta">{t['upd']}: {TODAY}</p></div>"""
    write(path, page(lang, path, l["fuentes_title"], l["fuentes_desc"], out, ldtype="CollectionPage"))
    search.append({"t": l["fuentes_title"], "d": l["fuentes_desc"], "u": path[len(lp):], "k": t["refs"], "n": " ".join(nm for _, it in data["FUENTES"] for nm, _, _ in it)})

    # ---------- portada ----------
    r = "./" if lang == "es" else "../"
    base = "./"
    secs = SECTIONS[lang]
    seccards = "".join(f'<a class="card" href="{base}{s[0]}/"><span class="num">{i:02d}</span><span class="tag">{esc(s[1])}</span><h3>{esc(s[2])}</h3><p>{esc(s[3])}</p><span class="more">{len(allsec.get(s[0], []))} {"artículos" if lang=="es" else "articles"} →</span></a>' for i, s in enumerate([s for s in secs if allsec.get(s[0])], 1))
    doors = "".join(f'<div class="door"><span class="tag">{a}</span><h3>{b}</h3><ul>' + "".join(f'<li><a href="{base}{u}">{n}</a></li>' for u, n in links) + "</ul></div>" for a, b, links in l["doors"])
    hl = data["HISTORIA"]
    pick = [hl[i] for i in data["HISTORIA_PORTADA"]]
    eras = "".join(f'<div class="era"><time>{esc(y)}</time><h3 style="color:#fff;margin:4px 0">{esc(h)}</h3><p>{re.sub("<[^>]+>", "", tx)[:150].rsplit(" ",1)[0].rstrip(".,;:")}…</p></div>' for y, h, tx, *_ in pick)
    pcards = "".join(f'<a class="card" href="{base}blog/{p["slug"]}/"><span class="tag">{l["date_fmt"](p["date"])}</span><h3>{esc(p["title"])}</h3><p>{esc(p["desc"])}</p><span class="more">{t["read"]}</span></a>' for p in posts[:3])
    n = lambda k: len(allsec.get(k, []))
    corecards = "".join(f'<a class="card big" href="{base}{s[0]}/"><span class="tag">{esc(s[1])}</span><h3>{esc(s[2])}</h3><p>{esc(s[3])}</p><span class="more">{n(s[0])} {"fichas" if lang=="es" else "entries"} →</span></a>' for s in secs[:3])
    basecards = "".join(f'<a class="card" href="{base}{s[0]}/"><span class="tag">{esc(s[1])}</span><h3>{esc(s[2])}</h3><p>{esc(s[3])}</p><span class="more">{n(s[0])} {"artículos" if lang=="es" else "articles"} →</span></a>' for s in secs[3:] if allsec.get(s[0]))
    scicards = "".join(f'<a class="card" href="{u}" rel="noopener"><span class="tag">{l["consult"]} · {esc(src)}</span><h3>{esc(h)}</h3><p>{esc(d)}</p><span class="more">{esc(src)} ↗</span></a>' for h, d, u, src in l["sci"])
    body = f"""<section class="wrap hero">
  <div>
    <span class="eyebrow">{l['eyebrow']}</span>
    <h1>{l['h1']}</h1>
    <p class="lead">{l['lead']}</p>
    <form class="search" role="search" onsubmit="return false"><input type="search" id="q" placeholder="{l['ph']}" aria-label="{l['btn']}" autocomplete="off"><button type="submit">{l['btn']}</button><div class="results" id="results" hidden></div></form>
    <div class="actions"><a class="btn primary" href="{base}{secs[0][0]}/">{l['start']}</a><a class="btn" href="{base}{secs[1][0]}/">{l['play']}</a></div>
    <p class="hnote">{l['note']}</p>
  </div>
  <figure class="arch"><img src="{r}assets/img/watson-crick-mccarty.jpg" width="1100" height="864" alt="{l['photo_alt']}" decoding="async" fetchpriority="high" style="object-position:62% 40%"><figcaption><b>{l['photo_t']}</b>{l['photo_c']}</figcaption></figure>
</section>
<div class="wrap"><div class="trust">{''.join(f'<span><b>{x}</b></span>' for x in l['trust'][:-1])}<span>{l['trust'][-1]}</span></div></div>

<section class="section wrap" id="mapa">
  <div class="shead"><div><span class="eyebrow">{l['core_e']}</span><h2>{l['core_h']}</h2></div><p>{l['core_p']}</p></div>
  <div class="grid core">{corecards}</div>
  <div class="grid g2" style="margin-top:16px">{basecards}</div>
</section>

<section class="wrap section"><div class="split2">
  <div class="dark2"><h2>{l['res_h']}</h2><p>{l['res_p']}</p><a class="btn" href="{base}{l['res_url']}">{l['res_btn']}</a></div>
  <div class="fam"><span class="eyebrow">{l['fam_e']}</span><h2>{l['fam_h']}</h2><p>{l['fam_p']}</p><a class="btn primary" href="{base}{l['fam_url']}">{l['fam_btn']}</a></div>
</div></section>

<section class="section wrap">
  <div class="shead"><div><span class="eyebrow">{l['doors_e']}</span><h2>{l['doors_h']}</h2></div></div>
  <div class="doors">{doors}</div>
</section>

<section class="darkband"><div class="wrap section">
  <div class="shead"><div><span class="eyebrow">{l['hist_e']}</span><h2 style="color:#fff">{l['hist_h']}</h2></div><a class="btn" href="{base}{l['hist']}/">{l['hist_btn']}</a></div>
  <div class="eras">{eras}</div>
</div></section>

<section class="section wrap">
  <div class="shead"><div><span class="eyebrow">{l['sci_e']}</span><h2>{l['sci_h']}</h2></div><a class="btn" href="{base}{l['fuentes']}/">{l['fuentes_btn']}</a></div>
  <p style="margin:-6px 0 16px;color:var(--mute);max-width:720px">{l['sci_p']}</p>
  <div class="grid">{scicards}</div>
</section>

<section class="section wrap">
  <div class="shead"><div><span class="eyebrow">{l['blog_e']}</span><h2>{l['blog_h']}</h2></div><a class="btn" href="{base}blog/">{l['blog_btn']}</a></div>
  <div class="grid">{pcards}</div>
</section>

<section class="wrap" style="margin-bottom:22px"><div class="door" style="background:var(--soft2);display:grid;grid-template-columns:auto 1fr auto;gap:22px;align-items:center" id="autor">
  <span class="sym" style="width:64px;height:64px;border:1.5px solid var(--accent2);border-radius:50%;display:grid;place-items:center;font:30px var(--serif);color:var(--accent2)">AR</span>
  <div><span class="tag">{l['who_t']}</span><h3 style="margin:6px 0">{l['who_h']}</h3><p style="margin:0;color:var(--mute)">{l['who_p']}</p></div>
  <a class="btn" href="{base}{g['PROJECT'][lang][0][0]}/">{l['who_btn']}</a>
</div></section>
<section class="wrap"><div class="door" style="display:flex;justify-content:space-between;gap:20px;align-items:center;flex-wrap:wrap">
  <div><span class="tag">{l['ed_t']}</span><h3>{l['ed_h']}</h3><p style="margin:0;color:var(--mute)">{l['ed_p']}</p></div>
  <a class="btn primary" href="{base}{g['PROJECT'][lang][1][0]}/">{l['ed_btn']}</a>
</div></section>"""
    title = "Geneticapedia · " + ("El ADN, explicado con claridad" if lang == "es" else "DNA, clearly explained")
    write(lp, page(lang, lp, title, t["desc"], body, full_title=True))

    # ---------- 404 ----------
    if lang == "es":
        out = f'<header class="phead wrap"><span class="eyebrow">404</span><h1>{l["p404"]}</h1><p class="lead">{l["p404d"]}</p><p><a class="btn primary" href="/">{l["back"]}</a> <a class="btn" href="/en/">English</a></p></header>'
        h = page(lang, "404.html", l["p404"], l["p404d"], out)
        # 404 se sirve desde cualquier ruta: rutas absolutas
        h = h.replace('href="./', 'href="/').replace('src="./', 'src="/')
        write("404.html", h)


def build_lite(lang, g, search):
    """Versión inicial en inglés: portada y páginas del proyecto; el resto enlaza a la versión en castellano."""
    T, page, write = g["T"], g["page"], g["write"]
    l = L[lang]
    t = T[lang]
    for slug, _ in g["PROJECT"][lang]:
        g["simple_page"](lang, slug, search)
    es_secs = g["SECTIONS"]["es"]
    cards = "".join(f'<a class="card" href="../{es[0]}/" hreflang="es"><span class="num">{i:02d}</span><span class="tag">{esc(en[1])}</span><h3>{esc(en[2])}</h3><p>{esc(en[3])}</p><span class="more">Read in Spanish →</span></a>' for i, (es, en) in enumerate(zip(es_secs, g["SECTIONS"][lang]), 1))
    body = f"""<section class="wrap hero">
  <div>
    <span class="eyebrow">{l['eyebrow']}</span>
    <h1>{l['h1']}</h1>
    <p class="lead">{l['lead']}</p>
    <div class="note" style="margin:18px 0 0">The English edition is on its way. All sections are already available in Spanish.</div>
    <div class="actions"><a class="btn primary" href="../" hreflang="es">Visit the Spanish edition →</a></div>
  </div>
  <figure class="arch"><img src="../assets/img/watson-crick-mccarty.jpg" width="1100" height="864" alt="{l['photo_alt']}" decoding="async" fetchpriority="high" style="object-position:62% 40%"><figcaption><b>{l['photo_t']}</b>{l['photo_c']}</figcaption></figure>
</section>
<section class="section wrap">
  <div class="shead"><div><span class="eyebrow">{l['map_e']}</span><h2>{l['map_h']}</h2></div><p>{l['map_p']}</p></div>
  <div class="grid">{cards}</div>
</section>
<section class="wrap" style="margin-bottom:22px"><div class="door" style="background:var(--soft2);display:grid;grid-template-columns:auto 1fr auto;gap:22px;align-items:center" id="autor">
  <span class="sym" style="width:64px;height:64px;border:1.5px solid var(--accent2);border-radius:50%;display:grid;place-items:center;font:30px var(--serif);color:var(--accent2)">AR</span>
  <div><span class="tag">{l['who_t']}</span><h3 style="margin:6px 0">{l['who_h']}</h3><p style="margin:0;color:var(--mute)">{l['who_p']}</p></div>
  <a class="btn" href="./about/">{l['who_btn']}</a>
</div></section>"""
    write("en/", page(lang, "en/", "Geneticapedia · DNA, clearly explained", t["desc"], body, full_title=True))
