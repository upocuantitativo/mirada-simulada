"""Genera los estímulos del laboratorio: casos/*.png y data/casos.json (zonas de interés, AOI).

Cada elemento del HTML con data-aoi se convierte en una zona medida en el propio navegador.
Las cifras de Road Bikes son las del escenario docente de Adventure Works del curso: no son datos nativos
de la base de ejemplo. La serie de producción es la del ejemplo de la diapositiva 8.
Los errores de cada versión «antes» están puestos a propósito para el ejercicio.

Uso:  pip install playwright && python tools/gen_casos.py
"""
import json, os
from playwright.sync_api import sync_playwright

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FILAS = [('C', 372, 311), ('F', 286, 232), ('H', 318, 267), ('I', 290, 235),
         ('A', 452, 426), ('B', 398, 372), ('D', 441, 417), ('E', 376, 350), ('G', 400, 376)]
CRIT = 'CFHI'
PROD = [(2017, 35), (2018, 50), (2019, 75), (2020, 85), (2021, 120), (2022, 140), (2023, 160), (2024, 190), (2025, 210)]


def aoi(id_, tipo, nombre, msg=False, orden=0, para=''):
    a = f'data-aoi="{id_}" data-tipo="{tipo}" data-nombre="{nombre}"'
    if msg: a += ' data-msg="1"'
    if orden: a += f' data-ord="{orden}"'
    if para: a += f' data-para="{para}"'
    return a


BASE = """<!doctype html><meta charset=utf-8><style>
*{box-sizing:border-box}html,body{margin:0}body{font-family:'Segoe UI',Arial,sans-serif;color:#23262f;background:#fff}
h1,h2,h3,p{margin:0}.t{font-variant-numeric:tabular-nums}
</style>"""


def linea(w, h, datos, color, resalta=False, gris=False, etiquetas=True, rejilla=True):
    x0, y0, x1, y1 = 56, 16, w - 28, h - 34
    mx = 250
    X = lambda i: x0 + (x1 - x0) * i / (len(datos) - 1)
    Y = lambda v: y1 - (y1 - y0) * v / mx
    s = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI,Arial" font-size="13">'
    for v in range(0, 251, 50):
        if rejilla: s += f'<line x1="{x0}" x2="{x1}" y1="{Y(v)}" y2="{Y(v)}" stroke="#e8dcc8"/>'
        s += f'<text x="{x0 - 8}" y="{Y(v) + 4}" text-anchor="end" fill="#555">{v}</text>'
    pts = ' '.join(f'{X(i)},{Y(v)}' for i, (_, v) in enumerate(datos))
    s += f'<polyline points="{pts}" fill="none" stroke="{"#b9bdc7" if gris else color}" stroke-width="3"/>'
    for i, (a, v) in enumerate(datos):
        ult = i == len(datos) - 1
        c = color if (ult or i == 0 or not gris) else '#b9bdc7'
        s += f'<circle cx="{X(i)}" cy="{Y(v)}" r="{7 if (ult and resalta) else 4.5}" fill="{c}"/>'
        s += f'<text x="{X(i)}" y="{y1 + 20}" text-anchor="middle" fill="#555">{a}</text>'
        if etiquetas or ult or i == 0:
            s += f'<text x="{X(i)}" y="{Y(v) - 12}" text-anchor="middle" fill="{c if gris else "#8a6a22"}" font-weight="{700 if (ult and resalta) else 400}" font-size="{17 if (ult and resalta) else 13}">{v}</text>'
    return s + '</svg>'


