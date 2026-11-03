# -*- coding: utf-8 -*-
"""Genera el panel de ejemplo «MercaSur 360 · ¿Crece el negocio?» como proyecto de Power BI (PBIP: modelo TMDL + informe PBIR).

Es lo que produce un agente (Claude Code o Codex) cuando se le pide el panel como ficheros: el servidor MCP de Power BI
crea el modelo y las medidas, pero no los visuales; los visuales se escriben en el formato PBIR.

    python tools/gen_pbip_mercasur.py

Salida: ejemplo_mercasur/MercaSur_Panel/ (ábrelo con MercaSur_Panel.pbip y pulsa Inicio > Actualizar).
Los datos van incrustados en las consultas de Power Query, así que el proyecto se abre en cualquier equipo.
Las medidas son las mismas que comprueba tools/probar_dax_mercasur.ps1 (16 cifras de control).
"""
import base64, json, os, shutil, uuid, zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "ejemplo_mercasur", "datos")
NOMBRE = "MercaSur_Panel"
PROY = os.path.join(RAIZ, "ejemplo_mercasur", NOMBRE)
T = "\t"
SCH = "https://developer.microsoft.com/json-schemas/fabric/"


def guid(s):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "mercasur-panel/" + s))


def w(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def wj(ruta, obj):
    w(ruta, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def qn(n):
    return n if n.replace("_", "").isalnum() and n.isascii() else "'" + n + "'"


# ── Modelo ──────────────────────────────────────────────────────────────
def m_csv(fichero, tipos, pasos):
    raw = open(os.path.join(DATOS, fichero), "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    b = base64.b64encode(co.compress(raw) + co.flush()).decode("ascii")
    trozos = (" &\n" + T * 4).join('"' + b[i:i + 3000] + '"' for i in range(0, len(b), 3000))
    tm = {"text": "type text", "int": "Int64.Type", "num": "type number"}
    tl = ", ".join('{"%s", %s}' % (c, tm[t]) for c, t in tipos)
    p = T * 4
    lineas = ["let",
              p + "Origen = Csv.Document(Binary.Decompress(Binary.FromText(",
              p + trozos + ",",
              p + 'BinaryEncoding.Base64), Compression.Deflate), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
              p + "Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),",
              p + "Tipos = Table.TransformColumnTypes(Encabezados, {" + tl + '}, "en-US")' + ("," if pasos else "")]
    lineas += [p + s for s in pasos]
    ultimo = pasos[-1].split("=")[0].strip() if pasos else "Tipos"
    return ("\n" + T * 3).join(lineas + ["in", p + ultimo])


DT = {"text": "string", "int": "int64", "num": "double", "date": "dateTime"}


def tabla(nombre, cols, m=None, calc=None, medidas=(), ocultas=()):
    L = ["table " + qn(nombre), T + "lineageTag: " + guid("t/" + nombre), ""]
    for nm, dax, fmt in medidas:
        L += [T + "measure " + qn(nm) + " = " + dax]
        if fmt:
            L.append(T * 2 + "formatString: " + fmt)
        L += [T * 2 + "lineageTag: " + guid("m/" + nm), ""]

    for c, t in cols:
        L += [T + "column " + qn(c), T * 2 + "dataType: " + DT[t]]
        if t == "date":
            L.append(T * 2 + "formatString: mmm yyyy")
        if c in ocultas:
            L.append(T * 2 + "isHidden")
        L += [T * 2 + "lineageTag: " + guid("c/" + nombre + "/" + c),
              T * 2 + "summarizeBy: " + ("sum" if t in ("int", "num") and c in ("unidades", "ventas_usd", "objetivo_usd") else "none"),
              T * 2 + "sourceColumn: " + ("[" + c + "]" if calc else c), ""]
    L += [T + "partition " + qn(nombre) + " = " + ("calculated" if calc else "m"), T * 2 + "mode: import", T * 2 + "source =",
          T * 3 + (calc or m), ""]
    return "\n".join(L)


# Las mismas medidas que tools/probar_dax_mercasur.ps1 y la pestaña ia_powerbi.html
MEDIDAS = [
    ("Ventas", "SUM ( Ventas[ventas_usd] )", "#,0"),
    ("Ventas ultimo anio", "CALCULATE ( [Ventas], Anios[Anio] = MAX ( Anios[Anio] ) )", "#,0"),
    ("Ventas anio anterior", "CALCULATE ( [Ventas], Anios[Anio] = MAX ( Anios[Anio] ) - 1 )", "#,0"),
    ("Crecimiento", "DIVIDE ( [Ventas ultimo anio] - [Ventas anio anterior], [Ventas anio anterior] )", "0.0%"),
    ("Ventas comparables", 'CALCULATE ( [Ventas], Tiendas[es_nueva] = "no" )', "#,0"),
    ("Crecimiento comparables", "VAR Actual = CALCULATE ( [Ventas comparables], Anios[Anio] = MAX ( Anios[Anio] ) ) VAR Previo = CALCULATE ( [Ventas comparables], Anios[Anio] = MAX ( Anios[Anio] ) - 1 ) RETURN DIVIDE ( Actual - Previo, Previo )", "0.0%"),
    ("Ventas tiendas nuevas", 'CALCULATE ( [Ventas], Tiendas[es_nueva] <> "no" )', "#,0"),
    ("Ventas tiendas nuevas ultimo anio", "CALCULATE ( [Ventas tiendas nuevas], Anios[Anio] = MAX ( Anios[Anio] ) )", "#,0"),
    ("Objetivo", "SUM ( Presupuesto[objetivo_usd] )", "#,0"),
    ("Cumplimiento", "DIVIDE ( [Ventas], [Objetivo] )", "0.0%"),
    ("Desviacion objetivo", "[Cumplimiento] - 1", "+0.0%;-0.0%;0.0%"),
    ("Margen ponderado", "DIVIDE ( SUMX ( Ventas, Ventas[ventas_usd] * Ventas[margen_pct] / 100 ), [Ventas] )", "0.0%"),
    ("Titulo panel", 'VAR T = [Crecimiento] VAR TC = [Crecimiento comparables] '
                     'VAR Total = IF ( T < 0, "caen un ", "suben un " ) & FORMAT ( ABS ( T ), "0.0 %" ) '
                     'VAR Comp = IF ( TC < 0, "caen un ", "suben un " ) & FORMAT ( ABS ( TC ), "0.0 %" ) '
                     'RETURN IF ( NOT ISBLANK ( T ), "En " & MAX ( Anios[Anio] ) & " las ventas " & Total '
                     '& IF ( SIGN ( T ) <> SIGN ( TC ), ", pero en las tiendas comparables ", " y en las tiendas comparables " ) & Comp, '
                     '"Ventas de MercaSur 360: " & FORMAT ( [Ventas], "#,##0" ) & " USD" )', None),
]


def modelo():
    base = os.path.join(PROY, NOMBRE + ".SemanticModel")
    d = os.path.join(base, "definition")
    wj(os.path.join(base, "definition.pbism"), {"version": "4.0", "settings": {}})
    wj(os.path.join(base, ".platform"), {"$schema": SCH + "gitIntegration/platformProperties/2.0.0/schema.json",
                                         "metadata": {"type": "SemanticModel", "displayName": "MercaSur Panel"},
                                         "config": {"version": "2.0", "logicalId": guid("modelo")}})
    w(os.path.join(d, "database.tmdl"), "database\n" + T + "compatibilityLevel: 1567\n")
    tablas = ["Ventas", "Tiendas", "Presupuesto", "Anios"]
    w(os.path.join(d, "model.tmdl"), "\n".join(["model Model", T + "culture: es-ES", T + "defaultPowerBIDataSourceVersion: powerBI_V3",
                                                T + "discourageImplicitMeasures", ""] + ["ref table " + t for t in tablas] + [""]))
    tv = [("fecha", "text"), ("id_tienda", "text"), ("linea", "text"), ("unidades", "int"), ("ventas_usd", "num"), ("margen_pct", "num")]
    w(os.path.join(d, "tables", "Ventas.tmdl"), tabla("Ventas", tv + [("Anio", "int"), ("Mes", "date")], m=m_csv("mercasur360_ventas.csv", tv, [
        'Columnas = Table.SelectColumns(Tipos, {"fecha", "id_tienda", "linea", "unidades", "ventas_usd", "margen_pct"}),',
        'ConAnio = Table.AddColumn(Columnas, "Anio", each Number.From(Text.Start([fecha], 4)), Int64.Type),',
        'ConMes = Table.AddColumn(ConAnio, "Mes", each #date(Number.From(Text.Start([fecha], 4)), Number.From(Text.End([fecha], 2)), 1), type date)']),
        medidas=MEDIDAS, ocultas=("fecha", "id_tienda", "Anio")))
    tt = [("id_tienda", "text"), ("tienda", "text"), ("departamento", "text"), ("es_nueva", "text")]
    w(os.path.join(d, "tables", "Tiendas.tmdl"), tabla("Tiendas", tt, m=m_csv("mercasur360_tiendas.csv", tt, [
        'Columnas = Table.SelectColumns(Tipos, {"id_tienda", "tienda", "departamento", "es_nueva"})'])))
    tp = [("id_tienda", "text"), ("linea", "text"), ("semestre", "text"), ("objetivo_usd", "num")]
    w(os.path.join(d, "tables", "Presupuesto.tmdl"), tabla("Presupuesto", tp + [("Anio", "int")], m=m_csv("mercasur360_presupuesto.csv", tp, [
        'ConAnio = Table.AddColumn(Tipos, "Anio", each Number.From(Text.Start([semestre], 4)), Int64.Type)']), ocultas=("id_tienda", "Anio")))
    w(os.path.join(d, "tables", "Anios.tmdl"), tabla("Anios", [("Anio", "int")], calc='SELECTCOLUMNS ( GENERATESERIES ( 2024, 2025, 1 ), "Anio", [Value] )'))
    rel = []
    for a, b in [("Ventas.id_tienda", "Tiendas.id_tienda"), ("Presupuesto.id_tienda", "Tiendas.id_tienda"), ("Ventas.Anio", "Anios.Anio"), ("Presupuesto.Anio", "Anios.Anio")]:
        rel.append("relationship " + guid("rel/" + a) + "\n" + T + "fromColumn: " + a + "\n" + T + "toColumn: " + b + "\n")
    w(os.path.join(d, "relationships.tmdl"), "\n".join(rel))


# ── Informe ─────────────────────────────────────────────────────────────
R = SCH + "item/report/definition/"


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def C(t, p):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": p}}, "queryRef": t + "." + p, "nativeQueryRef": p}


def Me(p):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "Ventas"}}, "Property": p}}, "queryRef": "Ventas." + p, "nativeQueryRef": p}


