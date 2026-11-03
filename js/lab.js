/* Laboratorio: conecta la interfaz con el motor. */
(async function () {
  const $ = id => document.getElementById(id), K = Object.keys(Motor.PERSONAS);
  const CASOS = await (await fetch('data/casos.json')).json();
  const INS = await (await fetch('data/instrumento.json')).json();
  const parametros = new URLSearchParams(location.search);
  const E = { imagen: null, mapa: null, aois: [], obs: null, medidas: null, vista: 'imagen', sel: null, indice: 0, A: null, B: null, nombre: '', anim: 0, huella: '' };
  const base = $('base'), ctx = base.getContext('2d');

  const f1 = v => v == null ? 's. d.' : (v / 1000).toFixed(1).replace('.', ',') + ' s';
  const pct = v => Math.round(v * 100) + ' %';

  // ---- preparación -----------------------------------------------------------------
  $('caso').innerHTML = CASOS.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
  $('comite').innerHTML = K.map(k => `<div class="fila"><label for="n_${k}">${Motor.PERSONAS[k].nombre}<small>${Motor.PERSONAS[k].pregunta} ${Motor.PERSONAS[k].tiempo} s</small></label><input id="n_${k}" type="number" min="0" max="60" value="6"></div>`).join('');
  $('filtro').innerHTML = '<option value="">Todo el comité</option>' + K.map(k => `<option value="${k}">${Motor.PERSONAS[k].nombre}</option>`).join('');
  INS.montajes.forEach(m => $('instrumento').insertAdjacentHTML('beforeend', `<option value="${m.clave}">${m.nombre}</option>`));
  function comite() { const c = {}; K.forEach(k => { c[k] = Math.min(60, Math.max(0, parseInt($('n_' + k).value) || 0)); }); return c; }
  function total() { const t = Object.values(comite()).reduce((a, b) => a + b, 0); $('totalp').textContent = t + ' personas simuladas. Cada una tiene su propio tiempo y sus intereses varían un poco.'; $('simular').disabled = !t || !E.imagen; return t; }
  K.forEach(k => $('n_' + k).addEventListener('input', total));

  function montaje() { return INS.montajes.find(m => m.clave === $('instrumento').value) || null; }
  $('instrumento').addEventListener('change', () => { const m = montaje(); $('insinfo').textContent = m ? `Error medio ${String(m.error_medio_deg).replace('.', ',')}° en pantalla y ${String(m.error_cabeza_deg).replace('.', ',')}° al moverse la cabeza. Supuesto didáctico calculado con PyEtSimul.` : 'Error de medida calculado con PyEtSimul.'; });

  async function fijar(src, aois, nombre, contexto) {
    E.imagen = await Pintar.cargar(src); E.mapa = Motor.saliencia(E.imagen.datos, E.imagen.w, E.imagen.h);
    E.aois = aois.map(a => ({ ...a, para: (a.para || []).slice() })); E.obs = null; E.nombre = nombre; E.sel = null; E.indice = 0;
    let h = 0; const d = E.imagen.datos; for (let i = 0; i < d.length; i += 4001) h = (Math.imul(h, 31) + d[i]) | 0;
    E.huella = (h >>> 0).toString(16);
    base.width = E.imagen.w; base.height = E.imagen.h;
    $('res').hidden = true; $('sinres').hidden = false; $('ctx').textContent = contexto || ''; total(); zonasUI(); ver(E.aois.length ? 'imagen' : 'zonas');
  }
  async function elegirCaso(id) { const c = CASOS.find(x => x.id === id); await fijar(c.imagen, c.aois, c.nombre, c.contexto); }
  $('caso').addEventListener('change', e => elegirCaso(e.target.value));
  async function subir(file) {
    if (!file || !file.type.startsWith('image/')) { aviso('Ese archivo no es una imagen.'); return; }
    const url = URL.createObjectURL(file);
    try { await fijar(url, [], file.name || 'captura', 'Marca las zonas y cuál es el mensaje antes de simular.'); } catch (e) { aviso('No he podido leer esa imagen. Prueba con PNG o JPG.'); } finally { URL.revokeObjectURL(url); }
  }
  $('fichero').addEventListener('change', e => subir(e.target.files[0]));
  window.addEventListener('paste', e => { const it = [...(e.clipboardData?.items || [])].find(i => i.type.startsWith('image/')); if (it) subir(it.getAsFile()); });
  function aviso(t) { $('msgExp').textContent = t; $('ctx').textContent = t; }

  // ---- simulación -------------------------------------------------------------------
  $('simular').addEventListener('click', async () => {
    const b = $('simular'), n = total(); if (!n) return;
    b.disabled = true; b.textContent = 'Simulando…'; $('progreso').style.transform = 'scaleX(0)';
    const semilla = parseInt($('semilla').value) || 1, puro = await Motor.simular({ mapa: E.mapa, aois: E.aois, comite: comite(), semilla, progreso: (h, t) => { $('progreso').style.transform = `scaleX(${h / t})`; } });
    const prop = E.imagen.h / E.imagen.w * (INS.pantalla_mm[0] / INS.pantalla_mm[1]) || 1;
    E.obs = Motor.instrumentar(puro, E.aois, montaje(), semilla, prop);
    E.medidas = Motor.metricas(E.obs, E.aois); E.puro = puro; E.indice = 0;
    b.disabled = false; b.textContent = 'Simular miradas'; resultados(); ver('calor');
  });

  function filtrados() { const f = $('filtro').value; return f ? E.obs.filter(o => o.persona === f) : E.obs; }
  function resultados() {
    const obs = filtrados(), m = Motor.metricas(obs, E.aois); E.vistaM = m;
    $('sinres').hidden = true; $('res').hidden = false;
    $('mVieron').textContent = pct(m.mensaje.vieron); $('mTtff').textContent = f1(m.mensaje.ttff_ms); $('mTiempo').textContent = pct(m.mensaje.tiempo_pct);
    $('mIc').textContent = `Con ${m.observadores} personas simuladas, intervalo del 95 %: ${pct(m.mensaje.ic95[0])} a ${pct(m.mensaje.ic95[1])}. Orden narrativo: ${m.orden_narrativo == null ? 'sin definir' : pct(m.orden_narrativo)}.`;
    const al = Motor.alertas(m);
    $('alertas').innerHTML = (al.length ? al : [{ nivel: 'ok', texto: 'Sin alertas. Comprueba también que el mensaje sea cierto: la mirada no lo dice.' }]).map(a => `<div class="alerta ${a.nivel}">${a.texto}</div>`).join('');
    const per = Motor.porPersona(E.obs, E.aois);
    $('tPer').innerHTML = '<tr><th>Audiencia</th><th class="n">Mensaje</th><th class="n">1.ª mirada</th></tr>' + K.filter(k => per[k]).map(k => `<tr><td>${Motor.PERSONAS[k].nombre}</td><td class="n">${pct(per[k].mensaje.vieron)}</td><td class="n">${f1(per[k].mensaje.ttff_ms)}</td></tr>`).join('');
    $('tZon').innerHTML = '<tr><th>Zona</th><th class="n">Vieron</th><th class="n">1.ª</th><th class="n">Tiempo</th></tr>' + m.zonas.slice().sort((a, b) => b.tiempo_pct - a.tiempo_pct).map(z => `<tr class="${z.mensaje ? 'm' : ''}"><td>${esc(z.nombre)}</td><td class="n">${pct(z.vieron)}</td><td class="n">${f1(z.ttff_ms)}</td><td class="n">${pct(z.tiempo_pct)}</td></tr>`).join('');
    comparar();
  }
  const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  $('filtro').addEventListener('change', () => { E.indice = 0; if (E.obs) { resultados(); dibujar(); } });

  function comparar() {
    if (!E.A && !E.B) { $('cmp').innerHTML = ''; return; }
    const L = [['Lo miran', m => pct(m.mensaje.vieron)], ['Primera mirada', m => f1(m.mensaje.ttff_ms)], ['Tiempo en el mensaje', m => pct(m.mensaje.tiempo_pct)], ['Orden narrativo', m => m.orden_narrativo == null ? 's. d.' : pct(m.orden_narrativo)], ['Decoración', m => pct(m.decoracion_pct)]];
    const c = (s, f) => s ? f(s.m) : '';
    $('cmp').innerHTML = `<table class="zonas" style="margin-top:8px"><tr><th></th><th class="n">A</th><th class="n">B</th></tr>` + L.map(l => `<tr><td>${l[0]}</td><td class="n">${c(E.A, l[1])}</td><td class="n">${c(E.B, l[1])}</td></tr>`).join('') + `</table><p class="ayuda" style="margin-top:6px">A: ${esc(E.A?.n || 'sin guardar')}. B: ${esc(E.B?.n || 'sin guardar')}. Usa la misma semilla y el mismo comité en las dos.</p>`;
  }
  $('guardaA').onclick = () => { E.A = { m: E.medidas, n: E.nombre, informe: informe() }; comparar(); };
  $('guardaB').onclick = () => { E.B = { m: E.medidas, n: E.nombre, informe: informe() }; comparar(); };

  // ---- vistas -----------------------------------------------------------------------
  function ver(v) { E.vista = v; document.querySelectorAll('.vistas button').forEach(b => b.setAttribute('aria-pressed', b.dataset.v === v)); $('lienzo').classList.toggle('dibuja', v === 'zonas'); $('leyenda').style.visibility = v === 'calor' || v === 'saliencia' ? 'visible' : 'hidden'; $('accRec').hidden = v !== 'recorrido'; cancelAnimationFrame(E.anim); dibujar(); }
  document.querySelectorAll('.vistas button').forEach(b => b.onclick = () => ver(b.dataset.v));

  function observados() { return E.obs ? filtrados() : []; }
  function dibujar(hasta) {
    if (!E.imagen) return;
    const w = base.width, h = base.height; ctx.clearRect(0, 0, w, h); ctx.drawImage(E.imagen.lienzo, 0, 0, w, h);
    if (E.vista === 'calor' && E.obs) {
      const W = 240, H = Math.round(W * h / w);
      ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(0, 0, w, h);
      Pintar.calor(ctx, Motor.mapaAtencion(observados(), W, H), W, H, w, h);
    } else if (E.vista === 'saliencia') {
      ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.fillRect(0, 0, w, h);
      Pintar.calor(ctx, E.mapa.mapa, E.mapa.W, E.mapa.H, w, h, 1);
    } else if (E.vista === 'recorrido' && E.obs) {
      const o = observados(), i = Math.min(E.indice, o.length - 1);
      if (o[i]) { const fx = o[i].fijaciones, lim = Math.min(fx.length, 40); Pintar.recorrido(ctx, fx.slice(0, lim), w, h, hasta); $('obsinfo').textContent = `${Motor.PERSONAS[o[i].persona].nombre}, persona ${i + 1} de ${o.length}. Primeras ${lim} de ${fx.length} fijaciones.`; }
    } else if (E.vista === 'zonas' || (E.vista === 'imagen' && !E.obs)) {
      Pintar.zonas(ctx, E.aois, w, h, E.sel);
      if (E.nuevo) { ctx.strokeStyle = '#c2290f'; ctx.lineWidth = 2; ctx.strokeRect(E.nuevo.x * w, E.nuevo.y * h, E.nuevo.w * w, E.nuevo.h * h); }
    }
  }
  $('anterior').onclick = () => { E.indice = Math.max(0, E.indice - 1); dibujar(); };
  $('siguiente').onclick = () => { E.indice = Math.min(observados().length - 1, E.indice + 1); dibujar(); };
  $('reproducir').onclick = () => {
    cancelAnimationFrame(E.anim);
    const o = observados()[E.indice]; if (!o) return;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { dibujar(); return; }
    const lim = Math.min(o.fijaciones.length, 40), t0 = performance.now();
    (function paso(t) { const n = Math.min(lim, 1 + Math.floor((t - t0) / 220)); dibujar(n); if (n < lim) E.anim = requestAnimationFrame(paso); })(t0);
  };

  // ---- zonas ------------------------------------------------------------------------
  function punto(e) { const r = base.getBoundingClientRect(); return { x: Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), y: Math.min(1, Math.max(0, (e.clientY - r.top) / r.height)) }; }
  $('lienzo').addEventListener('pointerdown', e => { if (E.vista !== 'zonas' || !E.imagen) return; E.ini = punto(e); $('lienzo').setPointerCapture(e.pointerId); });
  $('lienzo').addEventListener('pointermove', e => { if (!E.ini) return; const p = punto(e); E.nuevo = { x: Math.min(p.x, E.ini.x), y: Math.min(p.y, E.ini.y), w: Math.abs(p.x - E.ini.x), h: Math.abs(p.y - E.ini.y) }; dibujar(); });
  $('lienzo').addEventListener('pointerup', () => {
    const n = E.nuevo; E.ini = null; E.nuevo = null; if (!n) return;
    if (n.w > .015 && n.h > .012) { const id = 'z' + Date.now().toString(36); E.aois.push({ id, tipo: 'grafico', nombre: 'Zona ' + (E.aois.length + 1), mensaje: false, orden: 0, para: [], ...n }); E.sel = id; zonasUI(); }
    dibujar();
  });
  function zonasUI() {
    $('listaZ').innerHTML = E.aois.length ? '' : '<p class="ayuda">Todavía no hay zonas.</p>';
    E.aois.forEach(a => {
      const d = document.createElement('div'); d.className = 'zona';
      d.innerHTML = `<input type="text" aria-label="Nombre de la zona" value="${esc(a.nombre)}"><div class="dos"><select aria-label="Tipo">${Object.keys(Motor.TIPOS).map(t => `<option value="${t}"${t === a.tipo ? ' selected' : ''}>${Motor.TIPOS[t]}</option>`).join('')}</select><input type="number" min="0" max="20" aria-label="Orden narrativo" title="Orden narrativo" value="${a.orden || 0}"></div>
      <div class="chips"><button data-m aria-pressed="${!!a.mensaje}">Mensaje</button>${K.map(k => `<button data-k="${k}" aria-pressed="${a.para.includes(k)}">${Motor.PERSONAS[k].nombre}</button>`).join('')}<button data-b>Quitar</button></div>`;
      const [nom, tip, ord] = d.querySelectorAll('input,select');
      nom.oninput = () => { a.nombre = nom.value; dibujar(); }; tip.onchange = () => { a.tipo = tip.value; }; ord.oninput = () => { a.orden = parseInt(ord.value) || 0; dibujar(); };
      nom.onfocus = () => { E.sel = a.id; dibujar(); };
      d.querySelectorAll('.chips button').forEach(b => b.onclick = () => {
        if ('m' in b.dataset) a.mensaje = !a.mensaje;
        else if ('b' in b.dataset) { E.aois = E.aois.filter(x => x !== a); zonasUI(); dibujar(); return; }
        else { const k = b.dataset.k, i = a.para.indexOf(k); i < 0 ? a.para.push(k) : a.para.splice(i, 1); }
        b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true'); dibujar();
      });
      $('listaZ').append(d);
    });
  }

  // ---- exportar ---------------------------------------------------------------------
  function informe() {
    const s = Acceso.sesion() || {}, m = E.medidas, com = comite();
    return {
      aviso: 'Datos simulados con un modelo didáctico. No es un registro ocular de personas reales.',
      motor: 'Mirada simulada ' + Motor.VERSION, autor: s.nombre || '', correo: s.correo || '', fecha: new Date().toISOString().slice(0, 10), caso: E.nombre, huella_imagen: E.huella, semilla: parseInt($('semilla').value) || 1,
      comite: com, instrumento: montaje() ? montaje().clave : null,
      zonas_definidas: E.aois.map(a => ({ id: a.id, nombre: a.nombre, tipo: a.tipo, mensaje: !!a.mensaje, orden: a.orden || 0, para: a.para, caja: [a.x, a.y, a.w, a.h] })),
      global: redondear(m), por_audiencia: Object.fromEntries(Object.entries(Motor.porPersona(E.obs, E.aois)).map(([k, v]) => [k, redondear({ mensaje: v.mensaje, orden_narrativo: v.orden_narrativo, decoracion_pct: v.decoracion_pct, zonas: v.zonas })])),
      alertas: Motor.alertas(m).map(a => a.texto)
    };
  }
  function redondear(o) { return JSON.parse(JSON.stringify(o, (k, v) => typeof v === 'number' ? +v.toFixed(3) : v)); }
  function bajar(nombre, tipo, contenido) { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([contenido], { type: tipo })); a.download = nombre; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); }
  const slug = () => E.nombre.toLowerCase().normalize('NFD').replace(/[^a-z0-9]+/g, '_').slice(0, 40);
  $('json').onclick = () => bajar(`informe_mirada_${slug()}.json`, 'application/json', JSON.stringify(informe(), null, 1));
  $('csv').onclick = () => {
    const f = ['persona;audiencia;n;x;y;inicio_ms;duracion_ms;zona'];
    E.obs.forEach((o, i) => o.fijaciones.forEach((x, j) => f.push([i + 1, o.persona, j + 1, x.x, x.y, x.t, x.d, x.aoi || ''].join(';'))));
    bajar(`fijaciones_${slug()}.csv`, 'text/csv', '﻿' + f.join('\n'));
  };
  $('png').onclick = () => { base.toBlob(b => { const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = `${E.vista}_${slug()}.png`; a.click(); }); };
  $('copiar').onclick = async () => {
    const t = JSON.stringify(informe());
    try { localStorage.setItem('mirada.informe', t); } catch (e) {}
    try { await navigator.clipboard.writeText(t); $('msgExp').textContent = 'Copiado. Pégalo en «entrada/informe_mirada.json» o en Equipo de agentes.'; } catch (e) { $('msgExp').textContent = 'Guardado para Equipo de agentes. El navegador no deja copiar: usa «Informe JSON».'; }
  };

  // ---- arranque ---------------------------------------------------------------------
  const esc1 = parametros.get('escenario');
  const ESC = { E1: { caso: 'panel_antes', comite: { direccion: 8, comercial: 6, finanzas: 6, analista: 5, operaciones: 5 }, semilla: 2026, nota: 'Escenario de la tarea 1. No cambies el comité ni la semilla para contestar la parte A.' } };
  if (ESC[esc1]) {
    const e = ESC[esc1]; $('caso').value = e.caso; K.forEach(k => { $('n_' + k).value = e.comite[k]; }); $('semilla').value = e.semilla;
    await elegirCaso(e.caso); $('ctx').textContent = e.nota;
  } else await elegirCaso(parametros.get('caso') || CASOS[0].id);
  window.__lab = E;
})();