def grafico_antes():
    return BASE + f"""<style>body{{background:#fdf3e4;width:1280px;height:800px;padding:0 0 24px}}
.band{{background:linear-gradient(90deg,#ffb347,#ffc26b);height:74px;display:flex;align-items:center;padding:0 40px;gap:26px}}
.tag{{background:#e8891c;border-radius:12px;padding:9px 22px;font:700 24px Georgia,serif}}.band span{{font:15px Georgia,serif;letter-spacing:.04em}}
h1{{font:700 42px Georgia,serif;margin:22px 46px 8px;display:inline-block}}
.g{{margin:0 40px;width:1200px}}.kpi{{margin:16px 46px;background:#f9e3cb;border-radius:10px;padding:22px 30px;font:27px Georgia,serif;display:flex;gap:18px;align-items:center}}
.kpi b{{color:#a03a10}}.deco{{width:62px;height:50px;display:flex;align-items:flex-end;gap:5px}}.deco i{{display:block;width:14px;background:#a03a10}}
.leg{{margin:6px 46px;font-size:13px;color:#555}}</style>
<div class=band {aoi('marca','decoracion','Banda «Aplicando»')}><div class=tag>APLICANDO</div><span>ANTES / DESPUÉS · NARRACIÓN CON DATOS</span></div>
<h1 {aoi('titulo','titulo','Título: Evolución de la producción',orden=1,para='direccion,operaciones')}>Evolución de la producción</h1>
<div class=g {aoi('serie','grafico','Serie anual 2017-2025',orden=2,para='comercial,analista')}>{linea(1200,430,PROD,'#d7a12c')}</div>
<div class=kpi {aoi('kpi','kpi','Mensaje: Crecimiento sostenido +46',msg=True,orden=3,para='direccion,finanzas')}><div class=deco><i style=height:20px></i><i style=height:34px></i><i style=height:48px></i></div>Crecimiento sostenido: <b>+46 unidades</b></div>
<div class=leg {aoi('pie','texto','Nota: unidades',para='analista')}>Producción en unidades.</div>"""


def grafico_despues():
    return BASE + f"""<style>body{{width:1280px;height:800px;padding:34px 48px}}
h1{{font:600 38px 'Segoe UI',Arial;line-height:1.16;max-width:1180px;margin-bottom:8px}}h1 b{{color:#b3261e;font-weight:700}}
.sub{{font-size:18px;color:#555;margin-bottom:10px}}.g{{position:relative;width:1184px}}
.an{{position:absolute;right:120px;top:12px;width:260px;font-size:17px;line-height:1.3;color:#b3261e}}
.fu{{position:absolute;left:48px;bottom:24px;font-size:13px;color:#555}}</style>
<h1 {aoi('titulo','titulo','Título con el mensaje: +175 unidades',msg=True,orden=1,para='direccion,finanzas,operaciones')}>La producción se multiplica por seis: <b>+175 unidades</b> desde 2017</h1>
<p class=sub {aoi('sub','texto','Subtítulo: de 35 a 210',orden=2,para='analista')}>De 35 unidades en 2017 a 210 en 2025, con subida todos los años.</p>
<div class=g {aoi('serie','grafico','Serie anual 2017-2025',orden=3,para='comercial,analista')}>{linea(1184,540,PROD,'#b3261e',resalta=True,gris=True,etiquetas=False,rejilla=False)}
<div class=an {aoi('nota','anotacion','Anotación: 2025',para='direccion,comercial')}>2025: 210 unidades,<br>máximo de la serie</div></div>
<p class=fu {aoi('fuente','texto','Fuente y unidad',para='analista')}>Unidades producidas por año. Ejemplo didáctico de la microcredencial.</p>"""


def tarjeta(id_, tit, val, sub, color, nombre, tipo='kpi', msg=False, ord_=0, para=''):
    return f"""<div class=c style="background:{color}" {aoi(id_,tipo,nombre,msg,ord_,para)}><span>{tit}</span><b class=t>{val}</b><i>{sub}</i></div>"""


def barras(w, h, filas, multi=True):
    colores = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c']
    x0, y1 = 40, h - 26
    bw = (w - x0 - 10) / len(filas)
    s = f'<svg width="{w}" height="{h}" font-family="Segoe UI,Arial" font-size="12">'
    for i, (d, a, b) in enumerate(filas):
        hh = (h - 50) * b / 460
        s += f'<rect x="{x0 + i * bw + 5}" y="{y1 - hh}" width="{bw - 10}" height="{hh}" fill="{colores[i]}"/>'
        s += f'<text x="{x0 + i * bw + bw / 2}" y="{y1 + 16}" text-anchor="middle" fill="#333">{d}</text>'
    return s + '</svg>'