def vis(tipo, roles, orden=None):
    q = {"queryState": {r: {"projections": ps} for r, ps in roles.items()}}
    if orden:
        q["sortDefinition"] = {"sort": [{"field": orden["field"], "direction": "Descending"}], "isDefaultSort": False}
    return {"visualType": tipo, "query": q, "drillFilterOtherVisuals": True}


def texto(parrafos):
    ps = [{"textRuns": [{"value": t, "textStyle": {"fontFamily": "Segoe UI", "fontSize": s, **({"fontWeight": "bold"} if b else {}), "color": col}}]}
          for t, s, b, col in parrafos]
    return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": ps}}]}, "drillFilterOtherVisuals": True}


def informe():
    base = os.path.join(PROY, NOMBRE + ".Report")
    wj(os.path.join(base, "definition.pbir"), {"$schema": R.replace("definition/", "") + "definitionProperties/2.0.0/schema.json",
                                               "version": "4.0", "datasetReference": {"byPath": {"path": "../" + NOMBRE + ".SemanticModel"}}})
    wj(os.path.join(base, ".platform"), {"$schema": SCH + "gitIntegration/platformProperties/2.0.0/schema.json",
                                         "metadata": {"type": "Report", "displayName": "MercaSur Panel"},
                                         "config": {"version": "2.0", "logicalId": guid("informe")}})
    d = os.path.join(base, "definition")
    wj(os.path.join(d, "version.json"), {"$schema": R + "versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    wj(os.path.join(d, "report.json"), {"$schema": R + "report/1.0.0/schema.json",
                                        "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.59", "type": "SharedResources"}},
                                        "layoutOptimization": "None",
                                        "resourcePackages": [{"name": "SharedResources", "type": "SharedResources", "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]}],
                                        "settings": {"useStylableVisualContainerHeader": True}})
    paginas = [("antes", "1 · Antes", pagina_antes()), ("despues", "2 · Después", pagina_despues())]
    visuales = ["pages/pages.json"]
    if os.environ.get("SOLO_PAGINA"):   # solo para capturas: Power BI abre siempre la primera página
        paginas = [p for p in paginas if p[0] == os.environ["SOLO_PAGINA"]]
    wj(os.path.join(d, "pages", "pages.json"), {"$schema": R + "pagesMetadata/1.0.0/schema.json", "pageOrder": [p[0] for p in paginas], "activePageName": paginas[0][0]})
    for pid, nombre, elementos in paginas:
        visuales.append("pages/" + pid + "/page.json")
        wj(os.path.join(d, "pages", pid, "page.json"), {"$schema": R + "page/1.0.0/schema.json", "name": pid, "displayName": nombre, "displayOption": "FitToPage", "height": 720, "width": 1280})
        for z, (x, y, an, al, v, titulo, *alt) in enumerate(elementos):
            if alt:   # texto alternativo para lector de pantalla (B3.11)
                v.setdefault("visualContainerObjects", {})["general"] = [{"properties": {"altText": lit("'" + alt[0].replace("'", "''") + "'")}}]
            vid = pid[:3] + "%02d" % z + guid(pid + "%d" % z).replace("-", "")[:14]
            if titulo:
                v.setdefault("visualContainerObjects", {})["title"] = [{"properties": {"show": lit("true"), "text": lit("'" + titulo + "'")}}]
            visuales.append("pages/" + pid + "/visuals/" + vid + "/visual.json")
            wj(os.path.join(d, "pages", pid, "visuals", vid, "visual.json"),
               {"$schema": R + "visualContainer/1.0.0/schema.json", "name": vid, "position": {"x": x, "y": y, "z": z, "height": al, "width": an}, "visual": v})
    # lista de ficheros del informe: la usa la pestaña «Comprueba tu panel» para analizar el ejemplo
    wj(os.path.join(os.path.dirname(PROY), "informe_ficheros.json"), {"base": NOMBRE + "/" + NOMBRE + ".Report/definition/", "ficheros": visuales})


