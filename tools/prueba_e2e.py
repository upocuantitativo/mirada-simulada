"""Prueba de extremo a extremo en un navegador real. Uso: python tools/prueba_e2e.py [carpeta_de_capturas]"""
import functools, http.server, json, os, sys, threading
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CAP = sys.argv[1] if len(sys.argv) > 1 else None
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8766), functools.partial(Q, directory=RAIZ))
threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:8766/'
CODIGO = os.environ['MIRADA_CODIGO']  # código de acceso de tu copia
fallos = []
def ok(c, t):
    print(('OK  ' if c else 'FALLO ') + t)
    if not c: fallos.append(t)
def lee_informe(pg):
    return pg.evaluate("""async()=>{const E=__lab;return {m:E.medidas.mensaje,o:E.medidas.orden_narrativo,d:E.medidas.decoracion_pct,n:E.obs.length}}""")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True); pg = ctx.new_page()
    errores = []; pg.on('pageerror', lambda e: errores.append(str(e))); pg.on('console', lambda m: errores.append(m.text) if m.type == 'error' else None)
    pg.goto(U + 'lab.html'); pg.wait_for_url('**/index.html?volver=*'); ok(True, 'sin sesión redirige al acceso')
    pg.fill('#nombre', 'Persona de Prueba'); pg.fill('#correo', 'prueba@upo.es'); pg.fill('#codigo', 'mal'); pg.click('button[type=submit]')
    ok('no es el del curso' in pg.inner_text('#err'), 'código erróneo rechazado')
    pg.fill('#codigo', CODIGO); pg.click('button[type=submit]'); pg.wait_for_url('**/lab.html'); ok(True, 'entra y vuelve a la página pedida')
    pg.goto(U + 'lab.html?escenario=E1'); pg.wait_for_function("window.__lab && __lab.mapa")
    pg.click('#simular'); pg.wait_for_function("window.__lab.obs && !document.getElementById('res').hidden", timeout=60000)
    a = lee_informe(pg); ok(a['n'] == 30, '30 personas simuladas'); print('E1', json.dumps(a))
    with pg.expect_download() as d: pg.click('#json')
    inf = json.load(open(d.value.path(), encoding='utf-8')); ok(inf['semilla'] == 2026 and inf['autor'] == 'Persona de Prueba', 'informe JSON con autor y semilla')
    print('E1 audiencias', {k: (round(v['mensaje']['vieron'], 3), v['mensaje']['ttff_ms']) for k, v in inf['por_audiencia'].items()})
    print('E1 top', [(z['id'], z['tiempo_pct']) for z in sorted(inf['global']['zonas'], key=lambda z: -z['tiempo_pct'])[:5]])
    pg.click('#simular'); pg.wait_for_timeout(1500); ok(lee_informe(pg)['m'] == a['m'], 'misma semilla, mismo resultado')
    if CAP:
        pg.screenshot(path=os.path.join(CAP, 'lab_calor.png'), full_page=False)
        pg.click('[data-v=recorrido]'); pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(CAP, 'lab_rec.png'))
    pg.select_option('#instrumento', 'campo'); pg.click('#simular'); pg.wait_for_timeout(1500); c = lee_informe(pg); ok(c['m'] != a['m'], 'el instrumento cambia las métricas'); print('E1 campo', c['m']['vieron'])
    pg.select_option('#instrumento', ''); pg.select_option('#caso', 'grafico_antes'); pg.wait_for_timeout(600)
    pg.fill('#n_direccion', '10'); pg.fill('#n_comercial', '5'); pg.fill('#n_finanzas', '8'); pg.fill('#n_analista', '2'); pg.fill('#n_operaciones', '5')
    pg.click('#simular'); pg.wait_for_timeout(2000)
    with pg.expect_download() as d: pg.click('#json')
    ej = json.load(open(d.value.path(), encoding='utf-8')); ej['autor'] = 'Docente (ejemplo)'; ej['correo'] = ''
    json.dump(ej, open(os.path.join(RAIZ, 'ejemplo', 'entrada', 'informe_mirada.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # subida propia y dibujo de zona
    pg.set_input_files('#fichero', os.path.join(RAIZ, 'casos', 'web_antes.png')); pg.wait_for_timeout(600)
    bx = pg.locator('#base').bounding_box(); pg.mouse.move(bx['x'] + 40, bx['y'] + 40); pg.mouse.down(); pg.mouse.move(bx['x'] + 300, bx['y'] + 140, steps=4); pg.mouse.up()
    ok(pg.evaluate('__lab.aois.length') == 1, 'se dibuja una zona sobre captura propia')
    for n in ['teoria', 'equipo', 'ejercicios', 'montar', 'centro']:
        if os.path.exists(os.path.join(RAIZ, n + '.html')):
            pg.goto(U + n + '.html'); pg.wait_for_timeout(2500 if n == 'teoria' else 500)
            if CAP: pg.screenshot(path=os.path.join(CAP, n + '.png'), full_page=True)
    mv = b.new_context(viewport={'width': 390, 'height': 844}); m = mv.new_page(); m.goto(U + 'index.html'); m.wait_for_timeout(500)
    desb = m.evaluate('document.documentElement.scrollWidth>innerWidth'); ok(not desb, 'acceso sin desborde en móvil')
    if CAP: m.screenshot(path=os.path.join(CAP, 'm_acceso.png'))
    m.fill('#nombre', 'Persona Prueba'); m.fill('#correo', 'a@b.es'); m.fill('#codigo', CODIGO); m.click('button[type=submit]'); m.wait_for_url('**/centro.html')
    for n in ['lab', 'teoria', 'equipo', 'ejercicios', 'montar']:
        if os.path.exists(os.path.join(RAIZ, n + '.html')):
            m.goto(U + n + '.html'); m.wait_for_timeout(800)
            ok(not m.evaluate('document.documentElement.scrollWidth>innerWidth+1'), n + ' sin desborde en móvil')
    if CAP: m.goto(U + 'lab.html'); m.wait_for_timeout(800); m.screenshot(path=os.path.join(CAP, 'm_lab.png'))
    ok(not errores, 'sin errores de consola ' + str(errores[:3]))
    b.close()
print('RESULTADO:', 'todo correcto' if not fallos else fallos); sys.exit(1 if fallos else 0)
