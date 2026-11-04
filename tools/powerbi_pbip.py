# -*- coding: utf-8 -*-
"""Crea el proyecto de Power BI (PBIP: modelo TMDL + informe PBIR) del gráfico de producción.

    python tools/powerbi_pbip.py antes                       -> entrada/powerbi/  (la pieza original, tal cual)
    python tools/powerbi_pbip.py despues salida/propuesta.json -> salida/powerbi/   (la pieza mejorada)

Ábrelo con el fichero .pbip en Power BI Desktop. Los datos de entrada/produccion.csv van dentro del proyecto, así que se
abre en cualquier equipo. Si avisa de que hay cambios pendientes, pulsa Aplicar cambios.

Antes de escribir nada, comprueba sin IA que cada cifra de los textos de la propuesta sale de los datos. Si alguna no sale,
no crea el proyecto y termina con código 2: la cifra vuelve al agente.
"""
import base64, csv, json, os, re, shutil, sys, uuid, zlib

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Datos: entrada/datos.json (si no existe, los del ejemplo). Una serie anual: una columna de año y una de valor.
# Sin entrada/ (repositorio recién descargado) se usa la del ejemplo, ejemplo/entrada/.
ENTRADA = os.path.join(RAIZ, "entrada")
if not os.path.isdir(ENTRADA) and os.path.isdir(os.path.join(RAIZ, "ejemplo", "entrada")):
    ENTRADA = os.path.join(RAIZ, "ejemplo", "entrada")
CFG = {"csv": "produccion.csv", "separador": ";", "tabla": "Produccion", "anio": "Anio", "valor": "Unidades"}
if os.path.exists(os.path.join(ENTRADA, "datos.json")):
    CFG.update(json.load(open(os.path.join(ENTRADA, "datos.json"), encoding="utf-8")))
CSV = os.path.join(ENTRADA, CFG["csv"])
TB, X, Y = CFG["tabla"], CFG["anio"], CFG["valor"]
T = "\t"
SCH = "https://developer.microsoft.com/json-schemas/fabric/"
R = SCH + "item/report/definition/"

# ── datos y cifras comprobables ────────────────────────────────────────
def _num(t):
    v = float(str(t).replace(",", ".")) if t not in (None, "") else 0.0
    return int(v) if v.is_integer() else v


FILAS = sorted((int(r[X]), _num(r[Y])) for r in csv.DictReader(open(CSV, encoding="utf-8-sig"), delimiter=CFG["separador"]))
ANIOS = [a for a, _ in FILAS]
U = dict(FILAS)
P, ULT = U[min(ANIOS)], U[max(ANIOS)]
AUM = {a: U[a] - U[a - 1] for a in ANIOS if a - 1 in U}
CALC = {
    Y + " totales": sum(U.values()), Y + " primer anio": P, Y + " ultimo anio": ULT,
    "Aumento acumulado": ULT - P, "Veces que se multiplica": ULT / P,
    "Aumento anual medio": (ULT - P) / (len(ANIOS) - 1), "Anios con caida": sum(1 for v in AUM.values() if v < 0),
    "Crecimiento acumulado": (ULT - P) / P,
}


def cifras_validas():
    s = set(ANIOS) | set(U.values()) | set(AUM.values()) | {len(ANIOS), len(ANIOS) - 1}
    for v in CALC.values():
        s |= {round(v, 1), round(v), round(v * 100), round(v * 100, 1)}
    for a in ANIOS:                      # aumentos entre dos años cualesquiera (p. ej. 2017-2021)
        for b in ANIOS:
            if b > a:
                s |= {U[b] - U[a], round(U[b] / U[a], 1), round(U[b] / U[a], 2), round((U[b] - U[a]) / U[a] * 100)}
    s = {round(v, 2) for v in s}
    return s | {abs(v) for v in s}        # el signo va en el texto («caída de 70,5» o «-70,5»)


def numeros(texto):
    """Números de un texto en formato español (1.065 = mil sesenta y cinco; 1.250,5; 6,0 = seis)."""
    out = []
    for m in re.finditer(r"(?<![\w.,])(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?(?![\d])", texto):
        t = m.group(0)
        out.append((t, float(t.replace(".", "").replace(",", "."))))
    return out


