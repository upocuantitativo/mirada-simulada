# -*- coding: utf-8 -*-
"""Reúne los informes del equipo (salida/*.md) y las imágenes en un único Word presentable, con portada y logos.

    python tools/informe_word.py salida

Salida: salida/Informe_equipo.docx. Los .md se quedan: son los que leen los agentes y las comprobaciones.
"""
import datetime, glob, os, re, sys
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dibujar import imagen_antes
from powerbi_pbip import ENTRADA
LOGOS = os.path.join(RAIZ, "tools", "logos")
AZUL, GRIS, ROJO = RGBColor(0x1F, 0x1F, 0x6B), RGBColor(0x50, 0x54, 0x6B), RGBColor(0xC2, 0x29, 0x0F)
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def campo_pagina(par):
    r = par.add_run()
    for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    r.font.size = Pt(9); r.font.color.rgb = GRIS


def en_linea(par, texto, tam=None, color=None):
    """Negrita **x**, cursiva *x*, código `x` y enlaces [t](u) de Markdown."""
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|(?<!\*)\*[^*\s][^*]*\*(?!\*))", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            r = par.add_run(trozo[2:-2]); r.bold = True
        elif trozo.startswith("`"):
            r = par.add_run(trozo[1:-1]); r.font.name = "Consolas"; r.font.color.rgb = AZUL
        elif trozo.startswith("*"):
            r = par.add_run(trozo[1:-1]); r.italic = True
        else:
            r = par.add_run(trozo)
        if tam:
            r.font.size = Pt(tam)
        if color is not None and not trozo.startswith("`"):
            r.font.color.rgb = color


def tabla(doc, filas):
    celdas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
    celdas = [f for f in celdas if not all(re.fullmatch(r":?-{2,}:?", c) for c in f if c)]
    n = max(len(f) for f in celdas)
    t = doc.add_table(rows=0, cols=n); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, f in enumerate(celdas):
        fila = t.add_row()
        if i == 0:
            trPr = fila._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); trPr.append(h)
        trPr = fila._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        for j in range(n):
            c = fila.cells[j]; p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            txt = f[j] if j < len(f) else ""
            if i == 0:
                sombrear(c, "1F1F6B"); en_linea(p, txt.replace("**", ""), 9, RGBColor(0xFF, 0xFF, 0xFF))
                for r in p.runs:
                    r.bold = True
            else:
                en_linea(p, txt, 9)
                if re.search(r"ALERTA|No cumple", txt):
                    sombrear(c, "FDEEE9")
    # anchos según el contenido de cada columna (17 cm en total)
    largo = [max(8, len(celdas[0][j]) + 3 if j < len(celdas[0]) else 0, min(45, max(len(f[j]) if j < len(f) else 0 for f in celdas)) ** 0.5 * 4.5)
             for j in range(n)]
    anchos = [Cm(17 * l / sum(largo)) for l in largo]
    t.autofit = False
    for j, col in enumerate(t.columns):
        col.width = anchos[j]
    for fila in t.rows:
        for j, c in enumerate(fila.cells):
            c.width = anchos[j]
    doc.add_paragraph()