GRIS, GRIS_CLARO, ACENTO, TEXTO = "#8A96A3", "#C9D1D9", "#0F5B78", "#334155"


def color(c):
    return {"solid": {"color": lit("'" + c + "'")}}


def tarjeta(medida, tam="28D", unidades=None, decimales=None):
    """Tarjeta sin la etiqueta de categoría repetida y, si se pide, con la cifra completa (unidades = '1D')."""
    v = vis("card", {"Values": [Me(medida)]})
    p = {"fontSize": lit(tam), "color": color(TEXTO)}
    if unidades:
        p["labelDisplayUnits"] = lit(unidades)
    if decimales:
        p["labelPrecision"] = lit(decimales)
    v["objects"] = {"labels": [{"properties": p}], "categoryLabels": [{"properties": {"show": lit("false")}}]}
    return v


def pagina_antes():
    """El panel tal como suele salir: sin pregunta, sin mensaje, con todo lo que cabe. Incumple a propósito los criterios del Módulo 1."""
    return [
        (24, 12, 1232, 48, texto([("DASHBOARD DE VENTAS MERCASUR 2024-2025", "20pt", True, "#000000")]), None),
        (24, 66, 200, 120, vis("slicer", {"Values": [C("Tiendas", "departamento")]}), "Departamento"),
        (24, 192, 200, 120, vis("slicer", {"Values": [C("Ventas", "linea")]}), "Línea"),
        (24, 318, 200, 100, vis("slicer", {"Values": [C("Anios", "Anio")]}), "Año"),
        (236, 66, 250, 120, vis("card", {"Values": [Me("Ventas")]}), "Sum of ventas"),
        (498, 66, 250, 120, vis("card", {"Values": [Me("Crecimiento")]}), "Crecimiento"),
        (760, 66, 240, 120, vis("card", {"Values": [Me("Margen ponderado")]}), "Margen"),
        (1012, 66, 244, 240, vis("gauge", {"Y": [Me("Cumplimiento")]}), "Cumplimiento"),
        (236, 196, 380, 250, vis("pieChart", {"Category": [C("Tiendas", "tienda")], "Y": [Me("Ventas")]}), "Ventas por tienda"),
        (626, 196, 376, 250, vis("donutChart", {"Category": [C("Ventas", "linea")], "Y": [Me("Ventas")]}), "Ventas por línea"),
        (24, 456, 600, 252, vis("clusteredColumnChart", {"Category": [C("Tiendas", "tienda")], "Series": [C("Ventas", "linea")], "Y": [Me("Ventas")]}), "Ventas por tienda y línea"),
        (636, 316, 620, 392, vis("tableEx", {"Values": [C("Tiendas", "tienda"), C("Tiendas", "departamento"), C("Ventas", "linea"), Me("Ventas"), Me("Objetivo"), Me("Cumplimiento"), Me("Margen ponderado")]}), "Datos"),
    ]


