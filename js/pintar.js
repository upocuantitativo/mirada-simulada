/* Dibujo compartido: mapa de calor, recorrido y carga de imágenes. */
(function () {
  const STOPS = [[0, [26, 152, 80]], [.35, [217, 239, 59]], [.65, [253, 174, 45]], [1, [215, 25, 28]]];
  function color(v) {
    for (let i = 1; i < STOPS.length; i++) if (v <= STOPS[i][0]) {
      const a = STOPS[i - 1], b = STOPS[i], t = (v - a[0]) / (b[0] - a[0]);
      return [0, 1, 2].map(k => a[1][k] + (b[1][k] - a[1][k]) * t);
    }
    return STOPS[3][1];
  }
  function calor(ctx, m, W, H, ancho, alto, maximo, opacidad) {
    const off = document.createElement('canvas'); off.width = W; off.height = H;
    const c = off.getContext('2d'), im = c.createImageData(W, H);
    let mx = maximo || 0; if (!mx) for (let i = 0; i < m.length; i++) if (m[i] > mx) mx = m[i];
    for (let i = 0; i < m.length; i++) {
      const v = Math.min(1, m[i] / (mx || 1)), [r, g, b] = color(v);
      im.data[i * 4] = r; im.data[i * 4 + 1] = g; im.data[i * 4 + 2] = b;
      im.data[i * 4 + 3] = v < .04 ? 0 : 255 * (opacidad || .68) * Math.min(1, Math.pow(v, .55) * 1.25);
    }
    c.putImageData(im, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(off, 0, 0, ancho, alto); ctx.restore();
  }
  function recorrido(ctx, fix, ancho, alto, hasta, op) {
    const n = hasta == null ? fix.length : Math.min(hasta, fix.length), o = op || {};
    const esc = ancho / 1280, azul = o.color || '#1f4fa8';
    ctx.save(); ctx.lineWidth = 2 * esc; ctx.strokeStyle = azul; ctx.globalAlpha = .75; ctx.beginPath();
    for (let i = 0; i < n; i++) { const x = fix[i].x * ancho, y = fix[i].y * alto; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
    ctx.stroke(); ctx.restore();
    for (let i = 0; i < n; i++) {
      const f = fix[i], x = f.x * ancho, y = f.y * alto, r = (7 + Math.sqrt(f.d) * .62) * esc;
      ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = azul + 'bb'; ctx.fill(); ctx.lineWidth = 1.4 * esc; ctx.strokeStyle = '#fff'; ctx.stroke();
      if (!o.sinNumeros) { ctx.fillStyle = '#fff'; ctx.font = `600 ${Math.max(10, 12 * esc)}px Plex,sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(i + 1, x, y + .5); }
    }
  }
  function zonas(ctx, aois, ancho, alto, seleccion) {
    const esc = ancho / 1280; ctx.save(); ctx.textBaseline = 'top';
    aois.forEach(a => {
      const x = a.x * ancho, y = a.y * alto, w = a.w * ancho, h = a.h * alto, col = a.mensaje ? '#c2290f' : '#1f1f6b';
      ctx.lineWidth = (a.id === seleccion ? 3 : 1.6) * esc; ctx.strokeStyle = col; ctx.setLineDash(a.mensaje ? [] : [6 * esc, 4 * esc]); ctx.strokeRect(x, y, w, h);
      ctx.setLineDash([]); ctx.font = `600 ${Math.max(10, 12.5 * esc)}px Plex,sans-serif`;
      const t = (a.orden ? a.orden + '. ' : '') + a.nombre.slice(0, 34), m = ctx.measureText(t).width + 8 * esc;
      ctx.fillStyle = col; ctx.fillRect(x, y, Math.min(m, Math.max(w, m)), 17 * esc); ctx.fillStyle = '#fff'; ctx.fillText(t, x + 4 * esc, y + 2.5 * esc);
    });
    ctx.restore();
  }
  /** Carga una imagen y devuelve {w,h,datos,lienzo}. Se limita a 1600 px de ancho. */
  async function cargar(src) {
    const img = new Image(); img.src = src; await img.decode();
    const f = Math.min(1, 1600 / img.naturalWidth), w = Math.round(img.naturalWidth * f), h = Math.round(img.naturalHeight * f);
    const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
    const g = cv.getContext('2d', { willReadFrequently: true }); g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); g.drawImage(img, 0, 0, w, h);
    return { w, h, datos: g.getImageData(0, 0, w, h).data, lienzo: cv };
  }
  window.Pintar = { calor, recorrido, zonas, cargar };
})();
