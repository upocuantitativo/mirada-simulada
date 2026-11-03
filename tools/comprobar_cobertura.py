"""Comprueba que el equipo se ha pronunciado sobre TODOS los conceptos del Módulo 1.

Lee modulo1/CRITERIOS.md y, en la carpeta de salida:
- que cada agente responsable tiene una fila «| ID | Cumple/No cumple/No aplica | evidencia |» por criterio;
- que cada «No aplica» lleva motivo y cada fila lleva evidencia;
- que todo «No cumple» aparece en decisiones.md;
- que todo hallazgo aceptado llega a 4_mejora.md.

Uso:  python tools/comprobar_cobertura.py ejemplo/salida
Salida 0 = cobertura completa; 2 = falta algo.
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FICH = {'Mirada': '1_mirada.md', 'Narrativa': '2_narrativa.md', 'Auditoría': '3_auditoria.md', 'Power BI': '5_powerbi.md'}
sal = sys.argv[1] if len(sys.argv) > 1 else 'salida'
crit = re.findall(r'^- \*\*((?:B\d\.\d+|M\d)) [^*]+\*\* \[([^\]]+)\]', open(os.path.join(R, 'modulo1', 'CRITERIOS.md'), encoding='utf-8').read(), re.M)
leer = lambda f: open(os.path.join(sal, f), encoding='utf-8').read() if os.path.exists(os.path.join(sal, f)) else ''
nombres = dict(re.findall(r'^- \*\*((?:B\d\.\d+|M\d)) ([^*]+)\*\*', open(os.path.join(R, 'modulo1', 'CRITERIOS.md'), encoding='utf-8').read(), re.M))
faltan, nocumple, cuenta, filas = [], [], {}, []
for ident, ag in crit:
    txt = leer(FICH[ag]); m = re.search(r'^\|\s*\**' + re.escape(ident) + r'\**\s*\|\s*\**(Cumple|No cumple|No aplica)\**\s*\|\s*(.*?)\s*\|\s*$', txt, re.M)
    if not m: faltan.append(f'{ident} ({ag}): sin fila de cobertura'); filas.append((ident, ag, 'FALTA', '')); continue
    if len(m.group(2)) < 8: faltan.append(f'{ident} ({ag}): sin evidencia ni motivo')
    cuenta[m.group(1)] = cuenta.get(m.group(1), 0) + 1
    filas.append((ident, ag, m.group(1), m.group(2)))
    if m.group(1) == 'No cumple': nocumple.append(ident)
dec, mej = leer('decisiones.md'), leer('4_mejora.md')
# informe único: los 43 criterios en una sola tabla, con la decisión de la persona si la hay
def decision(i):
    for l in dec.splitlines():
        if re.search(r'(?<![\w.])' + re.escape(i) + r'(?![\d])', l):
            d = re.search(r'\b(Aceptado|Rechazado)\b', l)
            if d: return d.group(1)
    return ''
if os.path.isdir(sal):
    with open(os.path.join(sal, 'cobertura.md'), 'w', encoding='utf-8') as f:
        f.write('# Cobertura del Módulo 1\n\nGenerado por `tools/comprobar_cobertura.py` a partir de los informes de los agentes.\n\n')
        f.write('| ID | Concepto | Agente | Estado | Decisión | Evidencia |\n|---|---|---|---|---|---|\n')
        for i, ag, est, ev in filas:
            f.write(f'| {i} | {nombres.get(i, "").strip()} | {ag} | {est} | {decision(i) if est == "No cumple" else ""} | {ev.replace("|", "/")} |\n')
for i in nocumple:
    if not re.search(r'(?<![\w.])' + re.escape(i) + r'(?![\d])', dec): faltan.append(f'{i}: «No cumple» que no llega a decisiones.md')
ok = 0
for fila in re.findall(r'^\|.*\|\s*\**Aceptado.*$', dec, re.M):
    ok += 1; i = fila.split('|')[1].strip()
    if mej and not re.search(r'(?<![\w.])' + re.escape(i) + r'(?![\d])', mej): faltan.append(f'{i}: aceptado que no llega a 4_mejora.md')
print(f'{len(crit)} criterios del Módulo 1. Estados: {cuenta}. Hallazgos aceptados: {ok}.')
for f in faltan: print('  FALTA', f)
print('COBERTURA COMPLETA' if not faltan else f'COBERTURA INCOMPLETA: {len(faltan)} pendientes')
sys.exit(2 if faltan else 0)