def panel_antes():
    fil = ''.join(f'<tr><td>{d}</td><td class=t>{a}</td><td class=t>{b}</td><td class=t>{f'{(b - a) / a * 100:+.1f}'.replace('.', ',').replace('-', '−')} %</td></tr>' for d, a, b in FILAS)
    pie = ''.join(f'<i style="background:{c}"></i>{t} ' for c, t in [('#e6194b', 'Road'), ('#3cb44b', 'Mountain'), ('#4363d8', 'Touring'), ('#f58231', 'Accesorios')])
    return BASE + f"""<style>body{{width:1280px;height:800px;background:#20304f;padding:14px;color:#fff}}
.h{{display:flex;align-items:center;gap:14px;margin-bottom:10px}}.logo{{background:linear-gradient(135deg,#f58231,#e6194b);padding:12px 18px;font-weight:800;font-size:19px;border-radius:6px}}
h1{{font-size:24px;font-weight:600}}.fil{{margin-left:auto;display:flex;gap:6px}}.fil span{{background:#3b4f78;padding:7px 11px;font-size:12px;border-radius:4px}}
.k{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:8px}}.c{{padding:9px 12px;border-radius:6px;display:flex;flex-direction:column;min-height:88px}}
.c span{{font-size:12px;opacity:.95}}.c b{{font-size:27px}}.c i{{font-size:11px;font-style:normal}}
.m{{display:grid;grid-template-columns:1.4fr .9fr 1fr;gap:8px}}.p{{background:#fff;color:#23262f;border-radius:6px;padding:9px}}.p h3{{font-size:14px;margin-bottom:6px}}
table{{border-collapse:collapse;width:100%;font-size:12px}}td,th{{padding:15px 6px;border-bottom:1px solid #ddd;text-align:left}}
.leg{{font-size:12px}}.leg i{{display:inline-block;width:10px;height:10px;margin:0 3px 0 8px}}
.do{{width:230px;height:230px;border-radius:50%;margin:60px auto 40px;background:conic-gradient(#e6194b 0 46%,#3cb44b 0 68%,#4363d8 0 86%,#f58231 0);display:flex;align-items:center;justify-content:center}}.do b{{background:#fff;width:92px;height:92px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#222;font-size:14px}}
.n{{margin-top:8px;font-size:11px;color:#b9c6e0}}</style>
<div class=h><div class=logo {aoi('logo','decoracion','Logotipo con degradado')}>ADVENTURE WORKS</div>
<h1 {aoi('titulo','titulo','Título: Cuadro de mando de ventas',orden=1,para='direccion')}>Cuadro de mando de ventas</h1>
<div class=fil {aoi('filtros','filtro','Filtros de año, canal, región y línea',para='analista')}><span>Año ▾</span><span>Canal ▾</span><span>Región ▾</span><span>Línea ▾</span><span>Distribuidor ▾</span></div></div>
<div class=k>
{tarjeta('k1','Ventas Road Bikes','3,35 M','+0,6 % frente a 2024','#e6194b','KPI: +0,6 % con J, K y L incluidos',para='finanzas,analista')}
{tarjeta('k2','Caída Road Bikes','−17,5 %','(−0,22 M USD)','#f58231','KPI: −17,5 % atribuido a toda la línea',ord_=2,para='direccion,comercial')}
{tarjeta('k3','Pedidos','1.284','+2,1 %','#3cb44b','KPI: Pedidos')}
{tarjeta('k4','Distribuidores','12','+3 nuevos','#4363d8','KPI: Distribuidores')}
{tarjeta('k5','NPS','44','−9 puntos','#911eb4','KPI: NPS')}
{tarjeta('k6','Margen','30 %','supuesto','#0f8f8f','KPI: Margen',para='finanzas')}
</div>
<div class=m>
<div class=p {aoi('barras','grafico','Barras por distribuidor con nueve colores',orden=3,para='comercial,analista')}><h3>Ventas 2025 por distribuidor (miles USD)</h3>{barras(470,500,FILAS)}</div>
<div class=p {aoi('tarta','grafico','Anillo: ventas por línea',para='finanzas')}><h3>Ventas por línea</h3><div class=do><b>100 %</b></div><div class=leg {aoi('ley','leyenda','Leyenda del anillo',para='analista')}>{pie}</div></div>
<div class=p {aoi('tabla','tabla','Tabla por distribuidor',para='finanzas,analista')}><h3>Detalle</h3><table><tr><th>Dist.</th><th>2024</th><th>2025</th><th>Var.</th></tr>{fil}</table></div>
</div>
<div class=n {aoi('nota','accion','Nota al pie: propuesta de piloto',msg=True,orden=4,para='direccion,comercial,operaciones')}>Nota: se propone valorar un piloto en algunos distribuidores. Importes en miles de USD.</div>"""


