/* Piezas interactivas de la teoría: todas usan el motor real sobre los casos del laboratorio. */
(async function () {
  const $ = id => document.getElementById(id), K = Object.keys(Motor.PERSONAS);
  const CASOS = await (await fetch('data/casos.json')).json(), INS = await (await fetch('data/instrumento.json')).json();
  const caso = id => CASOS.find(c => c.id === id), cache = {};
  async function pre(id) { if (cache[id]) return cache[id]; const c = caso(id), im = await Pintar.cargar(c.imagen); return cache[id] = { c, im, mapa: Motor.saliencia(im.datos, im.w, im.h) }; }
  function botones(cont, lista, fn) {
    const d = $(cont); lista.forEach((l, i) => { const b = document.createElement('button'); b.textContent = l[1]; b.setAttribute('aria-pressed', i === 0); b.onclick = () => { d.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); fn(l[0]); }; d.append(b); }); fn(lista[0][0]);
  }
  const W = 240, H = 150;

  // 1 · de la fijación al mapa
  const g = await pre('grafico_antes'), obsD = Motor.simularSinc({ mapa: g.mapa, aois: g.c.aois, comite: { direccion: 30 }, semilla: 11 });
  const c1 = $('c1').getContext('2d');
  const T1 = { fij: 'Una sola fijación: un punto, unos 240 ms. El círculo crece con la duración.', sac: 'Las seis primeras fijaciones de una persona, unidas por sacadas.', rec: 'El recorrido completo de esa persona en los diez segundos que le da a este gráfico.', calor: 'Treinta personas sumadas: el mapa enseña dónde se concentra el tiempo, pero pierde el orden.', aoi: 'Las zonas de interés convierten la imagen en cifras. La roja es el mensaje.' };
  botones('p1', [['fij', 'Fijación'], ['sac', 'Sacadas'], ['rec', 'Recorrido'], ['calor', 'Mapa de calor'], ['aoi', 'Zonas']], m => {
    c1.drawImage(g.im.lienzo, 0, 0, 1280, 800); const f = obsD[0].fijaciones;
    if (m === 'fij') Pintar.recorrido(c1, f.slice(0, 1), 1280, 800);
    if (m === 'sac') Pintar.recorrido(c1, f.slice(0, 6), 1280, 800);
    if (m === 'rec') Pintar.recorrido(c1, f, 1280, 800);
    if (m === 'calor') Pintar.calor(c1, Motor.mapaAtencion(obsD, W, H), W, H, 1280, 800);
    if (m === 'aoi') Pintar.zonas(c1, g.c.aois, 1280, 800);
    $('t1').textContent = T1[m];
  });

  // 2 · audiencias
  const p = await pre('panel_antes'), c2 = $('c2').getContext('2d');
  botones('p2', K.map(k => [k, Motor.PERSONAS[k].nombre]), k => {
    const com = {}; com[k] = 30; const o = Motor.simularSinc({ mapa: p.mapa, aois: p.c.aois, comite: com, semilla: 2026 }), m = Motor.metricas(o, p.c.aois);
    c2.drawImage(p.im.lienzo, 0, 0, 1280, 800); Pintar.calor(c2, Motor.mapaAtencion(o, W, H), W, H, 1280, 800);
    const top = m.zonas.slice().sort((a, b) => b.tiempo_pct - a.tiempo_pct)[0];
    $('t2').textContent = `«${Motor.PERSONAS[k].pregunta}» Se simulan ${Motor.PERSONAS[k].tiempo} s. La zona con más tiempo es: ${top.nombre} (${Math.round(top.tiempo_pct * 100)} %). Datos simulados.`;
  });

  // 3 · saliencia antes y después
  const d = await pre('panel_despues'), c3 = $('c3').getContext('2d');
  botones('p3', [['panel_antes', 'Panel antes'], ['panel_despues', 'Panel después']], id => {
    const s = id === 'panel_antes' ? p : d; c3.drawImage(s.im.lienzo, 0, 0, 1280, 800); c3.fillStyle = 'rgba(255,255,255,.3)'; c3.fillRect(0, 0, 1280, 800); Pintar.calor(c3, s.mapa.mapa, s.mapa.W, s.mapa.H, 1280, 800, 1);
  });

  // 5 · simulación frente a medición
  const c5 = $('c5').getContext('2d'), obsP = Motor.simularSinc({ mapa: p.mapa, aois: p.c.aois, comite: { direccion: 8 }, semilla: 5 });
  botones('p5', INS.montajes.map(m => [m.clave, m.clave[0].toUpperCase() + m.clave.slice(1)]), cl => {
    const m = INS.montajes.find(x => x.clave === cl), reg = Motor.instrumentar(obsP, p.c.aois, m, 5, 1.0526);
    c5.drawImage(p.im.lienzo, 0, 0, 1280, 800); c5.fillStyle = 'rgba(255,255,255,.55)'; c5.fillRect(0, 0, 1280, 800); c5.lineWidth = 2;
    let cambia = 0, n = 0;
    obsP.forEach((o, i) => o.fijaciones.forEach((f, j) => {
      const r = reg[i].fijaciones[j]; n++; if (r.aoi !== f.aoi) cambia++;
      c5.strokeStyle = '#c2290f'; c5.beginPath(); c5.moveTo(f.x * 1280, f.y * 800); c5.lineTo(r.x * 1280, r.y * 800); c5.stroke();
      c5.fillStyle = '#1f1f6b'; c5.beginPath(); c5.arc(f.x * 1280, f.y * 800, 5, 0, 7); c5.fill();
      c5.fillStyle = '#c2290f'; c5.beginPath(); c5.arc(r.x * 1280, r.y * 800, 5, 0, 7); c5.fill();
    }));
    $('t5').textContent = `${m.nombre}. Azul: dónde cae la fijación simulada. Rojo: dónde la registraría el aparato. El ${Math.round(cambia / n * 100)} % de las fijaciones acabaría en otra zona. Error calculado con PyEtSimul sobre supuestos didácticos.`;
  });

  // quiz
  const Q = [
    ['Un mapa de calor muestra sobre todo…', ['Dónde se concentra el tiempo de muchas personas', 'En qué orden se ha leído la página', 'Qué ha entendido cada persona'], 'Pierde el orden. Para el orden está el recorrido.'],
    ['Finanzas y Dirección miran zonas distintas del mismo panel. Se explica por…', ['La fuerza descendente: buscan cosas distintas', 'Un fallo del modelo', 'Los colores del panel'], 'La tarea cambia la mirada (Yarbus, 1967).'],
    ['El 100 % mira un KPI que está mal calculado. Esto significa que…', ['El error se verá mucho: la mirada no valida la cifra', 'El KPI es correcto porque se mira', 'No hay que revisarlo'], 'Atención no es verdad: por eso existe el agente de auditoría.'],
    ['Un rediseño sube del 47 % al 100 % en el laboratorio. Lo correcto es decir…', ['La simulación estima una mejora; falta contrastarla con personas', 'Las personas ya miran el mensaje', 'El panel queda validado'], 'Simulación no es medición.'],
    ['Mucho tiempo en una zona significa…', ['Puede ser interés o confusión: hay que interpretarlo', 'Siempre interés', 'Siempre confusión'], 'La métrica no dice el porqué.']
  ];
  Q.forEach(q => {
    const d = document.createElement('div'); d.className = 'pregunta'; d.innerHTML = `<b>${q[0]}</b>`;
    const ops = q[1].map((t, i) => [t, i]).sort((a, b) => a[0].length % 3 - b[0].length % 3), fb = document.createElement('p'); fb.className = 'ayuda'; fb.setAttribute('role', 'status');
    ops.forEach(o => { const b = document.createElement('button'); b.textContent = o[0]; b.onclick = () => { d.querySelectorAll('button').forEach(x => x.classList.remove('bien', 'mal')); b.classList.add(o[1] === 0 ? 'bien' : 'mal'); fb.textContent = (o[1] === 0 ? 'Correcto. ' : 'No exactamente. ') + q[2]; }; d.append(b); });
    d.append(fb); $('quiz').append(d);
  });
})();
