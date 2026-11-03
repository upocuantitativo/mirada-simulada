"""Reúne en data/agentes.json las instrucciones de los agentes, los criterios y el ejemplo resuelto.
Así la web y Claude Code leen la misma fuente.  Uso: python tools/gen_agentes.py"""
import html, json, os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
lee = lambda *p: open(os.path.join(R, *p), encoding='utf-8').read()
ag = {k: re.sub(r'^---.*?---\s*', '', lee('.claude', 'agents', k + '.md'), flags=re.S).strip() for k in ['mirada', 'narrativa', 'auditoria', 'mejora', 'powerbi']}
BASE = 'https://github.com/upocuantitativo/mirada-simulada/blob/main/ejemplo/salida/'
FICH = [('1_mirada.md', 'Mirada'), ('2_narrativa.md', 'Narrativa'), ('3_auditoria.md', 'Auditoría'), ('decisiones.md', 'Decisiones de la persona'), ('4_mejora.md', 'Mejora'), ('5_powerbi.md', 'Power BI'), ('informe_equipo.md', 'Informe final')]
alerta = re.search(r'ALERTA: .*', lee('ejemplo', 'salida', '3_auditoria.md')).group(0).split(' Alerta bloqueante')[0].replace('`', '')
ej = ('<p>Le dimos al equipo el gráfico de producción de la diapositiva, sus datos y el informe del laboratorio. Esto es lo que escribió el agente Auditoría, sin ayuda:</p>'
      f'<div class="aviso cal">{html.escape(alerta)}</div>'
      '<p>Nadie le había dicho dónde estaba el error. La mirada no lo podía ver: el laboratorio solo dice que el recuadro se mira, no que sea cierto. '
      'Las decisiones del ejemplo las redactó el material del curso para mostrar la puerta humana, y dos hallazgos quedaron rechazados por falta de datos.</p><p>Informes reales del equipo: '
      + ', '.join(f'<a href="{BASE}{f}" target="_blank" rel="noopener">{n}</a>' for f, n in FICH) + '.</p>')
json.dump(dict(agentes=ag, criterios=lee('modulo1', 'CRITERIOS.md'), brief=lee('plantillas', 'brief.md'), ejemplo=ej), open(os.path.join(R, 'data', 'agentes.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('ok')