def panel_despues():
    criticos = [f for f in FILAS if f[0] in CRIT]
    resto = [f for f in FILAS if f[0] not in CRIT]
    def fila(d, a, b, foco):
        ancho = abs(b - a) * 5.4
        return f"""<div class=b><span>{d}</span><em style="width:{ancho}px;background:{'#b3261e' if foco else '#c5c9d3'}"></em><u class=t>−{a - b} k ({f'{(b - a) / a * 100:.1f}'.replace('.', ',').replace('-', '−')} %)</u></div>"""
    filas = ''.join(fila(*f, True) for f in sorted(criticos, key=lambda r: r[2] - r[1]))
    filas += ''.join(fila(*f, False) for f in sorted(resto, key=lambda r: r[2] - r[1]))
    return BASE + f"""<style>body{{width:1280px;height:800px;padding:30px 44px;background:#fff}}
h1{{font-size:33px;font-weight:600;line-height:1.18;max-width:1130px}}h1 b{{color:#b3261e}}.s{{color:#555;margin:6px 0 16px;font-size:16px}}
.g{{display:grid;grid-template-columns:330px 1fr;gap:34px}}.c{{padding:0 0 14px;margin-bottom:12px;border-bottom:1px solid #e3e5ea;display:flex;flex-direction:column}}.c span{{font-size:15px;color:#555}}.c b{{font-size:38px;font-weight:600}}.c i{{font-style:normal;font-size:14px;color:#555}}
h3{{font-size:17px;font-weight:600;margin-bottom:10px}}.b{{display:flex;align-items:center;gap:10px;height:40px;font-size:16px}}.b span{{width:18px;font-weight:600}}.b em{{display:block;height:26px}}.b u{{text-decoration:none;color:#444}}
.an{{position:absolute;left:830px;top:440px;width:320px;color:#555;font-size:17px;line-height:1.3}}
.pet{{position:absolute;left:44px;right:44px;bottom:58px;background:#1f1f6b;color:#fff;padding:15px 22px;font-size:20px;border-radius:6px}}
.fu{{position:absolute;left:44px;bottom:22px;font-size:12.5px;color:#555}}</style>
<h1 {aoi('titulo','titulo','Título BLUF: recuperar 4 distribuidores',msg=True,orden=1,para='direccion,comercial,operaciones')}>Recuperemos Carretera en <b>cuatro distribuidores</b>, no recortemos la línea</h1>
<p class=s {aoi('sub','texto','Subtítulo: −10,4 % en comparables',orden=2,para='finanzas,analista')}>Road Bikes cae un 10,4 % en los nueve comparables; C, F, H e I concentran el 64 % de la pérdida.</p>
<div class=g><div>
{tarjeta('k1','Pérdida comparable','−347 k USD','2025 frente a 2024','#fff','KPI: −347 k USD',ord_=3,para='direccion,finanzas')}
{tarjeta('k2','Concentración','64 % en 4','−221 k USD en C, F, H, I','#fff','KPI: 64 % en cuatro',para='direccion,comercial')}
{tarjeta('k3','Coste del piloto','40 k USD','se paga si recupera más del 60 %','#fff','KPI: umbral del piloto',para='finanzas')}
</div><div {aoi('barras','grafico','Pérdida por distribuidor, cuatro en rojo',orden=4,para='comercial,analista')}><h3>Pérdida de ventas por distribuidor</h3>{filas}</div></div>
<div class=an {aoi('nota','anotacion','Anotación: el resto también cae',para='direccion,comercial')}>El resto también cae (−6,1 %): el piloto no lo resuelve</div>
<div class=pet {aoi('peticion','accion','Petición: aprobar el piloto',msg=True,orden=5,para='direccion,comercial,operaciones')}>Pedimos aprobar este mes un piloto trimestral en C, F, H e I, con responsable y KPI semanal.</div>
<p class=fu {aoi('fuente','texto','Método y exclusiones',para='analista,finanzas')}>Comparables: distribuidores con 2024 y 2025 completos; J, K y L fuera. Escenario docente sobre Adventure Works. La causa no está demostrada.</p>"""