def comprobar(prop):
    ok, validas = True, cifras_validas()
    textos = [prop.get("titulo", ""), prop.get("subtitulo", ""), prop.get("tarjeta", {}).get("etiqueta", ""), prop.get("pie", "")]
    textos += [a.get("texto", "") for a in prop.get("anotaciones", [])]
    for tx in textos:
        for t, v in numeros(tx):
            if v not in validas and round(v, 1) not in validas:
                print("CIFRA SIN RESPALDO:", t, "en «" + tx + "»"); ok = False
    for c in prop.get("cifras", []):
        esperado = CALC.get(c.get("medida"))
        if esperado is None:
            print("Sin comprobar (medida no calculable aquí):", c.get("medida")); continue
        if abs(float(c.get("valor", "nan")) - esperado) > 0.05:
            print("NO CUADRA:", c["medida"], "propuesta", c.get("valor"), "· datos", round(esperado, 3)); ok = False
        else:
            print("OK  ", c["medida"], "=", round(esperado, 3))
    med = prop.get("tarjeta", {}).get("medida")
    if med and med not in dict((m[0], 1) for m in MEDIDAS) and med not in [m.get("nombre") for m in prop.get("medidas", [])]:
        print("La tarjeta usa una medida que no existe:", med); ok = False
    return ok


# ── utilidades ─────────────────────────────────────────────────────────
def guid(s):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "produccion-pbip/" + s))