def pagina_despues():
    """El mismo dato con los criterios del Módulo 1: pregunta y mensaje en el título, comparación justa, un acento, cero en el eje, fuente."""
    desv = Me("Desviacion objetivo")
    titulo = tarjeta("Titulo panel", "20D")
    titulo["objects"]["labels"][0]["properties"]["color"] = color(ACENTO)
    linea = vis("lineChart", {"Category": [C("Ventas", "Mes")], "Y": [Me("Ventas"), Me("Ventas comparables")]})
    linea["objects"] = {"dataPoint": [{"properties": {"fill": color(GRIS_CLARO)}, "selector": {"metadata": "Ventas.Ventas"}},
                                      {"properties": {"fill": color(ACENTO)}, "selector": {"metadata": "Ventas.Ventas comparables"}}],
                        "lineStyles": [{"properties": {"strokeWidth": lit("3D")}}],
                        "valueAxis": [{"properties": {"start": lit("0D"), "showAxisTitle": lit("false")}}],
                        "categoryAxis": [{"properties": {"showAxisTitle": lit("false")}}],
                        "legend": [{"properties": {"show": lit("false")}}]}
    barras = vis("clusteredBarChart", {"Category": [C("Tiendas", "tienda")], "Y": [desv]}, orden=desv)
    barras["objects"] = {"dataPoint": [{"properties": {"fill": color(GRIS)}}], "labels": [{"properties": {"show": lit("true")}}],
                         "valueAxis": [{"properties": {"showAxisTitle": lit("false")}}], "categoryAxis": [{"properties": {"showAxisTitle": lit("false")}}]}
    anio = vis("slicer", {"Values": [C("Anios", "Anio")]})
    anio["objects"] = {"data": [{"properties": {"mode": lit("'Dropdown'")}}]}
    return [
        (32, 12, 1060, 30, texto([("MercaSur 360 · ¿Crece el negocio o solo el total?", "13pt", True, TEXTO)]), None),
        (32, 44, 1060, 56, titulo, None),
        (1104, 12, 144, 88, anio, "Año"),
        (32, 112, 300, 104, tarjeta("Crecimiento"), "Crecimiento total, último año", "Crecimiento de las ventas totales en el último año: 17,7 %."),
        (348, 112, 300, 104, tarjeta("Crecimiento comparables"), "Tiendas comparables (A a I)", "Crecimiento de las nueve tiendas comparables en el último año: menos 1,1 %."),
        (664, 112, 300, 104, tarjeta("Ventas tiendas nuevas ultimo anio", "28D", "1000000D", "2L"), "Ventas de J, K y L, último año (millones de USD)", "Ventas de las tiendas nuevas J, K y L en el último año: 2,80 millones de USD."),
        (980, 112, 268, 104, tarjeta("Margen ponderado"), "Margen ponderado por ventas", "Margen ponderado por ventas: 22,4 %."),
        (32, 228, 760, 400, linea, "Ventas mensuales (USD): total en gris, tiendas comparables en azul", "Líneas de ventas mensuales de 2024 y 2025. El total se separa de las tiendas comparables desde mediados de 2024, cuando abre J; las comparables se mantienen planas."),
        (430, 262, 340, 44, texto([("Desde jul-2024 abren J, K y L: la distancia entre las dos líneas son sus ventas.", "10pt", True, ACENTO)]), None),
        (808, 228, 440, 400, barras, "Desviación frente al objetivo por tienda", "Barras de desviación frente al objetivo en 2024-2025, de más 2,4 % en la tienda H a menos 1,9 % en la tienda L."),
        (32, 636, 1216, 76, texto([("Lectura: en 2025 el total sube porque abren J, K y L; las nueve tiendas que ya existían venden un 1,1 % menos. En 2024-2025 ninguna tienda se aleja más de 2,5 puntos de su objetivo.", "11pt", True, TEXTO),
                                   ("Fuente: MercaSur 360, datos sintéticos de práctica, enero de 2024 a diciembre de 2025. «Comparables» = tiendas abiertas antes de 2024 (A a I).", "9pt", False, TEXTO)]), None),
    ]


def main():
    if os.path.isdir(PROY):   # se vacía el contenido (borrar la carpeta falla si una ventana la tiene abierta)
        for e in os.listdir(PROY):
            r = os.path.join(PROY, e)
            shutil.rmtree(r) if os.path.isdir(r) else os.remove(r)
    modelo()
    informe()
    wj(os.path.join(PROY, NOMBRE + ".pbip"), {"version": "1.0", "artifacts": [{"report": {"path": NOMBRE + ".Report"}}], "settings": {"enableAutoRecovery": True}})
    w(os.path.join(PROY, ".gitignore"), "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    print("Proyecto en", PROY)


if __name__ == "__main__":
    main()