def informe_antes():
    parr = ('Durante el ejercicio se ha analizado la evolución de la línea de bicicletas de carretera en el canal de distribuidores, '
            'atendiendo a los principales indicadores comerciales y a la información disponible en el modelo. Se han considerado las ventas, '
            'los pedidos, el comportamiento de cada cuenta y la satisfacción declarada. ')
    fil = ''.join(f'<tr><td>{d}</td><td class=t>{a}</td><td class=t>{b}</td><td class=t>{b - a}</td></tr>' for d, a, b in FILAS)
    return BASE + f"""<style>body{{width:1000px;height:1280px;padding:48px 60px;font-size:15px;line-height:1.5}}
.h{{display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #1f6f50;padding-bottom:12px;margin-bottom:18px}}.logo{{font-weight:700;color:#1f6f50;font-size:20px}}
h1{{font-size:27px;font-weight:600;margin-bottom:6px}}h2{{font-size:18px;margin:14px 0 4px;color:#1f6f50}}p{{margin-bottom:8px;text-align:justify}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0}}td,th{{border:1px solid #ccd;padding:3px 8px;text-align:right}}td:first-child,th:first-child{{text-align:left}}
.fu{{font-size:12px;color:#555}}</style>
<div class=h><div class=logo {aoi('logo','decoracion','Membrete')}>Adventure Works · Control de gestión</div><span {aoi('fecha','texto','Referencia y fecha')}>Informe 11/2025</span></div>
<h1 {aoi('titulo','titulo','Título: Informe de seguimiento',orden=1,para='direccion,finanzas')}>Informe de seguimiento de la línea Road Bikes</h1>
<h2 {aoi('h1','titulo','Epígrafe: Introducción')}>1. Introducción</h2>
<p {aoi('intro','texto','Introducción extensa',para='analista')}>{parr}{parr}</p>
<h2 {aoi('h2','titulo','Epígrafe: Análisis')}>2. Análisis</h2>
<p {aoi('ana','texto','Análisis extenso',para='analista,finanzas')}>{parr}{parr}{parr}</p>
<table {aoi('tabla','tabla','Tabla por distribuidor',orden=2,para='finanzas,analista')}><tr><th>Distribuidor</th><th>2024 (k USD)</th><th>2025 (k USD)</th><th>Dif.</th></tr>{fil}</table>
<h2 {aoi('h3','titulo','Epígrafe: Otras consideraciones')}>3. Otras consideraciones</h2>
<p {aoi('otras','texto','Otras consideraciones',para='comercial')}>{parr}</p>
<h2 {aoi('h4','titulo','Epígrafe: Conclusiones')}>4. Conclusiones</h2>
<p {aoi('concl','accion','Conclusión final: aprobar piloto, en la última línea',msg=True,orden=3,para='direccion,finanzas,comercial,operaciones')}>En consecuencia, y sin perjuicio de análisis posteriores, se estima conveniente que la dirección apruebe un piloto de 40.000 USD en C, F, H e I, que se paga si recupera más del 60 % de lo perdido.</p>
<p class=fu {aoi('fuente','texto','Fuente',para='analista')}>Escenario docente sobre Adventure Works.</p>"""


