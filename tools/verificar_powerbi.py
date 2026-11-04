"""Recalcula desde los datos las cifras de control que da el agente Power BI.

No sustituye a abrir el informe en Power BI Desktop: comprueba que las cifras que el agente pide verificar salen de los
datos y no de la IA. Los datos se leen como en tools/powerbi_pbip.py (entrada/datos.json o, si no existe, el ejemplo).

Uso:  python tools/verificar_powerbi.py salida/5_powerbi.md
      (también vale la forma antigua: python tools/verificar_powerbi.py entrada/produccion.csv salida/5_powerbi.md)
Salida 0 = todas las cifras cuadran; 2 = alguna no cuadra o falta.
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from powerbi_pbip import AUM, CALC, Y

informe = sys.argv[-1]
calc = {k: [v] for k, v in CALC.items() if k != 'Crecimiento acumulado'}
num = lambda s: float(s.replace('.', '').replace(',', '.'))
txt = open(informe, encoding='utf-8').read()
tabla = re.search(r'## Cifras de control[^\n]*\n+((?:\|[^\n]*\n?)+)', txt)
mal = 0
if not tabla:
    print('FALTA la tabla «Cifras de control» en el informe'); sys.exit(2)
vistas = set()
for fila in tabla.group(1).splitlines()[2:]:
    c = [x.strip().strip('`*') for x in fila.strip('|').split('|')]
    if len(c) < 3:
        continue
    if c[0] == 'Aumento anual':              # una cifra por cada año del estado de filtro: «2025 / 2020 / 2021»
        real = [AUM.get(int(a)) for a in re.findall(r'\b(\d{4})\b', c[1])]
    elif c[0] in calc:
        real = calc[c[0]]
    else:
        print('SIN COMPROBAR', c[0], '(medida que esta herramienta no calcula)'); continue
    vistas.add(c[0])
    try:
        esperado = [num(re.sub(r'\s*\(.*\)', '', v).strip().lstrip('+')) for v in c[2].split('/')]
    except ValueError:
        print('MAL  ', c[0], ': valor esperado ilegible «' + c[2] + '»'); mal += 1; continue
    ok = bool(real) and len(esperado) == len(real) and all(r is not None and abs(r - e) <= max(0.05, abs(r) * 0.005) for r, e in zip(real, esperado))
    mal += not ok
    print(('OK   ' if ok else 'MAL  ') + f'{c[0]}: informe {c[2]} · datos {", ".join("—" if r is None else f"{r:g}" for r in real)}')
for k in (Y + ' totales', 'Aumento acumulado'):
    if k not in vistas:
        print('FALTA', k); mal += 1
print('CIFRAS DE CONTROL CORRECTAS' if not mal else f'{mal} cifras no cuadran')
sys.exit(2 if mal else 0)