def markdown(doc, ruta, nivel_base=1, saltar_titulo=False):
    if not os.path.exists(ruta):
        p = doc.add_paragraph(); en_linea(p, "(No se ha generado `" + os.path.basename(ruta) + "`.)", color=GRIS); return
    lineas = open(ruta, encoding="utf-8").read().splitlines()
    i, primero = 0, True
    while i < len(lineas):
        l = lineas[i]
        if l.startswith("```"):
            bloque = []; i += 1
            while i < len(lineas) and not lineas[i].startswith("```"):
                bloque.append(lineas[i]); i += 1
            t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; c = t.cell(0, 0); sombrear(c, "F5F6FA")
            p = c.paragraphs[0]
            for k, b in enumerate(bloque):
                r = p.add_run(b); r.font.name = "Consolas"; r.font.size = Pt(9)
                if k < len(bloque) - 1:
                    r.add_break()
            doc.add_paragraph(); i += 1; continue
        if l.lstrip().startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].lstrip().startswith("|"):
                filas.append(lineas[i]); i += 1
            tabla(doc, filas); continue
        m = re.match(r"^(#{1,6})\s+(.*)", l)
        if m:
            if primero and saltar_titulo:
                primero = False; i += 1; continue
            primero = False
            doc.add_heading(re.sub(r"\*\*", "", m.group(2)), level=min(9, nivel_base + len(m.group(1))))
        elif re.match(r"^\s*[-*]\s+", l):
            txt = re.sub(r"^\s*[-*]\s+", "", l).replace("[ ] ", "☐ ").replace("[x] ", "☑ ")
            p = doc.add_paragraph(style="List Bullet" if not l.startswith("   ") else "List Bullet 2"); en_linea(p, txt)
        elif re.match(r"^\s*\d+[.)]\s+", l):
            p = doc.add_paragraph(style="List Number"); en_linea(p, re.sub(r"^\s*\d+[.)]\s+", "", l))
        elif l.startswith(">"):
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.8); en_linea(p, l.lstrip("> "), color=GRIS)
        elif l.strip():
            p = doc.add_paragraph(); en_linea(p, l)
        primero = primero and not l.strip()
        i += 1


