/* Interfaz de «Comprueba tu panel»: lee el informe en el navegador y pinta la valoración de js/comprobar.js. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const estado = $('estado'), res = $('res');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ETQ = { cumple: 'Cumple', revisar: 'Revisar', falla: 'No cumple' };
  const coma = n => n == null ? '—' : String(n).replace('.', ',');
  let ultimo = null, nombreUltimo = '';

  // ── lectura ────────────────────────────────────────────────────────────
  async function desdePbix(file) {
    if (!window.JSZip) throw new Error('No se pudo cargar el lector de .pbix. Comprueba la conexión o usa la carpeta del proyecto.');
    const z = await JSZip.loadAsync(file), out = {};
    for (const n of Object.keys(z.files)) {
      if (n === 'Report/Layout') out[n] = new TextDecoder('utf-16le').decode(await z.files[n].async('uint8array')).replace(/^﻿/, '');
      else if (/^Report\/definition\/.*\.json$/.test(n)) out[n] = (await z.files[n].async('string')).replace(/^﻿/, '');
    }
    return out;
  }
  async function desdeCarpeta(files) {
    const out = {};
    for (const f of files) {
      const r = f.webkitRelativePath || f.name;
      if (/\/definition\/.*\.json$/.test(r) && !/SemanticModel/.test(r)) out[r] = (await f.text()).replace(/^﻿/, '');
    }
    return out;
  }
  async function desdeEjemplo() {
    const lista = await (await fetch('ejemplo_mercasur/informe_ficheros.json', { cache: 'no-store' })).json(), out = {};
    await Promise.all(lista.ficheros.map(async f => { out[f] = await (await fetch('ejemplo_mercasur/' + lista.base + f, { cache: 'no-store' })).text(); }));
    return out;
  }

  async function procesar(obtener, nombre) {
    estado.textContent = 'Leyendo ' + nombre + '…'; res.hidden = true;
    try {
      const fs = await obtener();
      const a = Comprobador.analizar(fs);
      if (a.error) { estado.textContent = a.error; return; }
      ultimo = a; nombreUltimo = nombre;
      estado.textContent = '';
      pintar(a, nombre);
    } catch (e) { estado.textContent = 'No se pudo leer: ' + e.message; }
  }

  // ── resultado ──────────────────────────────────────────────────────────
  function pintar(a, nombre) {
    const top = a.acciones.slice(0, 6);
    let h = `<h2>2. Valoración</h2>
      <div class="cabeza"><div class="nota">${coma(a.nota)}<small> / 10</small></div>
      <div><p class="val">${esc(a.valoracion)}</p><p class="ayuda">${esc(nombre)} · ${esc(a.formato)} · ${a.paginas.length} página(s)</p></div></div>`;
    h += `<h2>3. Qué hacer primero</h2>`;
    h += top.length ? `<ol class="acciones">${top.map(x => `<li><span class="chip ${x.estado}">${ETQ[x.estado]}</span> <b>${esc(x.criterio)}</b> (${esc(x.id)}, ${esc(x.pagina)}). ${esc(x.accion)}<span class="ev">${esc(x.evidencia)}</span></li>`).join('')}</ol>` +
         (a.acciones.length > top.length ? `<p class="ayuda">Hay ${a.acciones.length - top.length} criterio(s) más por mejorar en el detalle por página.</p>` : '')
      : '<p>No hay cambios pendientes en lo que el comprobador puede ver. Repasa la lista del punto 5.</p>';
    h += `<h2>4. Detalle por página</h2>`;
    for (const p of a.paginas) {
      h += `<details class="pag"${a.paginas.length === 1 ? ' open' : ''}><summary><span>${esc(p.nombre)}</span><span>${p.nota == null ? 'sin puntuar' : coma(p.nota) + ' / 10'}</span></summary>
        <p class="ayuda">${esc(p.valoracion)} · ${p.datos} visual(es) con datos.</p>` +
        (p.reglas.length ? `<div class="tablaw"><table><thead><tr><th>Estado</th><th>Criterio</th><th>Qué se ha visto</th><th>Qué hacer</th></tr></thead><tbody>${p.reglas.map(x =>
          `<tr><td><span class="chip ${x.estado}">${ETQ[x.estado]}</span></td><td>${esc(x.id)} ${esc(x.criterio)}</td><td>${esc(x.evidencia)}</td><td>${esc(x.accion) || '—'}</td></tr>`).join('')}</tbody></table></div>` : '') + `</details>`;
    }
    if (a.informe.length) h += `<h3>Todo el informe</h3><div class="tablaw"><table><tbody>${a.informe.map(x =>
      `<tr><td><span class="chip ${x.estado}">${ETQ[x.estado]}</span></td><td>${esc(x.id)} ${esc(x.criterio)}</td><td>${esc(x.evidencia)}</td><td>${esc(x.accion) || '—'}</td></tr>`).join('')}</tbody></table></div>`;
    h += `<h2>5. Lo que tienes que comprobar tú</h2><div class="manual">${Comprobador.MANUAL.map((m, i) =>
      `<label><input type="checkbox" id="man${i}"><span><b>${m[0] ? esc(m[0]) + ' ' : ''}${esc(m[1])}.</b> ${esc(m[2])}</span></label>`).join('')}</div>`;
    h += `<p style="margin-top:1.4em"><button class="btn sec" id="bDescargar" type="button">Descargar la valoración (.md)</button></p>`;
    res.innerHTML = h; res.hidden = false;
    $('bDescargar').onclick = descargar;
    res.querySelector('h2').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  function descargar() {
    const a = ultimo; if (!a) return;
    const s = (window.Acceso && Acceso.sesion()) || {};
    const L = [`# Valoración narrativa: ${nombreUltimo}`, '', `${s.nombre || ''}${s.correo ? ' · ' + s.correo : ''} · ${new Date().toLocaleString('es-ES')}`, '',
      `**Nota: ${coma(a.nota)} / 10.** ${a.valoracion}.`, '', '## Qué hacer primero', ''];
    a.acciones.forEach((x, i) => L.push(`${i + 1}. [${ETQ[x.estado]}] ${x.criterio} (${x.id}, ${x.pagina}). ${x.accion} _${x.evidencia}_`));
    for (const p of a.paginas) {
      L.push('', `## ${p.nombre} · ${p.nota == null ? 'sin puntuar' : coma(p.nota) + ' / 10'}`, '', '| Estado | Criterio | Qué se ha visto |', '|---|---|---|');
      p.reglas.forEach(x => L.push(`| ${ETQ[x.estado]} | ${x.id} ${x.criterio} | ${x.evidencia.replace(/\|/g, '/')} |`));
    }
    L.push('', '## Comprobación personal', '');
    Comprobador.MANUAL.forEach((m, i) => L.push(`- [${$('man' + i) && $('man' + i).checked ? 'x' : ' '}] ${m[0] ? m[0] + ' ' : ''}${m[1]}: ${m[2]}`));
    L.push('', '_Valoración automática con reglas heurísticas sobre la estructura del informe. No comprueba los datos ni sustituye la revisión de una persona._');
    const b = new Blob([L.join('\n')], { type: 'text/markdown;charset=utf-8' });
    const u = URL.createObjectURL(b), el = document.createElement('a');
    el.href = u; el.download = 'valoracion_' + nombreUltimo.replace(/[^\w.-]+/g, '_').replace(/\.pbix$/i, '') + '.md'; el.click();
    setTimeout(() => URL.revokeObjectURL(u), 1000);
  }

  // ── eventos ────────────────────────────────────────────────────────────
  $('fPbix').onchange = e => { const f = e.target.files[0]; if (f) procesar(() => desdePbix(f), f.name); e.target.value = ''; };
  $('fCarpeta').onchange = e => { const fs = [...e.target.files]; if (fs.length) procesar(() => desdeCarpeta(fs), (fs[0].webkitRelativePath || '').split('/')[0] || 'carpeta'); e.target.value = ''; };
  $('bEjemplo').onclick = () => procesar(desdeEjemplo, 'Ejemplo MercaSur (Antes y Después)');
  const z = $('soltar');
  ['dragenter', 'dragover'].forEach(t => z.addEventListener(t, e => { e.preventDefault(); z.classList.add('encima'); }));
  ['dragleave', 'drop'].forEach(t => z.addEventListener(t, e => { e.preventDefault(); z.classList.remove('encima'); }));
  z.addEventListener('drop', e => { const f = e.dataTransfer.files[0]; if (f && /\.pbix$/i.test(f.name)) procesar(() => desdePbix(f), f.name); else estado.textContent = 'Arrastra un fichero .pbix; para un proyecto .pbip usa «Elegir carpeta del proyecto».'; });
})();