def w(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def wj(ruta, obj):
    w(ruta, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def qn(n):
    return n if n.replace("_", "").isalnum() and n.isascii() else "'" + n + "'"


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def color(c):
    return {"solid": {"color": lit("'" + c + "'")}}


def s(t):
    return lit("'" + str(t).replace("'", "''") + "'")


# ── modelo ─────────────────────────────────────────────────────────────
# Medidas comprobadas en el motor de Power BI (mismas cifras de control que tools/verificar_powerbi.py)
_MEDIDAS = [
    ("Unidades totales", "SUM ( Produccion[Unidades] )", "#,0"),
    ("Unidades ultimo anio", "CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MAX ( Produccion[Anio] ) )", "#,0"),
    ("Unidades primer anio", "CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MIN ( Produccion[Anio] ) )", "#,0"),
    ("Aumento acumulado", "[Unidades ultimo anio] - [Unidades primer anio]", "+#,0;-#,0;0"),
    ("Veces que se multiplica", "DIVIDE ( [Unidades ultimo anio], [Unidades primer anio] )", "0.0"),
    ("Crecimiento acumulado", "DIVIDE ( [Aumento acumulado], [Unidades primer anio] )", "0%"),
    ("Aumento anual", "VAR A = MAX ( Produccion[Anio] ) VAR Previo = CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = A - 1 ) "
                      "RETURN IF ( NOT ISBLANK ( Previo ), SUM ( Produccion[Unidades] ) - Previo )", "+#,0;-#,0;0"),
    ("Aumento anual medio", "DIVIDE ( [Aumento acumulado], DISTINCTCOUNT ( Produccion[Anio] ) - 1 )", "0.0"),
    ("Anios con caida", "COALESCE ( COUNTROWS ( FILTER ( VALUES ( Produccion[Anio] ), [Aumento anual] < 0 ) ), 0 )", "0"),
    ("Titulo dinamico", 'IF ( HASONEVALUE ( Produccion[Anio] ), "Producción de " & VALUES ( Produccion[Anio] ) & ": " '
                        '& FORMAT ( [Unidades totales], "#,##0" ) & " unidades", "La producción pasó de " & [Unidades primer anio] '
                        '& " a " & [Unidades ultimo anio] & " unidades entre " & MIN ( Produccion[Anio] ) & " y " & MAX ( Produccion[Anio] ) '
                        '& " (+" & [Aumento acumulado] & ")" )', None),
]


def nombres(t):
    """Traduce los nombres del ejemplo (Produccion, Anio, Unidades) a los de entrada/datos.json."""
    t = re.sub(r"\bUnidades (totales|ultimo anio|primer anio)\b", lambda m: Y + " " + m.group(1), t)
    return t.replace("Produccion[Anio]", qn(TB) + "[" + X + "]").replace("Produccion[Unidades]", qn(TB) + "[" + Y + "]")


MEDIDAS = [(nombres(n), nombres(d), f) for n, d, f in _MEDIDAS]
if TB != "Produccion" or Y != "Unidades":   # el título dinámico habla de producción: solo vale para el ejemplo
    MEDIDAS = [m for m in MEDIDAS if m[0] != "Titulo dinamico"]


def m_csv():
    raw = open(CSV, "rb").read()
    raw = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    b = base64.b64encode(co.compress(raw) + co.flush()).decode("ascii")
    p = T * 4
    return ("\n" + T * 3).join([
        "let",
        p + 'Origen = Csv.Document(Binary.Decompress(Binary.FromText("' + b + '", BinaryEncoding.Base64), Compression.Deflate), '
            '[Delimiter="' + CFG["separador"] + '", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        p + "Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),",
        p + 'Tipos = Table.TransformColumnTypes(Encabezados, {{"%s", Int64.Type}, {"%s", %s}}, "es-ES"),' % (X, Y, "Int64.Type" if all(isinstance(v, int) for v in U.values()) else "type number"),
        p + 'ConFecha = Table.AddColumn(Tipos, "Fecha", each #date([%s], 12, 31), type date)' % X,
        "in", p + "ConFecha"])


def tabla(nombre, cols, fuente, calc=False, medidas=(), ocultas=(), extra=()):
    L = ["table " + qn(nombre), T + "lineageTag: " + guid("t/" + nombre)] + [T + e for e in extra] + [""]
    for nm, dax, fmt in medidas:
        L += [T + "measure " + qn(nm) + " = " + dax] + ([T * 2 + "formatString: " + fmt] if fmt else []) + [T * 2 + "lineageTag: " + guid("m/" + nm), ""]
    for c, t in cols:
        L += [T + "column " + qn(c), T * 2 + "dataType: " + t]
        if t == "dateTime":
            L.append(T * 2 + "formatString: dd/mm/yyyy")
        if c in ocultas:
            L.append(T * 2 + "isHidden")
        L += [T * 2 + "lineageTag: " + guid("c/" + nombre + "/" + c), T * 2 + "summarizeBy: none",
              T * 2 + "sourceColumn: " + ("[" + c + "]" if calc else c), ""]
    L += [T + "partition " + qn(nombre) + " = " + ("calculated" if calc else "m"), T * 2 + "mode: import", T * 2 + "source =", T * 3 + fuente, ""]
    return "\n".join(L)


def modelo(proy, nombre, extra_medidas):
    base = os.path.join(proy, nombre + ".SemanticModel")
    d = os.path.join(base, "definition")
    wj(os.path.join(base, "definition.pbism"), {"version": "4.0", "settings": {}})
    wj(os.path.join(base, ".platform"), {"$schema": SCH + "gitIntegration/platformProperties/2.0.0/schema.json",
                                         "metadata": {"type": "SemanticModel", "displayName": nombre},
                                         "config": {"version": "2.0", "logicalId": guid(nombre + "/modelo")}})
    w(os.path.join(d, "database.tmdl"), "database\n" + T + "compatibilityLevel: 1567\n")
    w(os.path.join(d, "model.tmdl"), "\n".join(["model Model", T + "culture: es-ES", T + "defaultPowerBIDataSourceVersion: powerBI_V3",
                                                T + "discourageImplicitMeasures", "", "ref table " + qn(TB), "ref table Calendario", ""]))
    w(os.path.join(d, "tables", TB + ".tmdl"),
      tabla(TB, [(X, "int64"), (Y, "int64" if all(isinstance(v, int) for v in U.values()) else "double"), ("Fecha", "dateTime")], m_csv(), medidas=MEDIDAS + extra_medidas, ocultas=("Fecha",)))
    w(os.path.join(d, "tables", "Calendario.tmdl"),
      tabla("Calendario", [("Date", "dateTime"), ("Anio", "int64")], calc=True, ocultas=("Date",), extra=("dataCategory: Time",),
            fuente="ADDCOLUMNS ( CALENDAR ( DATE ( %d, 1, 1 ), DATE ( %d, 12, 31 ) ), \"Anio\", YEAR ( [Date] ) )" % (min(ANIOS), max(ANIOS))))
    w(os.path.join(d, "relationships.tmdl"), "relationship " + guid("rel") + "\n" + T + "fromColumn: " + qn(TB) + ".Fecha\n" + T + "toColumn: Calendario.Date\n")


# ── visuales ───────────────────────────────────────────────────────────
def C(p):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": TB}}, "Property": p}}, "queryRef": TB + "." + p, "nativeQueryRef": p}


def Me(p):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": TB}}, "Property": p}}, "queryRef": TB + "." + p, "nativeQueryRef": p}


def vis(tipo, roles):
    return {"visualType": tipo, "query": {"queryState": {r: {"projections": ps} for r, ps in roles.items()}}, "drillFilterOtherVisuals": True}


def texto(parrafos, fondo=None):
    """parrafos = [[(texto, tamaño pt, negrita, color, fuente), ...], ...]  (cada párrafo, una lista de tramos)"""
    ps = [{"textRuns": [{"value": t, "textStyle": {"fontFamily": f or "Segoe UI", "fontSize": "%dpt" % tam, **({"fontWeight": "bold"} if b else {}), "color": col}}
                        for t, tam, b, col, f in par]} for par in parrafos]
    v = {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": ps}}]}, "drillFilterOtherVisuals": True}
    v["visualContainerObjects"] = {"background": [{"properties": {"show": lit("true"), "color": color(fondo), "transparency": lit("0D")}}] if fondo
                                   else [{"properties": {"show": lit("false")}}]}   # sin fondo: no tapa el gráfico
    return v


def linea(medida, col, rejilla, etiquetas, ymax=None, grosor="3D"):
    v = vis("lineChart", {"Category": [C(X)], "Y": [Me(medida)]})
    va = {"start": lit("0D"), "showAxisTitle": lit("false"), "gridlineShow": lit("true" if rejilla else "false")}
    if ymax:
        va["end"] = lit("%dD" % ymax)
    v["objects"] = {"dataPoint": [{"properties": {"fill": color(col)}, "selector": {"metadata": TB + "." + medida}}], "lineStyles": [{"properties": {"strokeWidth": lit(grosor), "showMarker": lit("true")}}],
                    "valueAxis": [{"properties": va}], "categoryAxis": [{"properties": {"axisType": lit("'Categorical'"), "showAxisTitle": lit("false")}}],
                    "labels": [{"properties": {"show": lit("true" if etiquetas else "false"), "color": color("#334155")}}],
                    "legend": [{"properties": {"show": lit("false")}}]}
    return v


def tarjeta(medida, col, tam="40D"):
    v = vis("card", {"Values": [Me(medida)]})
    v["objects"] = {"labels": [{"properties": {"fontSize": lit(tam), "color": color(col)}}], "categoryLabels": [{"properties": {"show": lit("false")}}]}
    return v


def pagina_antes():
    NAR, FONDO, TXT, OXIDO = "#D9A030", "#FDF3E6", "#1F2937", "#A33A12"
    return FONDO, [
        (0, 0, 1280, 58, texto([[("APLICANDO", 18, True, TXT, "Georgia"), ("      ANTES / DESPUÉS · NARRACIÓN CON DATOS", 11, False, TXT, "Georgia")]], fondo="#FFBE5C"), None, None),
        (36, 66, 900, 58, texto([[("Evolución de la producción", 30, True, TXT, "Georgia")]]), None, None),
        (36, 126, 1210, 410, linea(Y + " totales", NAR, True, True, None, "2D"), None, None),
        (36, 548, 1210, 82, texto([[("▮▮▮   ", 20, True, OXIDO, None), ("Crecimiento sostenido:   ", 18, False, TXT, "Georgia"), ("+46 unidades", 20, True, OXIDO, "Georgia")]], fondo="#FAE3CD"), None, None),
        (36, 640, 600, 32, texto([[("Producción en unidades.", 9, False, "#475569", None)]]), None, None),
    ]


def pagina_despues(prop):
    A, TXT, GRIS = prop.get("color_acento", "#0F5B78"), "#1F2937", "#475569"
    ymax = -(-int(max(U.values()) * 1.1) // 50) * 50
    alt = prop.get("alt", {})
    tj = prop.get("tarjeta", {"medida": "Aumento acumulado", "etiqueta": "unidades más"})
    el = [
        (40, 18, 1200, 52, texto([[(prop["titulo"], 22, True, TXT, None)]]), None, None),
        (40, 70, 1200, 30, texto([[(prop.get("subtitulo", ""), 12, False, GRIS, None)]]), None, None),
        (40, 120, 290, 110, tarjeta(tj["medida"], A), None, alt.get("tarjeta")),
        (40, 228, 290, 70, texto([[(tj.get("etiqueta", ""), 12, False, GRIS, None)]]), None, None),
    ]
    gx, gy, gw, gh = 350, 110, 900, 510
    el.append((gx, gy, gw, gh, linea(Y + " totales", A, False, True, ymax), None, alt.get("linea")))
    # anotaciones: posición aproximada sobre el punto del año (recolócalas si mueves el gráfico)
    x0, x1, y0, y1 = gx + 52, gx + gw - 26, gy + 18, gy + gh - 42
    for an in prop.get("anotaciones", []):
        i = ANIOS.index(int(an["anio"])) if int(an["anio"]) in ANIOS else 0
        px = x0 + i * (x1 - x0) / (len(ANIOS) - 1)
        py = y1 - U[ANIOS[i]] / ymax * (y1 - y0)
        el.append((int(px - 200), int(py - 96), 190, 46, texto([[(an["texto"], 10, True, A, None)]]), None, None))
    el.append((40, 640, 1200, 60, texto([[(prop.get("pie", ""), 9, False, GRIS, None)]]), None, None))
    return "#FFFFFF", el


def pagina_ritmo(prop):
    A = prop.get("color_acento", "#0F5B78")
    col = vis("clusteredColumnChart", {"Category": [C(X)], "Y": [Me("Aumento anual")]})
    col["objects"] = {"dataPoint": [{"properties": {"fill": color("#8A96A3")}}], "labels": [{"properties": {"show": lit("true")}}],
                      "valueAxis": [{"properties": {"start": lit("0D"), "showAxisTitle": lit("false"), "gridlineShow": lit("false")}}],
                      "categoryAxis": [{"properties": {"axisType": lit("'Categorical'"), "showAxisTitle": lit("false")}}]}
    r = prop.get("pagina_ritmo", {})
    return "#FFFFFF", [
        (40, 18, 1200, 52, texto([[(r.get("titulo", "Aumento anual de la producción"), 22, True, "#1F2937", None)]]), None, None),
        (40, 70, 1200, 30, texto([[(r.get("subtitulo", "Aumento frente al año anterior"), 12, False, "#475569", None)]]), None, None),
        (40, 110, 1200, 520, col, None, r.get("alt")),
        (40, 640, 1200, 60, texto([[(prop.get("pie", ""), 9, False, "#475569", None)]]), None, None),
    ]


def pagina_anexo(prop):
    tb = vis("tableEx", {"Values": [C(X), Me(Y + " totales"), Me("Aumento anual")]})
    return "#FFFFFF", [
        (40, 18, 1200, 52, texto([[("Anexo: producción por año", 22, True, "#1F2937", None)]]), None, None),
        (40, 90, 520, 420, tb, None, "Tabla de producción anual con el total y el aumento frente al año anterior."),
        (40, 640, 1200, 60, texto([[(prop.get("pie", ""), 9, False, "#475569", None)]]), None, None),
    ]


def informe(proy, nombre, paginas):
    base = os.path.join(proy, nombre + ".Report")
    wj(os.path.join(base, "definition.pbir"), {"$schema": R.replace("definition/", "") + "definitionProperties/2.0.0/schema.json",
                                               "version": "4.0", "datasetReference": {"byPath": {"path": "../" + nombre + ".SemanticModel"}}})
    wj(os.path.join(base, ".platform"), {"$schema": SCH + "gitIntegration/platformProperties/2.0.0/schema.json",
                                         "metadata": {"type": "Report", "displayName": nombre},
                                         "config": {"version": "2.0", "logicalId": guid(nombre + "/informe")}})
    d = os.path.join(base, "definition")
    wj(os.path.join(d, "version.json"), {"$schema": R + "versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    wj(os.path.join(d, "report.json"), {"$schema": R + "report/1.0.0/schema.json",
                                        "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.59", "type": "SharedResources"}},
                                        "layoutOptimization": "None",
                                        "resourcePackages": [{"name": "SharedResources", "type": "SharedResources", "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]}],
                                        "settings": {"useStylableVisualContainerHeader": True}})
    wj(os.path.join(d, "pages", "pages.json"), {"$schema": R + "pagesMetadata/1.0.0/schema.json", "pageOrder": [p[0] for p in paginas], "activePageName": paginas[0][0]})
    for pid, titulo, (fondo, elementos) in paginas:
        wj(os.path.join(d, "pages", pid, "page.json"), {"$schema": R + "page/1.0.0/schema.json", "name": pid, "displayName": titulo, "displayOption": "FitToPage",
                                                        "height": 720, "width": 1280,
                                                        "objects": {"background": [{"properties": {"color": color(fondo), "transparency": lit("0D")}}]}})
        for z, (x, y, an, al, v, tit, alt) in enumerate(elementos):
            vc = v.setdefault("visualContainerObjects", {})
            if v["visualType"] != "textbox":
                vc["title"] = [{"properties": {"show": lit("true" if tit else "false"), **({"text": s(tit)} if tit else {})}}]
            if alt:
                vc["general"] = [{"properties": {"altText": s(alt)}}]
            vid = pid[:3] + "%02d" % z + guid(nombre + pid + "%d" % z).replace("-", "")[:14]
            wj(os.path.join(d, "pages", pid, "visuals", vid, "visual.json"),
               {"$schema": R + "visualContainer/1.0.0/schema.json", "name": vid, "position": {"x": x, "y": y, "z": z, "height": al, "width": an}, "visual": v})


def crear(proy, nombre, paginas, extra_medidas):
    os.makedirs(proy, exist_ok=True)
    for e in os.listdir(proy):   # se vacía el contenido; borrar la carpeta falla si Power BI la tiene abierta
        r = os.path.join(proy, e)
        shutil.rmtree(r) if os.path.isdir(r) else os.remove(r)
    modelo(proy, nombre, extra_medidas)
    informe(proy, nombre, paginas)
    wj(os.path.join(proy, nombre + ".pbip"), {"version": "1.0", "artifacts": [{"report": {"path": nombre + ".Report"}}], "settings": {"enableAutoRecovery": True}})
    print("Proyecto de Power BI:", os.path.join(proy, nombre + ".pbip"))


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "antes":
        crear(os.path.join(ENTRADA, "powerbi"), "Produccion_antes", [("antes", "Evolución de la producción", pagina_antes())], [])
        return 0
    if modo != "despues" or len(sys.argv) < 3:
        print(__doc__); return 1
    prop = json.load(open(sys.argv[2], encoding="utf-8"))
    if not prop.get("titulo"):
        print("Falta «titulo» en la propuesta."); return 2
    if not comprobar(prop):
        print("NO SE CREA EL PROYECTO: corrige las cifras de la propuesta."); return 2
    base = {m[0] for m in MEDIDAS}
    extra = []
    for m in prop.get("medidas", []):
        if m.get("nombre") in base:
            continue                       # se usa la versión comprobada de la herramienta
        tablas = {t.strip("'") for t in re.findall(r"(?<![\w\]])('[^']+'|[A-Za-z_]\w*)\[", m.get("dax", ""))}
        if tablas - {TB, "Calendario"}:
            print("Medida omitida (usa una tabla que no existe en el modelo):", m.get("nombre")); continue
        extra.append((m["nombre"], m["dax"].replace("\n", " "), m.get("formato")))
    paginas = [("principal", prop.get("nombre_pagina", "Mensaje"), pagina_despues(prop))]
    if prop.get("pagina_ritmo"):
        paginas.append(("ritmo", "Ritmo anual", pagina_ritmo(prop)))
    if prop.get("pagina_anexo", True):
        paginas.append(("anexo", "Anexo", pagina_anexo(prop)))
    crear(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "powerbi"), re.sub(r"\W+", "_", TB) + "_mejorado", paginas, extra)
    print("Medidas añadidas por el agente:", ", ".join(e[0] for e in extra) or "ninguna")
    return 0


if __name__ == "__main__":
    sys.exit(main())
