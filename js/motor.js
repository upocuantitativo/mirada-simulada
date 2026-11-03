/* Motor de atención simulada. Sin dependencias; funciona en el navegador y en Node.
   Mapa ascendente:  residuo espectral (Hou y Zhang, 2007) + contraste centro-periferia (Itti, Koch y Niebur, 1998).
   Mapa descendente: pesos de cada audiencia sobre el tipo de zona; la tarea cambia la mirada (Yarbus, 1967).
   Recorrido: muestreo secuencial con inhibición de retorno, sesgo central (Tatler, 2007) y lectura desde arriba a la izquierda.
   Es un modelo didáctico: NO está calibrado con registros oculares humanos. Los parámetros de PERSONAS son supuestos. */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Motor = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const VERSION = '1.0';
  const GW = 96;                // ancho de la rejilla de atención
  const GRADOS_ANCHO = 30.37;   // ancho de imagen en grados visuales (pantalla de instrumento.json)

  // Audiencias del caso Adventure Works del curso. tiempo = segundos; fijacion = ms; asc = peso del mapa ascendente.
  const PERSONAS = {
    direccion: { nombre: 'Alta Dirección', pregunta: '¿Qué decisión tomamos?', tiempo: 10, fijacion: 240, asc: .8, lectura: .9,
      pesos: { titulo: 3, kpi: 3, accion: 4, anotacion: 2, grafico: 1.2, texto: .5, tabla: .2, leyenda: .2, filtro: .1, decoracion: .3 } },
    comercial: { nombre: 'Comercial', pregunta: '¿Por qué pasa y qué hago?', tiempo: 20, fijacion: 250, asc: .9, lectura: .7,
      pesos: { titulo: 2, kpi: 1.5, accion: 3, anotacion: 2.5, grafico: 3, texto: 1, tabla: 1.5, leyenda: .6, filtro: 1.2, decoracion: .4 } },
    finanzas: { nombre: 'Finanzas', pregunta: '¿Cuál es el impacto y el riesgo?', tiempo: 30, fijacion: 280, asc: .6, lectura: .8,
      pesos: { titulo: 1.5, kpi: 2.5, accion: 1.5, anotacion: 1.2, grafico: 1.5, texto: 2, tabla: 4, leyenda: .8, filtro: .6, decoracion: .1 } },
    analista: { nombre: 'Analista', pregunta: '¿Cómo se calcula esto?', tiempo: 45, fijacion: 300, asc: .5, lectura: .6,
      pesos: { titulo: 1, kpi: 1.2, accion: .8, anotacion: 1.5, grafico: 2.5, texto: 2.5, tabla: 3.5, leyenda: 2.5, filtro: 3, decoracion: .1 } },
    operaciones: { nombre: 'Operaciones', pregunta: '¿Qué hago mañana?', tiempo: 12, fijacion: 240, asc: .9, lectura: .8,
      pesos: { titulo: 1.5, kpi: 1, accion: 4.5, anotacion: 2, grafico: .8, texto: .8, tabla: 1.5, leyenda: .3, filtro: .3, decoracion: .3 } }
  };
  const TIPOS = { titulo: 'Título', kpi: 'Indicador', accion: 'Petición o acción', anotacion: 'Anotación', grafico: 'Gráfico', tabla: 'Tabla', texto: 'Texto', leyenda: 'Leyenda', filtro: 'Filtro o menú', decoracion: 'Decoración' };

  // ---- azar reproducible -------------------------------------------------------------
  function azar(semilla) {
    let a = semilla >>> 0;
    const u = function () { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    u.normal = function () { let x = 0; while (x === 0) x = u(); return Math.sqrt(-2 * Math.log(x)) * Math.cos(2 * Math.PI * u()); };
    u.lognormal = function (s) { return Math.exp(s * u.normal() - s * s / 2); };
    return u;
  }
  function hash(texto) { let h = 2166136261; for (let i = 0; i < texto.length; i++) { h ^= texto.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(16).padStart(8, '0'); }

  // ---- utilidades de imagen ---------------------------------------------------------
  function reducir(canal, w, h, W, H) {
    const s = new Float32Array(W * H);
    for (let Y = 0; Y < H; Y++) {
      const y0 = Math.floor(Y * h / H), y1 = Math.max(y0 + 1, Math.floor((Y + 1) * h / H));
      for (let X = 0; X < W; X++) {
        const x0 = Math.floor(X * w / W), x1 = Math.max(x0 + 1, Math.floor((X + 1) * w / W));
        let t = 0; for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) t += canal[y * w + x];
        s[Y * W + X] = t / ((x1 - x0) * (y1 - y0));
      }
    }
    return s;
  }
  function difuminar(m, W, H, sigma) {
    const r = Math.max(1, Math.ceil(sigma * 2.5)), k = []; let sum = 0;
    for (let i = -r; i <= r; i++) { const v = Math.exp(-i * i / (2 * sigma * sigma)); k.push(v); sum += v; }
    for (let i = 0; i < k.length; i++) k[i] /= sum;
    const t = new Float32Array(W * H), o = new Float32Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { let a = 0; for (let i = -r; i <= r; i++) { const X = Math.min(W - 1, Math.max(0, x + i)); a += m[y * W + X] * k[i + r]; } t[y * W + x] = a; }
    for (let x = 0; x < W; x++) for (let y = 0; y < H; y++) { let a = 0; for (let i = -r; i <= r; i++) { const Y = Math.min(H - 1, Math.max(0, y + i)); a += t[Y * W + x] * k[i + r]; } o[y * W + x] = a; }
    return o;
  }
  function normalizar(m) {
    let a = Infinity, b = -Infinity; for (let i = 0; i < m.length; i++) { if (m[i] < a) a = m[i]; if (m[i] > b) b = m[i]; }
    const o = new Float32Array(m.length), d = b - a || 1; for (let i = 0; i < m.length; i++) o[i] = (m[i] - a) / d; return o;
  }
  function escalar(m, w, h, W, H) { // bilineal
    const o = new Float32Array(W * H);
    for (let Y = 0; Y < H; Y++) { const fy = (Y + .5) * h / H - .5, y0 = Math.max(0, Math.floor(fy)), y1 = Math.min(h - 1, y0 + 1), ty = Math.max(0, fy - y0);
      for (let X = 0; X < W; X++) { const fx = (X + .5) * w / W - .5, x0 = Math.max(0, Math.floor(fx)), x1 = Math.min(w - 1, x0 + 1), tx = Math.max(0, fx - x0);
        o[Y * W + X] = (m[y0 * w + x0] * (1 - tx) + m[y0 * w + x1] * tx) * (1 - ty) + (m[y1 * w + x0] * (1 - tx) + m[y1 * w + x1] * tx) * ty; } }
    return o;
  }

  // ---- FFT 2D radix-2 ---------------------------------------------------------------
  function fft1(re, im, inv) {
    const n = re.length;
    for (let i = 1, j = 0; i < n; i++) { let b = n >> 1; for (; j & b; b >>= 1) j ^= b; j ^= b; if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (let l = 2; l <= n; l <<= 1) { const a = (inv ? 2 : -2) * Math.PI / l, wr = Math.cos(a), wi = Math.sin(a);
      for (let i = 0; i < n; i += l) { let cr = 1, ci = 0; for (let k = 0; k < l / 2; k++) { const u = i + k, v = u + l / 2, xr = re[v] * cr - im[v] * ci, xi = re[v] * ci + im[v] * cr; re[v] = re[u] - xr; im[v] = im[u] - xi; re[u] += xr; im[u] += xi; const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } } }
    if (inv) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
  }
  function fft2(re, im, n, inv) {
    const fr = new Float64Array(n), fi = new Float64Array(n);
    for (let y = 0; y < n; y++) { for (let x = 0; x < n; x++) { fr[x] = re[y * n + x]; fi[x] = im[y * n + x]; } fft1(fr, fi, inv); for (let x = 0; x < n; x++) { re[y * n + x] = fr[x]; im[y * n + x] = fi[x]; } }
    for (let x = 0; x < n; x++) { for (let y = 0; y < n; y++) { fr[y] = re[y * n + x]; fi[y] = im[y * n + x]; } fft1(fr, fi, inv); for (let y = 0; y < n; y++) { re[y * n + x] = fr[y]; im[y * n + x] = fi[y]; } }
  }
  function residuoEspectral(gris, w, h) {
    const n = 64, g = reducir(gris, w, h, n, n), re = new Float64Array(n * n), im = new Float64Array(n * n);
    for (let i = 0; i < n * n; i++) re[i] = g[i];
    fft2(re, im, n, false);
    const lg = new Float32Array(n * n), fa = new Float32Array(n * n);
    for (let i = 0; i < n * n; i++) { lg[i] = Math.log(Math.hypot(re[i], im[i]) + 1e-6); fa[i] = Math.atan2(im[i], re[i]); }
    const media = new Float32Array(n * n);
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) { let t = 0; for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) t += lg[((y + a + n) % n) * n + (x + b + n) % n]; media[y * n + x] = t / 9; }
    for (let i = 0; i < n * n; i++) { const e = Math.exp(lg[i] - media[i]); re[i] = e * Math.cos(fa[i]); im[i] = e * Math.sin(fa[i]); }
    fft2(re, im, n, true);
    const s = new Float32Array(n * n); for (let i = 0; i < n * n; i++) s[i] = re[i] * re[i] + im[i] * im[i];
    return normalizar(difuminar(s, n, n, 2.2));
  }

  /** Mapa ascendente. rgba = Uint8 RGBA de w×h. Devuelve {mapa, W, H}. */
  function saliencia(rgba, w, h) {
    const N = w * h, L = new Float32Array(N), RG = new Float32Array(N), BY = new Float32Array(N);
    for (let i = 0; i < N; i++) { const r = rgba[i * 4], g = rgba[i * 4 + 1], b = rgba[i * 4 + 2]; L[i] = (.299 * r + .587 * g + .114 * b) / 255; RG[i] = (r - g) / 255; BY[i] = ((r + g) / 2 - b) / 255; }
    const W = GW, H = Math.max(8, Math.round(GW * h / w));
    const sr = escalar(residuoEspectral(L, w, h), 64, 64, W, H);
    const con = new Float32Array(W * H);
    [[L, 1], [RG, 1.3], [BY, 1.3]].forEach(function (par) {
      const c = reducir(par[0], w, h, W, H), f = difuminar(c, W, H, 1);
      [6, 12].forEach(function (s) { const sur = difuminar(c, W, H, s); for (let i = 0; i < W * H; i++) con[i] += par[1] * Math.abs(f[i] - sur[i]); });
    });
    const nc = normalizar(con), m = new Float32Array(W * H);
    for (let i = 0; i < W * H; i++) m[i] = .35 * sr[i] + .65 * nc[i];
    return { mapa: normalizar(difuminar(m, W, H, 1)), W: W, H: H };
  }

  function aoiEn(aois, x, y) { // la zona más pequeña que contiene el punto
    let mejor = null, area = Infinity;
    for (const a of aois) if (x >= a.x && x <= a.x + a.w && y >= a.y && y <= a.y + a.h) { const s = a.w * a.h; if (s < area) { area = s; mejor = a; } }
    return mejor;
  }

  function campoDescendente(mapa, aois, persona, clave, pesosObs) {
    const W = mapa.W, H = mapa.H, T = new Float32Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const a = aoiEn(aois, (x + .5) / W, (y + .5) / H);
      if (a) { const base = (persona.pesos[a.tipo] == null ? 1 : persona.pesos[a.tipo]) * pesosObs(a.tipo);
        // el peso se reparte por superficie: una zona grande no gana solo por ocupar más celdas
        const tam = Math.pow(Math.max(.012, a.w * a.h) / .05, -.6);
        T[y * W + x] = base * tam * ((a.para || []).indexOf(clave) >= 0 ? 1.5 : 1); }
    }
    return T;
  }

  /** Simula un observador. Devuelve la lista de fijaciones {x,y,d,t,aoi}. x, y en 0..1; d y t en ms. */
  function observador(mapa, aois, clave, opciones, rng) {
    const P = PERSONAS[clave], W = mapa.W, H = mapa.H, S = mapa.mapa, nC = W * H, asp = H / W;
    const tiempo = (opciones.tiempos && opciones.tiempos[clave] || P.tiempo) * 1000 * rng.lognormal(.2);
    const varP = {}; const pesosObs = function (t) { if (varP[t] == null) varP[t] = rng.lognormal(.3); return varP[t]; };
    const T = campoDescendente(mapa, aois, P, clave, pesosObs);
    const hayAOI = aois.length > 0, IOR = new Float32Array(nC).fill(1), asc = P.asc * rng.lognormal(.15);
    const prior = new Float32Array(nC), lect = new Float32Array(nC);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const ny = (y + .5) / H, nx = (x + .5) / W;
      const central = Math.exp(-((nx - .5) ** 2 + ((ny - .5) * asp) ** 2) / (2 * .32 * .32));
      lect[y * W + x] = Math.exp(-P.lectura * (.55 * nx + 1.1 * ny));
      const base = Math.pow(.04 + S[y * W + x], 1.6 * asc) * (hayAOI ? .12 + T[y * W + x] : 1);
      prior[y * W + x] = base * central;
    }
    const pC = new Float32Array(nC), fix = [];
    let t = 0, cx = W / 2, cy = H / 2, aPrev = null;
    const salto = .16 * W;               // longitud característica del salto
    while (t < tiempo && fix.length < 400) {
      let tot = 0;
      const ini = fix.length < 4 ? 3 : 1;   // las primeras miradas buscan el titular: orientación antes que exploración
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const d = Math.hypot(x - cx, y - cy), v = prior[y * W + x] * IOR[y * W + x] * Math.pow(lect[y * W + x], ini) * Math.exp(-d / salto);
        pC[y * W + x] = v; tot += v;
      }
      let r = rng() * tot, i = nC - 1;
      for (let k = 0; k < nC; k++) { r -= pC[k]; if (r <= 0) { i = k; break; } }
      const gx = i % W, gy = (i - gx) / W;
      const x = (gx + rng()) / W, y = (gy + rng()) / H, a = aoiEn(aois, x, y);
      const lectora = a && (a.tipo === 'texto' || a.tipo === 'tabla' || a.tipo === 'accion') ? 1.25 : 1;
      const d = Math.min(1600, Math.max(80, P.fijacion * lectora * rng.lognormal(.4)));
      const amp = fix.length ? Math.hypot((gx - cx) / W, (gy - cy) / W) * GRADOS_ANCHO : 0;
      t += 21 + 2.2 * amp;               // secuencia principal del movimiento sacádico
      fix.push({ x: +x.toFixed(4), y: +y.toFixed(4), d: Math.round(d), t: Math.round(t), aoi: a ? a.id : null });
      t += d; cx = gx; cy = gy; aPrev = a;
      for (let k = 0; k < nC; k++) IOR[k] = Math.min(1, IOR[k] + (1 - IOR[k]) * .1);   // la inhibición se desvanece
      const R = Math.ceil(W * .1), sg2 = (W * .055) ** 2;
      for (let yy = Math.max(0, gy - R); yy <= Math.min(H - 1, gy + R); yy++) for (let xx = Math.max(0, gx - R); xx <= Math.min(W - 1, gx + R); xx++) {
        IOR[yy * W + xx] *= 1 - .9 * Math.exp(-((xx - gx) ** 2 + (yy - gy) ** 2) / (2 * sg2));
      }
    }
    return fix;
  }

  /** Lanza el comité. comite = {direccion:6, finanzas:4...}. progreso(hechos,total) opcional; asíncrono para no bloquear la página. */
  async function simular(entrada) {
    const mapa = entrada.mapa, aois = entrada.aois || [], comite = entrada.comite, semilla = entrada.semilla >>> 0;
    const lista = []; Object.keys(PERSONAS).forEach(function (k) { for (let i = 0; i < (comite[k] || 0); i++) lista.push(k); });
    const obs = [];
    for (let i = 0; i < lista.length; i++) {
      const rng = azar((semilla * 2654435761 + i * 40503 + 7) >>> 0);
      obs.push({ persona: lista[i], fijaciones: observador(mapa, aois, lista[i], entrada, rng) });
      if (entrada.progreso) { entrada.progreso(i + 1, lista.length); if (i % 4 === 3) await new Promise(function (r) { setTimeout(r, 0); }); }
    }
    return obs;
  }

  function simularSinc(entrada) {
    const lista = []; Object.keys(PERSONAS).forEach(function (k) { for (let i = 0; i < (entrada.comite[k] || 0); i++) lista.push(k); });
    return lista.map(function (k, i) { return { persona: k, fijaciones: observador(entrada.mapa, entrada.aois || [], k, entrada, azar(((entrada.semilla >>> 0) * 2654435761 + i * 40503 + 7) >>> 0)) }; });
  }

  // ---- capa de instrumento (tabla calculada con PyEtSimul) ----------------------------
  function instrumentar(obs, aois, montaje, semilla, proporcion) {
    if (!montaje) return obs;
    const rng = azar((semilla ^ 0x51ED270B) >>> 0), pr = proporcion || 1;
    const sd = Math.hypot(montaje.error_cabeza_deg || 0, .25) / GRADOS_ANCHO / 1.25;
    function sesgo(x, y) { let d = 1e9, e = montaje.sesgo[0]; for (const s of montaje.sesgo) { const v = (s.x - x) ** 2 + (s.y - y) ** 2; if (v < d) { d = v; e = s; } } return e; }
    return obs.map(function (o) {
      const cab = { x: rng.normal() * sd, y: rng.normal() * sd };    // deriva común del observador
      return { persona: o.persona, fijaciones: o.fijaciones.map(function (f) {
        const s = sesgo(f.x, f.y);
        const x = Math.min(1, Math.max(0, f.x + s.dx + cab.x + rng.normal() * sd * .25));
        const y = Math.min(1, Math.max(0, f.y + (s.dy + cab.y + rng.normal() * sd * .25) / pr));
        const a = aoiEn(aois, x, y);
        return { x: +x.toFixed(4), y: +y.toFixed(4), d: f.d, t: f.t, aoi: a ? a.id : null };
      }) };
    });
  }

  // ---- métricas ------------------------------------------------------------------------
  function mediana(v) { if (!v.length) return null; const s = v.slice().sort(function (a, b) { return a - b; }), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }
  function wilson(k, n) { if (!n) return [0, 0]; const z = 1.96, p = k / n, d = 1 + z * z / n, c = p + z * z / (2 * n), m = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return [Math.max(0, (c - m) / d), Math.min(1, (c + m) / d)]; }
  function edicion(a, b) { const f = []; for (let i = 0; i <= a.length; i++) { f.push([i]); } for (let j = 1; j <= b.length; j++) f[0][j] = j; for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) f[i][j] = Math.min(f[i - 1][j] + 1, f[i][j - 1] + 1, f[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); return f[a.length][b.length]; }

  function metricas(obs, aois) {
    const n = obs.length, ids = aois.map(function (a) { return a.id; });
    const fila = {}; aois.forEach(function (a) { fila[a.id] = { id: a.id, nombre: a.nombre, tipo: a.tipo, mensaje: !!a.mensaje, vistos: 0, ttff: [], tiempo: 0, entradas: 0 }; });
    let total = 0, fuera = 0, nf = 0;
    const ordenada = aois.filter(function (a) { return a.orden > 0; }).sort(function (a, b) { return a.orden - b.orden; }).map(function (a) { return a.id; });
    const msg = aois.filter(function (a) { return a.mensaje; }).map(function (a) { return a.id; });
    const sims = [], cel = {}; let vistoMsg = 0;
    obs.forEach(function (o) {
      const visto = {}; let prev = null; const seq = [];
      o.fijaciones.forEach(function (f) {
        total += f.d; nf++; cel[Math.floor(f.x * 16) + ',' + Math.floor(f.y * 10)] = (cel[Math.floor(f.x * 16) + ',' + Math.floor(f.y * 10)] || 0) + f.d;
        if (!f.aoi || !fila[f.aoi]) { fuera += f.d; prev = null; return; }
        const r = fila[f.aoi]; r.tiempo += f.d;
        if (!visto[f.aoi]) { visto[f.aoi] = 1; r.vistos++; r.ttff.push(f.t); if (ordenada.indexOf(f.aoi) >= 0) seq.push(f.aoi); }
        if (prev !== f.aoi) r.entradas++;
        prev = f.aoi;
      });
      if (msg.length && msg.some(function (m) { return visto[m]; })) vistoMsg++;
      if (ordenada.length > 1) sims.push(1 - edicion(seq, ordenada) / Math.max(seq.length, ordenada.length));
    });
    const filas = ids.map(function (id) { const r = fila[id]; return { id: id, nombre: r.nombre, tipo: r.tipo, mensaje: r.mensaje, vieron: n ? r.vistos / n : 0, ic95: wilson(r.vistos, n), ttff_ms: mediana(r.ttff), tiempo_pct: total ? r.tiempo / total : 0, entradas: r.vistos ? r.entradas / r.vistos : 0 }; });
    let H = 0; Object.keys(cel).forEach(function (k) { const p = cel[k] / total; H -= p * Math.log(p); });
    const decor = filas.filter(function (f) { return f.tipo === 'decoracion'; }).reduce(function (s, f) { return s + f.tiempo_pct; }, 0);
    const fm = filas.filter(function (f) { return f.mensaje; });
    return {
      observadores: n, fijaciones_por_persona: n ? nf / n : 0, zonas: filas,
      mensaje: { vieron: n ? vistoMsg / n : 0, ic95: wilson(vistoMsg, n), ttff_ms: mediana(fm.map(function (f) { return f.ttff_ms; }).filter(function (v) { return v != null; })), tiempo_pct: fm.reduce(function (s, f) { return s + f.tiempo_pct; }, 0) },
      orden_narrativo: sims.length ? sims.reduce(function (a, b) { return a + b; }, 0) / sims.length : null,
      decoracion_pct: decor, fuera_pct: total ? fuera / total : 0, dispersion: H / Math.log(160)
    };
  }
  function porPersona(obs, aois) {
    const salida = {}; Object.keys(PERSONAS).forEach(function (k) { const s = obs.filter(function (o) { return o.persona === k; }); if (s.length) salida[k] = metricas(s, aois); });
    return salida;
  }

  /** Mapa de atención: gaussianas ponderadas por duración (Wooding, 2002). */
  function mapaAtencion(obs, W, H, sigma) {
    const m = new Float32Array(W * H), s = sigma || W * .035, R = Math.ceil(s * 3), s2 = 2 * s * s;
    obs.forEach(function (o) { o.fijaciones.forEach(function (f) {
      const cx = f.x * W, cy = f.y * H;
      for (let y = Math.max(0, Math.floor(cy - R)); y <= Math.min(H - 1, Math.ceil(cy + R)); y++) for (let x = Math.max(0, Math.floor(cx - R)); x <= Math.min(W - 1, Math.ceil(cx + R)); x++)
        m[y * W + x] += f.d * Math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / s2);
    }); });
    return m;
  }

  /** Diagnóstico por reglas: no decide por la persona, señala dónde mirar. */
  function alertas(m) {
    const a = [], pct = function (v) { return Math.round(v * 100) + ' %'; };
    if (m.mensaje.ttff_ms == null && !m.zonas.some(function (z) { return z.mensaje; })) { a.push({ nivel: 'aviso', texto: 'No has marcado ninguna zona como mensaje: sin ella no se puede saber si la mirada lo encuentra.' }); return a; }
    if (m.mensaje.vieron < .6) a.push({ nivel: 'grave', texto: 'Solo el ' + pct(m.mensaje.vieron) + ' llega a mirar el mensaje. Súbelo, dale contraste o quita lo que compite con él.' });
    else if (m.mensaje.vieron < .85) a.push({ nivel: 'medio', texto: 'El ' + pct(m.mensaje.vieron) + ' mira el mensaje: una parte del comité se va sin verlo.' });
    if (m.mensaje.ttff_ms != null && m.mensaje.ttff_ms > 3000) a.push({ nivel: 'medio', texto: 'El mensaje tarda ' + (m.mensaje.ttff_ms / 1000).toFixed(1).replace('.', ',') + ' s en recibir la primera mirada.' });
    if (m.decoracion_pct > .1) a.push({ nivel: 'medio', texto: 'La decoración se lleva el ' + pct(m.decoracion_pct) + ' del tiempo.' });
    if (m.mensaje.tiempo_pct < m.decoracion_pct) a.push({ nivel: 'grave', texto: 'La decoración recibe más tiempo que el mensaje.' });
    if (m.orden_narrativo != null && m.orden_narrativo < .5) a.push({ nivel: 'medio', texto: 'El recorrido se parece poco al orden en que quieres contar la historia.' });
    return a;
  }

  function desdeRejilla(m, w, h, ancho, alto) { const W = GW, H = Math.max(8, Math.round(GW * alto / ancho)); return { mapa: normalizar(escalar(m, w, h, W, H)), W: W, H: H }; }

  return { VERSION, GW, GRADOS_ANCHO, desdeRejilla, PERSONAS, TIPOS, azar, hash, saliencia, simular, simularSinc, instrumentar, metricas, porPersona, mapaAtencion, alertas, aoiEn, edicion, wilson };
});
