"""Recalcula desde el CSV las cifras de control que da el agente Power BI.

No sustituye a abrir el informe en Power BI Desktop: comprueba que las cifras
que el agente pide verificar salen de los datos y no de la IA.

Uso:  python tools/verificar_powerbi.py ejemplo/entrada/produccion.csv ejemplo/salida/5_powerbi.md
Salida 0 = todas las cifras cuadran; 2 = alguna no cuadra o falta.
"""
import csv, re, sys
sys.stdout.reconfigure(encoding='utf-8')
datos, informe = sys.argv[1], sys.argv[2]
with open(datos, encoding='utf-8-sig') as f:
    u = {int(r['Anio']): int(r['Unidades']) for r in csv.DictReader(f, delimiter=';')}
a = sorted(u); prim, ult = u[a[0]], u[a[-1]]
inc = {y: u[y] - u[y - 1] for y in a[1:] if y - 1 in u}
calc = {
    'Unidades totales': [sum(u.values())],
    'Unidades primer anio': [prim],
    'Unidades ultimo anio': [ult],
    'Aumento acumulado': [ult - prim],
    'Veces que se multiplica': [ult / prim],
    'Aumento anual': [inc.get(y) for y in (2025, 2020, 2021)],
    'Aumento anual medio': [(ult - prim) / (len(a) - 1)],
    'Anios con caida': [sum(1 for v in inc.values() if v < 0)],
}
num = lambda s: float(s.replace('.', '').replace(',', '.'))
txt = open(informe, encoding='utf-8').read()
tabla = re.search(r'## Cifras de control.*?\n((?:\|.*\n)+)', txt, re.S)
mal = 0
if not tabla: print('FALTA la tabla «Cifras de control» en el informe'); sys.exit(2)
vistas = set()
for fila in tabla.group(1).splitlines()[2:]:
    c = [x.strip() for x in fila.strip('|').split('|')]
    if len(c) < 3 or c[0] not in calc: continue
    vistas.add(c[0])
    esperado = [num(re.sub(r'\s*\(.*\)', '', v)) for v in c[2].split('/')]
    real = calc[c[0]]
    ok = len(esperado) == len(real) and all(r is not None and abs(r - e) <= max(0.05, abs(r) * 0.005) for r, e in zip(real, esperado))
    mal += not ok
    print(('OK   ' if ok else 'MAL  ') + f'{c[0]}: informe {c[2]} · datos {", ".join(f"{r:g}" for r in real)}')
for k in calc.keys() - vistas: print('FALTA', k); mal += 1
print('CIFRAS DE CONTROL CORRECTAS' if not mal else f'{mal} cifras no cuadran')
sys.exit(2 if mal else 0)