def web_antes():
    return BASE + f"""<style>body{{width:1280px;height:800px;background:#f4f5f7}}
.n{{background:#fff;height:62px;display:flex;align-items:center;padding:0 36px;gap:26px;font-size:15px;box-shadow:0 1px 3px #0002}}.lg{{font-weight:800;font-size:20px;color:#c2410c;margin-right:24px}}
.b{{height:330px;background:linear-gradient(115deg,#ea580c,#be123c 60%,#7e22ce);color:#fff;padding:54px 60px;position:relative;overflow:hidden}}.b h1{{font-size:52px;font-weight:800;line-height:1.05;max-width:680px}}.b p{{font-size:20px;margin-top:12px}}
.btn{{display:inline-block;margin-top:18px;background:#fff;color:#be123c;padding:12px 26px;border-radius:30px;font-weight:700}}
.rd{{position:absolute;right:90px;top:50px;width:230px;height:230px;border-radius:50%;border:22px solid #fff5;display:flex;align-items:center;justify-content:center;font-size:70px;font-weight:800}}
.g{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:20px 36px}}.tj{{background:#fff;border-radius:10px;padding:16px;height:150px;box-shadow:0 1px 3px #0002}}.tj h3{{font-size:17px;margin-bottom:6px}}.tj p{{font-size:14px;color:#555;line-height:1.35}}.tj b{{display:block;font-size:30px;color:#c2410c}}
.av{{padding:0 36px;font-size:12.5px;color:#666}}.pie{{position:absolute;bottom:0;left:0;right:0;background:#1f2937;color:#cbd5e1;font-size:12.5px;padding:12px 36px}}</style>
<div class=n {aoi('nav','filtro','Menú superior',para='analista')}><span class=lg>AW Partners</span><span>Inicio</span><span>Catálogo</span><span>Pedidos</span><span>Formación</span><span>Soporte</span></div>
<div class=b {aoi('hero','decoracion','Banner promocional')}><h1>Rueda más lejos este invierno</h1><p>Nueva colección para distribuidores</p><span class=btn>Ver catálogo</span><div class=rd>26"</div></div>
<div class=g>
<div class=tj {aoi('t1','kpi','Tarjeta: Formación',)}><h3>Formación</h3><p>Nuevos cursos de mecánica para tu equipo.</p></div>
<div class=tj {aoi('t2','kpi','Tarjeta: Catálogo',para='comercial')}><h3>Catálogo 2026</h3><b class=t>+120</b><p>referencias nuevas</p></div>
<div class=tj {aoi('t3','kpi','Tarjeta: Pedidos',para='operaciones')}><h3>Tus pedidos</h3><p>Consulta el estado de tus envíos.</p></div>
<div class=tj {aoi('t4','kpi','Tarjeta: Promociones',para='comercial')}><h3>Promociones</h3><b class=t>−15 %</b><p>en accesorios</p></div>
</div>
<p class=av {aoi('aviso','accion','Aviso: revisión de Road Bikes en C, F, H e I',msg=True,orden=1,para='direccion,comercial,operaciones,finanzas')}>Aviso: Road Bikes pierde 221.000 USD en C, F, H e I. Si eres uno de ellos, solicita antes del día 30 la revisión de surtido y tallas.</p>
<div class=pie {aoi('pie','texto','Pie legal',para='analista')}>Adventure Works Cycles (escenario docente). Aviso legal · Privacidad · Contacto</div>"""


CASOS = [
    ('grafico_antes', 'Gráfico: producción (antes)', 'grafico', grafico_antes, 1280, 800, 'Toda la plantilla de la empresa ve este gráfico en el informe anual.'),
    ('grafico_despues', 'Gráfico: producción (después)', 'grafico', grafico_despues, 1280, 800, 'Rediseño del gráfico anterior.'),
    ('panel_antes', 'Panel: Road Bikes (antes)', 'panel', panel_antes, 1280, 800, 'Panel que se lleva al comité para decidir qué hacer con Road Bikes.'),
    ('panel_despues', 'Panel: Road Bikes (después)', 'panel', panel_despues, 1280, 800, 'Rediseño del panel para el comité.'),
    ('informe_antes', 'Informe: seguimiento Road Bikes', 'informe', informe_antes, 1000, 1280, 'Informe de una página que debe acabar en una aprobación.'),
    ('web_antes', 'Web: portal de distribuidores', 'web', web_antes, 1280, 800, 'Portal desde el que se avisa a los distribuidores de la revisión.'),
]

JS = """() => [...document.querySelectorAll('[data-aoi]')].map(e => { const r = e.getBoundingClientRect(), d = e.dataset;
  const W = document.documentElement.clientWidth, H = window.innerHeight;
  return {id:d.aoi, tipo:d.tipo, nombre:d.nombre, mensaje:!!d.msg, orden:+(d.ord||0), para:(d.para||'').split(',').filter(Boolean),
          x:+(r.x/W).toFixed(4), y:+(r.y/H).toFixed(4), w:+(r.width/W).toFixed(4), h:+(r.height/H).toFixed(4)} })"""

if __name__ == '__main__':
    os.makedirs(os.path.join(RAIZ, 'casos'), exist_ok=True)
    salida = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for id_, nombre, clase, fn, w, h, contexto in CASOS:
            pag = nav.new_page(viewport={'width': w, 'height': h})
            pag.set_content(fn())
            pag.screenshot(path=os.path.join(RAIZ, 'casos', id_ + '.png'))
            salida.append(dict(id=id_, nombre=nombre, clase=clase, contexto=contexto, ancho=w, alto=h, imagen=f'casos/{id_}.png', aois=pag.evaluate(JS)))
            pag.close()
        nav.close()
    with open(os.path.join(RAIZ, 'data', 'casos.json'), 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=0)
    print({c['id']: len(c['aois']) for c in salida})