def imagen(doc, ruta, ancho_cm, pie):
    if not os.path.exists(ruta):
        return
    doc.add_picture(ruta, width=Cm(ancho_cm)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; en_linea(p, pie, 9, GRIS)


def brief():
    datos = {}
    ruta = os.path.join(ENTRADA, "brief.md")
    if os.path.exists(ruta):
        for m in re.finditer(r"^- \*\*([^*:]+):?\*\*:?\s*(.*)$", open(ruta, encoding="utf-8").read(), re.M):
            datos[m.group(1).strip().rstrip(":")] = m.group(2).strip()
    return datos


def main():
    sal = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "salida")
    b = brief()
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for n, tam in (("Title", 30), ("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12), ("Heading 4", 11)):
        s = doc.styles[n]; s.font.name = "Calibri"; s.font.size = Pt(tam); s.font.color.rgb = AZUL; s.font.bold = True
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, lado, Cm(2))
    sec.different_first_page_header_footer = True

    # portada
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for f, alto in (("logoFp.png", 2.0), ("logoUPO.png", 1.35), ("logoFundacion.png", 1.45), ("microcredenciales.png", 1.15)):
        ruta = os.path.join(LOGOS, f)
        if os.path.exists(ruta):
            p.add_run().add_picture(ruta, height=Cm(alto)); p.add_run("      ")
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph(); en_linea(p, "Microcredencial «Visualización y narrativa de datos con Power BI» · Módulo 1, Tema 1.3", 11, GRIS)
    p = doc.add_paragraph(); r = p.add_run("Revisión con un equipo de agentes de IA"); r.bold = True; r.font.size = Pt(28); r.font.color.rgb = AZUL
    pieza = b.get("Pieza que se revisa", "")
    p = doc.add_paragraph(); en_linea(p, pieza, 14, GRIS)
    imagen(doc, os.path.join(sal, "antes_despues.png"), 17, "Antes y después. A la derecha, la propuesta del equipo con los cambios que aprobó la persona.")
    hoy = datetime.date.today()
    for et in ("Autor o autora", "Audiencia principal", "Decisión que debe tomar la audiencia"):
        if b.get(et):
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2); en_linea(p, "**" + et + ":** " + b[et], 11)
    p = doc.add_paragraph(); en_linea(p, "%d de %s de %d" % (hoy.day, MESES[hoy.month - 1], hoy.year), 11, GRIS)

    # cabecera y pie del resto de páginas
    cab = sec.header.paragraphs[0]
    for f, alto in (("logoFp.png", 0.8), ("logoUPO.png", 0.6), ("logoFundacion.png", 0.65)):
        ruta = os.path.join(LOGOS, f)
        if os.path.exists(ruta):
            cab.add_run().add_picture(ruta, height=Cm(alto)); cab.add_run("   ")
    r = cab.add_run("\tRevisión con un equipo de agentes · Módulo 1"); r.font.size = Pt(8); r.font.color.rgb = GRIS
    cab.paragraph_format.tab_stops.add_tab_stop(Cm(17), alignment=2)
    pie = sec.footer.paragraphs[0]; pie.alignment = WD_ALIGN_PARAGRAPH.CENTER; campo_pagina(pie)

    def capitulo(t):
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        doc.add_heading(t, level=1)

    capitulo("1. Resumen del equipo")
    markdown(doc, os.path.join(sal, "informe_equipo.md"), 1, saltar_titulo=True)

    capitulo("2. Antes y después")
    imagen(doc, imagen_antes(), 16, "Antes: la pieza original (entrada/%s)." % os.path.basename(imagen_antes()))
    imagen(doc, os.path.join(sal, "grafico_despues.png"), 16, "Después: la propuesta (salida/grafico_despues.png). La misma página está en el proyecto de Power BI.")
    doc.add_heading("Cómo la mira el comité (simulación)", level=2)
    imagen(doc, os.path.join(ENTRADA, "mapa_calor.png"), 13, "Mapa de calor del laboratorio Mirada simulada. Datos simulados, no es un registro ocular.")
    imagen(doc, os.path.join(ENTRADA, "recorrido.png"), 13, "Recorrido de una persona simulada del comité. Los números son el orden de las paradas.")
    p = doc.add_paragraph(); en_linea(p, "Para la prueba A/B, sube `salida/grafico_despues.png` al laboratorio con el mismo comité y la misma semilla (2026) y compara las métricas.", 10, GRIS)

    capitulo("3. Decisiones de la persona")
    markdown(doc, os.path.join(sal, "decisiones.md"), 1, saltar_titulo=True)

    for n, (f, t) in enumerate([("1_mirada.md", "Agente Mirada"), ("2_narrativa.md", "Agente Narrativa"), ("3_auditoria.md", "Agente Auditoría"),
                                ("4_mejora.md", "Agente Mejora"), ("5_powerbi.md", "Agente Power BI")], start=4):
        capitulo("%d. %s" % (n, t))
        markdown(doc, os.path.join(sal, f), 1, saltar_titulo=True)

    capitulo("9. Cobertura de los 43 criterios del Módulo 1")
    markdown(doc, os.path.join(sal, "cobertura.md"), 1, saltar_titulo=True)

    capitulo("10. Ficheros entregados")
    rel = lambda r: os.path.relpath(r, RAIZ).replace(os.sep, "/")
    lista = ["`%s`: el proyecto de Power BI mejorado. Ábrelo en Power BI Desktop." % rel(f) for f in glob.glob(os.path.join(sal, "powerbi", "*.pbip"))]
    lista += ["`%s`: la pieza original en Power BI, para comparar." % rel(f) for f in glob.glob(os.path.join(ENTRADA, "**", "*.pbi[px]"), recursive=True)]
    lista += ["`salida/grafico_despues.png` y `salida/antes_despues.png`: las imágenes de este informe.",
              "`salida/*.md`: los informes de cada agente en texto, tal como los escribieron."]
    for txt in lista:
        p = doc.add_paragraph(style="List Bullet"); en_linea(p, txt)

    cp = doc.core_properties
    cp.author = ""; cp.last_modified_by = ""; cp.comments = ""; cp.keywords = ""; cp.category = ""; cp.subject = ""
    cp.title = "Revisión con un equipo de agentes de IA"
    ruta = os.path.join(sal, "Informe_equipo.docx")
    doc.save(ruta)
    print("Informe en Word:", ruta)


if __name__ == "__main__":
    main()
