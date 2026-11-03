/* Página del equipo: fichas de agentes y generador de prompts para cualquier chat. */
(async function () {
  const $ = id => document.getElementById(id);
  const D = await (await fetch('data/agentes.json')).json();
  const FICHAS = {
    mirada: ['Mirada', 'Agente de eye-tracking', 'Lee el informe de atención simulada.', ['Localiza las áreas de interés', 'Estudia fijaciones y saltos', 'Distingue simulación y medición']],
    narrativa: ['Narrativa', 'Agente de storytelling', 'Comprueba que la pieza cuenta lo que debe.', ['Define audiencia y objetivo', 'Contexto, conflicto y acción', 'Contrasta el mensaje principal']],
    auditoria: ['Auditoría', 'Agente de integridad', 'Recalcula y desconfía.', ['Comprueba cifras y etiquetas', 'Revisa escalas, sesgos y fuentes', 'Evalúa claridad y accesibilidad']],
    mejora: ['Mejora', 'Agente de diseño', 'Convierte lo aceptado en cambios.', ['Prioriza los elementos relevantes', 'Anota, simplifica y reordena', 'Recomienda pruebas A/B']],
    powerbi: ['Power BI', 'Agente de despliegue', 'Lleva lo aprobado a Power BI.', ['Power Query y modelo de datos', 'Medidas DAX y visuales', 'Publicación y seguimiento']]
  };
  const orden = Object.keys(FICHAS);
  function fichar(k) {
    const f = FICHAS[k]; $('ag-t').textContent = f[0] + ': ' + f[1].toLowerCase(); $('ag-d').textContent = f[2]; $('ag-l').innerHTML = f[3].map(x => `<li>${x}</li>`).join(''); $('ag-p').textContent = D.agentes[k];
    $('sel').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === k));
  }
  orden.forEach(k => { const b = document.createElement('button'); b.dataset.k = k; b.innerHTML = `${FICHAS[k][0]}<small>${FICHAS[k][1]}</small>`; b.onclick = () => fichar(k); $('sel').append(b); $('cual').insertAdjacentHTML('beforeend', `<option value="${k}">${FICHAS[k][0]}</option>`); });
  fichar(orden[0]);
  document.querySelectorAll('#cam button').forEach(b => b.onclick = () => { document.querySelectorAll('#cam button').forEach(x => x.setAttribute('aria-pressed', x === b)); $('chat').hidden = b.dataset.c !== 'chat'; $('code').hidden = b.dataset.c !== 'code'; });
  $('brief').value = D.brief;
  try { const i = localStorage.getItem('mirada.informe'); if (i) $('inf').value = JSON.stringify(JSON.parse(i), null, 1); } catch (e) {}
  $('ejemplo').innerHTML = D.ejemplo;

  $('copiaP').onclick = async () => {
    const k = $('cual').value, usaPrev = k === 'mejora' || k === 'powerbi';
    if (!$('inf').value.trim() && k === 'mirada') { $('msg').textContent = 'Falta el informe de la mirada. Genéralo en el laboratorio.'; return; }
    if (usaPrev && !$('prev').value.trim()) { $('msg').textContent = 'Este agente trabaja sobre tus decisiones: pégalas en «Trabajo previo».'; return; }
    const t = ['Trabaja como el agente descrito. Donde diga que leas o escribas ficheros, usa el material pegado aquí y escribe tu informe en la respuesta.', '# Instrucciones del agente', D.agentes[k], '# Criterios del Módulo 1', D.criterios, '# Brief', $('brief').value,
      k === 'mirada' ? '# Informe de la mirada\n' + $('inf').value : '', usaPrev ? '# Trabajo previo y decisiones de la persona\n' + $('prev').value : '', 'Adjunto la imagen de la pieza y, si existen, los datos de origen.'].filter(Boolean).join('\n\n');
    try { await navigator.clipboard.writeText(t); $('msg').textContent = 'Copiado. Pégalo en un chat nuevo y adjunta tu imagen.'; }
    catch (e) { $('prev').value = t; $('msg').textContent = 'El navegador no deja copiar: he dejado el prompt en «Trabajo previo» para que lo copies a mano.'; }
  };
})();
