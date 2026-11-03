/* Comprobador de narrativa para informes de Power BI (Módulo 1).
   Lee la definición del informe (no los datos) y aplica reglas deterministas ligadas a los criterios de modulo1/CRITERIOS.md.
   Formatos: carpeta de proyecto PBIP (informe PBIR), .pbix con informe PBIR y .pbix con el formato antiguo (Report/Layout).
   Funciona igual en el navegador (window.Comprobador) y en Node (module.exports), para poder probarlo con ficheros reales. */
(function (raiz) {
  'use strict';

  // ── utilidades ─────────────────────────────────────────────────────────
  const json = t => { try { return JSON.parse(t); } catch (e) { return null; } };
  const lit = o => {                           // valor de una expresión literal de Power BI: "'texto'", "0D", "2L", "true"
    const v = o && o.expr && o.expr.Literal ? o.expr.Literal.Value : (o && o.Literal ? o.Literal.Value : undefined);
    if (typeof v !== 'string') return v;
    if (/^'.*'$/s.test(v)) return v.slice(1, -1).replace(/''/g, "'");
    if (/^-?\d+(\.\d+)?[DLM]$/.test(v)) return parseFloat(v);
    if (v === 'true' || v === 'false') return v === 'true';
    return v;
  };
  const prop = (objs, obj, p) => { const a = objs && objs[obj]; if (!Array.isArray(a)) return undefined;
    for (const e of a) if (e && e.properties && p in e.properties && !e.selector) return lit(e.properties[p]);
    for (const e of a) if (e && e.properties && p in e.properties) return lit(e.properties[p]); return undefined; };
  const colores = objs => { const out = []; for (const e of (objs && objs.dataPoint) || []) {
      const f = e && e.properties && e.properties.fill; const c = f && f.solid && lit(f.solid.color); if (typeof c === 'string') out.push(c.toUpperCase()); } return out; };
  const esGris = hex => { const m = /^#?([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})$/i.exec(hex || ''); if (!m) return false;
    const [r, g, b] = m.slice(1).map(x => parseInt(x, 16)); return Math.max(r, g, b) - Math.min(r, g, b) < 40; };

  function campo(f) {                          // {kind, entidad, nombre} a partir de un campo de consulta
    if (!f) return null;
    if (f.Measure) return { kind: 'medida', entidad: ent(f.Measure), nombre: f.Measure.Property };
    if (f.Column) return { kind: 'columna', entidad: ent(f.Column), nombre: f.Column.Property };
    if (f.Aggregation) { const c = campo(f.Aggregation.Expression) || {}; return { kind: 'implicita', entidad: c.entidad, nombre: c.nombre }; }
    if (f.HierarchyLevel) return { kind: 'columna', entidad: '', nombre: f.HierarchyLevel.Level };
    return null;
  }
  const ent = x => (x.Expression && x.Expression.SourceRef && (x.Expression.SourceRef.Entity || x.Expression.SourceRef.Source)) || '';

  function textos(objs) {                      // párrafos de un cuadro de texto
    const ps = prop(objs, 'general', 'paragraphs') || ((objs && objs.general && objs.general[0] && objs.general[0].properties && objs.general[0].properties.paragraphs) || []);
    return (Array.isArray(ps) ? ps : []).map(p => (p.textRuns || []).map(r => r.value || '').join('')).filter(Boolean);
  }

  // ── lectura de los tres formatos a un modelo común ─────────────────────
  // ficheros: { 'ruta/relativa': texto }. Las rutas pueden empezar por cualquier carpeta.
  function leer(ficheros) {
    const rutas = Object.keys(ficheros).map(r => r.replace(/\\/g, '/'));
    const mapa = {}; Object.keys(ficheros).forEach((r, i) => { mapa[rutas[i]] = ficheros[r]; });
    const layout = rutas.find(r => /(^|\/)Report\/Layout$/.test(r));
    const visPbir = rutas.filter(r => /pages\/[^/]+\/visuals\/[^/]+\/visual\.json$/.test(r));
    if (visPbir.length || rutas.some(r => /pages\/[^/]+\/page\.json$/.test(r))) return leerPbir(mapa, rutas);
    if (layout) return leerLayout(json(mapa[layout]));
    return null;
  }

  function leerPbir(mapa, rutas) {
    const paginas = {}; let orden = [];
    for (const r of rutas) {
      let m = /pages\/([^/]+)\/page\.json$/.exec(r);
      if (m) { const p = json(mapa[r]) || {}; paginas[m[1]] = Object.assign(paginas[m[1]] || { visuales: [] }, { id: m[1], nombre: p.displayName || m[1], ancho: p.width || 1280, alto: p.height || 720 }); continue; }
      m = /pages\/([^/]+)\/visuals\/[^/]+\/visual\.json$/.exec(r);
      if (m) { const v = json(mapa[r]); if (!v || !v.visual) continue; (paginas[m[1]] = paginas[m[1]] || { id: m[1], nombre: m[1], ancho: 1280, alto: 720, visuales: [] }).visuales.push(normPbir(v)); continue; }
      if (/pages\/pages\.json$/.test(r)) orden = (json(mapa[r]) || {}).pageOrder || [];
    }
    const ids = orden.filter(i => paginas[i]).concat(Object.keys(paginas).filter(i => !orden.includes(i)));
    return { formato: 'PBIR', paginas: ids.map(i => paginas[i]) };
  }
  function normPbir(v) {
    const vi = v.visual, pos = v.position || {}, q = (vi.query && vi.query.queryState) || {}, vco = vi.visualContainerObjects || {};
    const campos = [];
    for (const rol of Object.keys(q)) for (const p of (q[rol].projections || [])) { const c = campo(p.field); if (c) campos.push(Object.assign(c, { rol })); }
    return { tipo: vi.visualType || '', x: pos.x || 0, y: pos.y || 0, an: pos.width || 0, al: pos.height || 0, campos,
             objetos: vi.objects || {}, titulo: prop(vco, 'title', 'text'), tituloVisible: prop(vco, 'title', 'show'),
             alt: prop(vco, 'general', 'altText'), ordenado: !!(vi.query && vi.query.sortDefinition), textos: textos(vi.objects) };
  }

  function leerLayout(L) {
    if (!L || !Array.isArray(L.sections)) return null;
    return { formato: 'pbix (formato antiguo)', paginas: L.sections.slice().sort((a, b) => (a.ordinal || 0) - (b.ordinal || 0)).map(s => ({
      id: s.name, nombre: s.displayName || s.name, ancho: s.width || 1280, alto: s.height || 720,
      visuales: (s.visualContainers || []).map(vc => {
        const c = json(vc.config) || {}, sv = c.singleVisual || {}, pq = sv.prototypeQuery || {}, sel = {};
        for (const s2 of pq.Select || []) { const k = campo(s2); if (k) sel[s2.Name] = k; }
        const campos = [];
        for (const rol of Object.keys(sv.projections || {})) for (const p of sv.projections[rol]) {
          const k = sel[p.queryRef] || { kind: /^\w+\(/.test(p.queryRef) ? 'implicita' : 'columna', entidad: '', nombre: p.queryRef };
          campos.push(Object.assign({}, k, { rol }));
        }
        const vco = sv.vcObjects || {};
        return { tipo: sv.visualType || (c.singleVisualGroup ? 'grupo' : ''), x: vc.x || 0, y: vc.y || 0, an: vc.width || 0, al: vc.height || 0, campos,
                 objetos: sv.objects || {}, titulo: prop(vco, 'title', 'text'), tituloVisible: prop(vco, 'title', 'show'),
                 alt: prop(vco, 'general', 'altText'), ordenado: !!(pq.OrderBy && pq.OrderBy.length), textos: textos(sv.objects) };
      }).filter(v => v.tipo && v.tipo !== 'grupo')
    })) };
  }

  // ── clasificación de visuales ──────────────────────────────────────────
  const esTexto = v => v.tipo === 'textbox';
  const esDecor = v => /^(basicShape|shape|image|actionButton|pageNavigator|bookmarkNavigator)$/i.test(v.tipo);
  const esFiltro = v => /slicer/i.test(v.tipo);
  const esTarjeta = v => /^(card|multiRowCard|cardVisual|kpi)$/i.test(v.tipo);
  const esTabla = v => /^(tableEx|pivotTable|table|matrix)$/i.test(v.tipo);
  const esDato = v => !esTexto(v) && !esDecor(v) && !esFiltro(v);
  const esGrafico = v => esDato(v) && !esTarjeta(v) && !esTabla(v);
  const NOMBRE = { pieChart: 'gráfico circular', donutChart: 'anillo', gauge: 'medidor', treemap: 'mapa de árbol', card: 'tarjeta', tableEx: 'tabla', pivotTable: 'matriz',
    lineChart: 'gráfico de líneas', areaChart: 'gráfico de áreas', clusteredBarChart: 'barras', clusteredColumnChart: 'columnas', lineClusteredColumnComboChart: 'columnas y línea',
    stackedBarChart: 'barras apiladas', stackedColumnChart: 'columnas apiladas', funnel: 'embudo', scatterChart: 'dispersión', map: 'mapa', filledMap: 'mapa coroplético', waterfallChart: 'cascada' };
  const nombreVis = v => (v.titulo ? '«' + v.titulo + '»' : (NOMBRE[v.tipo] || v.tipo)) + (v.titulo && NOMBRE[v.tipo] ? ' (' + NOMBRE[v.tipo] + ')' : '');
  const lista = (vs, n = 4) => vs.slice(0, n).map(nombreVis).join(', ') + (vs.length > n ? ' y ' + (vs.length - n) + ' más' : '');
  const series = v => { const y = v.campos.filter(c => /^(Y|Y2|Values)$/.test(c.rol)).length; const s = v.campos.some(c => /^(Series|Legend)$/.test(c.rol));
    return s ? 99 : (/pie|donut|treemap/i.test(v.tipo) ? 99 : y); };

  const VERBO = /\b(sube|suben|baja|bajan|crece|crecen|cae|caen|aumenta|aumentan|disminuye|disminuyen|supera|superan|mejora|mejoran|empeora|empeoran|pierde|pierden|gana|ganan|duplica|duplican|dobla|doblan|concentra|concentran|explica|explican|necesita|necesitan|debe|deben|cumple|cumplen|alcanza|alcanzan|mantiene|mantienen|lidera|lideran|recupera|recuperan|frena|frenan|reduce|reducen|retrocede|retroceden|falta|faltan|sobra|sobran|vende|venden|rises?|falls?|grows?|drops?|increases?|decreases?)\b/i;
  const GENERICO = /^\s*(dashboard|panel|informe|reporte|report|cuadro de mandos?|an[aá]lisis|resumen|kpis?|indicadores|ventas|detalle|p[aá]gina|page)\b/i;
  const COMPARA = /compar|anterior|previo|\bLY\b|\bPY\b|a[nñ]o pasado|\bvs\b|frente|objetivo|presup|budget|target|meta|desv|\bdif|variaci|crec|growth|yoy|ytd|mismo periodo|sameperiod/i;
  const TITULO_DIN = /t[ií]tulo|titular|mensaje|bluf|conclusi|resumen/i;

  // ── reglas por página ──────────────────────────────────────────────────
  // estado: 'cumple' | 'revisar' | 'falla'. peso: importancia en la nota.
  function reglasPagina(p) {
    const arriba = v => v.y < p.alto * 0.2, abajo = v => v.y > p.alto * 0.82;
    // una tarjeta arriba con una medida de título hace de título: no cuenta como visual de datos
    const esTitDin = v => arriba(v) && esTarjeta(v) && v.campos.some(c => c.kind === 'medida' && TITULO_DIN.test(c.nombre));
    const V = p.visuales, datos = V.filter(v => esDato(v) && !esTitDin(v)), graf = V.filter(esGrafico), txt = V.filter(esTexto);
    const R = [];
    const r = (id, criterio, peso, estado, evidencia, accion) => R.push({ id, criterio, peso, estado, evidencia, accion: estado === 'cumple' ? '' : accion });

    // 1. Título de acción (B2.9, B2.7)
    const din = V.filter(esTitDin);
    const tops = txt.filter(arriba).sort((a, b) => a.y - b.y).map(v => v.textos.join(' ').trim()).filter(Boolean);
    const accion = tops.find(t => t.split(/\s+/).length >= 5 && (VERBO.test(t) || /\d\s?%|\d[\d.,]*\s?(M|mill|millones|USD|€|\$)/i.test(t)) && !GENERICO.test(t));
    if (din.length) r('B2.9', 'Título de acción', 3, 'cumple', 'Título dinámico con la medida «' + din[0].campos.find(c => TITULO_DIN.test(c.nombre)).nombre + '»: la conclusión cambia si cambian los datos.');
    else if (accion) r('B2.9', 'Título de acción', 3, 'cumple', 'Título: «' + accion + '».');
    else if (tops.length && tops.some(t => /\?/.test(t))) r('B2.9', 'Título de acción', 3, 'revisar', 'El título es una pregunta: «' + tops[0] + '».', 'Deja la pregunta como antetítulo y escribe debajo la respuesta en una frase con verbo y cifra (por ejemplo, «Las ventas suben un 17,7 %, pero las tiendas comparables caen un 1,1 %»). Si cambia con los filtros, hazla con una medida DAX y ponla en una tarjeta.');
    else if (tops.length) r('B2.9', 'Título de acción', 3, 'falla', 'El título es una etiqueta: «' + tops[0] + '». Dice de qué trata la página, no qué hay que ver.', 'Sustituye la etiqueta por la conclusión en una frase con verbo y cifra. Pregúntate qué debe recordar quien decide si solo lee el título.');
    else r('B2.9', 'Título de acción', 3, 'falla', 'No hay ningún texto en la parte superior de la página.', 'Añade arriba un cuadro de texto (o una tarjeta con una medida de título) con la conclusión de la página.');

    // 2. Referencia de comparación (B1.8)
    const comp = V.flatMap(v => v.campos).filter(c => COMPARA.test(c.nombre || ''));
    if (comp.length) r('B1.8', 'Cifra con referencia', 2, 'cumple', 'Hay medidas de comparación: ' + [...new Set(comp.map(c => c.nombre))].slice(0, 4).join(', ') + '. Comprueba que la comparación es justa (subgrupos, comparables, altas y bajas).');
    else if (datos.length) r('B1.8', 'Cifra con referencia', 2, 'revisar', 'Ninguna medida compara con un año anterior, un objetivo o un grupo de referencia.', 'Una cifra sola no dice si es buena o mala. Añade la referencia que importa a tu audiencia: año anterior, objetivo, media o tiendas comparables, y comprueba que el total no esconde otra lectura.');

    // 3. Carga visual (B3.6, B2.11)
    const n = datos.length;
    if (n) r('B3.6', 'Carga visual', 2, n <= 6 ? 'cumple' : n <= 9 ? 'revisar' : 'falla', n + ' elementos con datos en la página' + (n > 6 ? ': ' + lista(datos, 5) + '.' : '.'),
      'Una página, una idea. Quédate con los visuales que sostienen el título (de dos a cuatro argumentos) y mueve el resto a una página de detalle o anexo.');

    // 4. Gráfico según la pregunta (B3.8)
    const malas = graf.filter(v => /^(pieChart|donutChart|gauge|treemap)$/.test(v.tipo) || /3D/i.test(v.tipo));
    if (graf.length) r('B3.8', 'Gráfico según la pregunta', 2, malas.length === 0 ? 'cumple' : malas.length === 1 ? 'revisar' : 'falla',
      malas.length ? 'Formas difíciles de comparar: ' + lista(malas) + '.' : 'Las formas usadas (' + [...new Set(graf.map(v => NOMBRE[v.tipo] || v.tipo))].join(', ') + ') sirven para comparar o ver evolución.',
      'Para comparar categorías usa barras ordenadas; para el tiempo, líneas; un medidor ocupa mucho para una sola cifra: usa una tarjeta con su referencia. Una tarta solo con dos o tres partes.');

    // 5. Ejes y escalas honestos (B3.9)
    const ejeMal = graf.filter(v => /bar|column/i.test(v.tipo) && typeof prop(v.objetos, 'valueAxis', 'start') === 'number' && prop(v.objetos, 'valueAxis', 'start') !== 0);
    const dosEjes = graf.filter(v => v.campos.some(c => c.rol === 'Y2'));
    const lineaCorte = graf.filter(v => /line|area/i.test(v.tipo) && typeof prop(v.objetos, 'valueAxis', 'start') === 'number' && prop(v.objetos, 'valueAxis', 'start') !== 0);
    if (graf.length) r('B3.9', 'Ejes y escalas honestos', 2, ejeMal.length ? 'falla' : (dosEjes.length || lineaCorte.length) ? 'revisar' : 'cumple',
      ejeMal.length ? 'Barras que no empiezan en cero: ' + lista(ejeMal) + '.' : dosEjes.length ? 'Gráficos con dos ejes: ' + lista(dosEjes) + '. Dos escalas distintas pueden sugerir relaciones que no existen.' : lineaCorte.length ? 'Líneas con el eje cortado: ' + lista(lineaCorte) + '.' : 'Ningún eje de barras cortado ni gráficos con dos ejes.',
      ejeMal.length ? 'Pon el inicio del eje de valores en 0 en las barras (Formato → Eje Y → Inicio).' : 'Si comparas dos medidas, usa la misma escala o dos gráficos; si cortas el eje de una línea, dilo en el subtítulo.');

    // 6. Foco y color (B3.7, B3.10, B3.12)
    const multicolor = graf.filter(v => series(v) >= 2 && colores(v.objetos).length === 0);
    const explicitos = [...new Set(graf.flatMap(v => colores(v.objetos)))];
    if (graf.length) {
      const bien = multicolor.length === 0 && explicitos.length > 0 && explicitos.length <= 4;
      r('B3.7', 'Gris por defecto, un color para el foco', 2, bien ? 'cumple' : multicolor.length >= 2 ? 'falla' : 'revisar',
        bien ? 'Colores elegidos a mano (' + explicitos.join(', ') + ')' + (explicitos.some(esGris) ? ', con gris para el contexto.' : '.') :
        multicolor.length ? 'Visuales con un color por categoría o serie sin elegir: ' + lista(multicolor) + '.' : 'Todos los colores son los del tema por defecto.',
        'Pinta todo en gris y usa un único color de acento para lo que dice el título (Formato → Columnas o Líneas → Color). Usa el mismo color para lo mismo en todas las páginas.');
    }

    // 7. Etiqueta directa en lugar de leyenda (B3.13)
    const conLeyenda = graf.filter(v => series(v) >= 2 && prop(v.objetos, 'legend', 'show') !== false && !/gris|azul|rojo|verde|naranja|negro|grey|blue|red|green/i.test(v.titulo || ''));
    if (graf.some(v => series(v) >= 2)) r('B3.13', 'Etiqueta directa', 1, conLeyenda.length ? 'revisar' : 'cumple',
      conLeyenda.length ? 'Leyenda separada del dato en ' + lista(conLeyenda) + '.' : 'Las series se identifican sin leyenda lejana (etiquetas o colores explicados en el título).',
      'Quita la leyenda y pon el nombre al final de cada línea o en el título del visual («total en gris, comparables en azul»).');

    // 8. Anotación (B3.14)
    const dentro = (t, v) => t.x < v.x + v.an && t.x + t.an > v.x && t.y < v.y + v.al && t.y + t.al > v.y;
    const anot = txt.filter(t => graf.some(v => dentro(t, v)) || (!arriba(t) && !abajo(t)));
    if (graf.length) r('B3.14', 'Anotación', 1, anot.length ? 'cumple' : 'revisar', anot.length ? 'Hay ' + anot.length + ' anotación(es) junto a los datos: «' + anot[0].textos.join(' ').slice(0, 90) + '».' : 'Ningún texto explica dónde ocurre lo importante.',
      'Añade un cuadro de texto pequeño junto al punto donde ocurre algo (una apertura, una caída) diciendo por qué importa.');

    // 9. Subtítulo, fuente y fecha (B3.15)
    const todo = txt.map(t => t.textos.join(' ')).join(' ');
    const fuente = /fuente|source|origen de los datos/i.test(todo), periodo = /\b(19|20)\d{2}\b|actualizad/i.test(todo);
    r('B3.15', 'Fuente, periodo y fecha', 1, fuente && periodo ? 'cumple' : fuente || periodo ? 'revisar' : 'falla',
      fuente && periodo ? 'La página indica la fuente y el periodo.' : fuente ? 'Indica la fuente pero no el periodo ni la actualización.' : periodo ? 'Hay un periodo, pero no la fuente de los datos.' : 'No se indica de dónde salen los datos ni de qué periodo son.',
      'Añade al pie: «Fuente: … Periodo: … Actualizado: …». La unidad y el periodo de cada gráfico van en su subtítulo.');

    // 10. Cifras y nombres legibles (B3.16)
    const implic = V.filter(v => v.campos.some(c => c.kind === 'implicita'));
    const sinTit = datos.filter(v => !v.titulo || /^(sum|suma|count|recuento|average|promedio|min|max)\b|\bof\b/i.test(v.titulo));
    if (datos.length) r('B3.16', 'Cifras y nombres legibles', 1, implic.length + sinTit.length === 0 ? 'cumple' : (implic.length && sinTit.length) ? 'falla' : 'revisar',
      [implic.length ? 'Agregaciones automáticas («Suma de…») en ' + lista(implic) + '.' : '', sinTit.length ? 'Visuales sin título propio o con el nombre técnico: ' + lista(sinTit) + '.' : ''].filter(Boolean).join(' ') || 'Medidas con nombre y títulos propios en todos los visuales.',
      'Crea medidas con nombre (Ventas = SUM(...)) en lugar de arrastrar la columna, pon a cada visual un título en castellano con su unidad y redondea: «2,80 M USD» se lee antes que «2.796.629,35».');

    // 11. Accesibilidad (B3.11)
    const conAlt = datos.filter(v => v.alt);
    if (datos.length) r('B3.11', 'Texto alternativo', 1, conAlt.length === datos.length ? 'cumple' : conAlt.length ? 'revisar' : 'falla',
      conAlt.length + ' de ' + datos.length + ' visuales con texto alternativo.',
      'Escribe en cada visual (Formato → General → Texto alternativo) qué muestra y qué conclusión tiene, para quien usa lector de pantalla. Y no confíes solo en el color: añade etiqueta o signo.');

    // 12. Explicar, no explorar (B1.2)
    const filtros = V.filter(esFiltro).length;
    const tablas = V.filter(v => esTabla(v) && v.campos.length >= 6 && v.an * v.al > p.ancho * p.alto * 0.15);
    r('B1.2', 'Explicar, no explorar', 1, filtros > 3 && tablas.length ? 'falla' : (filtros > 3 || tablas.length) ? 'revisar' : 'cumple',
      [filtros > 3 ? filtros + ' segmentadores: la página invita a buscar en vez de leer.' : '', tablas.length ? 'Tabla de detalle grande: ' + lista(tablas) + '.' : ''].filter(Boolean).join(' ') || 'Pocos filtros y sin tablas de detalle que compitan con el mensaje.',
      'Deja uno o dos filtros que respondan a la pregunta de la audiencia y lleva la tabla de detalle a una página de anexo.');
    return R;
  }

  // ── reglas del informe completo ────────────────────────────────────────
  function reglasInforme(inf, porPagina) {
    const R = [], P = inf.paginas;
    const conDatos = porPagina.filter(x => x.reglas.length);
    if (conDatos.length > 1) {
      const ok = conDatos.filter(x => x.reglas.find(q => q.id === 'B2.9' && q.estado === 'cumple')).length;
      R.push({ id: 'B2.10', criterio: 'Titles test', peso: 1, estado: ok === conDatos.length ? 'cumple' : ok ? 'revisar' : 'falla',
        evidencia: ok + ' de ' + conDatos.length + ' páginas con datos tienen título de acción. Leídos seguidos deberían contar la historia.',
        accion: ok === conDatos.length ? '' : 'Escribe un título de acción en cada página y léelos seguidos: deben formar el resumen ejecutivo.' });
    }
    if (P.length > 1) {
      const genericas = P.filter(p => /^(page|p[aá]gina|pagina)\s*\d+$/i.test(p.nombre) || /^(duplicado|copia|copy)/i.test(p.nombre));
      const primeraDetalle = P[0].visuales.some(v => esTabla(v) && v.an * v.al > P[0].ancho * P[0].alto * 0.3);
      R.push({ id: 'B2.12', criterio: 'Arquitectura del informe', peso: 1, estado: genericas.length || primeraDetalle ? 'revisar' : 'cumple',
        evidencia: [genericas.length ? 'Páginas con nombre genérico: ' + genericas.map(p => '«' + p.nombre + '»').join(', ') + '.' : '', primeraDetalle ? 'La primera página es una tabla de detalle.' : ''].filter(Boolean).join(' ') || 'Páginas con nombre propio: ' + P.map(p => '«' + p.nombre + '»').join(', ') + '.',
        accion: 'Ordena las páginas como la historia (conclusión, evidencia, detalle) y nómbralas por lo que cuentan.' });
    }
    return R;
  }

  const VALOR = { cumple: 1, revisar: 0.5, falla: 0 };
  const nota = rs => { const w = rs.reduce((s, x) => s + x.peso, 0); return w ? Math.round(rs.reduce((s, x) => s + x.peso * VALOR[x.estado], 0) / w * 100) / 10 : null; };
  function valoracion(n) {
    if (n === null) return 'Sin visuales que analizar';
    if (n >= 8) return 'Cuenta una historia: la conclusión se ve y está sostenida';
    if (n >= 6) return 'Va por buen camino: falta pulir el foco o el contexto';
    if (n >= 4) return 'Informa, pero no concluye: es más un cuadro de mandos que una narrativa';
    return 'Cuadro de mandos sin mensaje: quien lo vea tendrá que sacar sus propias conclusiones';
  }

  function analizar(ficheros) {
    const inf = leer(ficheros);
    if (!inf || !inf.paginas.length) return { error: 'No encuentro la definición del informe. Sube la carpeta del proyecto (.pbip), la carpeta «.Report» o un fichero .pbix.' };
    const paginas = inf.paginas.map(p => { const reglas = reglasPagina(p), datos = p.visuales.filter(esDato).length;
      // una portada o una página solo de texto no se puntúa
      return datos ? { nombre: p.nombre, visuales: p.visuales.length, datos, reglas, nota: nota(reglas), valoracion: valoracion(nota(reglas)) }
                   : { nombre: p.nombre, visuales: p.visuales.length, datos, reglas: [], nota: null, valoracion: 'Página sin visuales con datos (portada o texto): no se puntúa' }; });
    const informe = reglasInforme(inf, paginas);
    const conDatos = paginas.filter(p => p.datos > 0);
    const media = conDatos.length ? conDatos.reduce((s, p) => s + p.nota, 0) / conDatos.length : null;
    const notaInf = informe.length && media !== null ? Math.round((media * 0.85 + nota(informe) * 0.15) * 10) / 10 : (media === null ? null : Math.round(media * 10) / 10);
    // acciones: primero lo que falla, por peso; una por criterio y página
    const acciones = [];
    paginas.forEach(p => p.reglas.forEach(x => { if (x.estado !== 'cumple') acciones.push({ pagina: p.nombre, id: x.id, criterio: x.criterio, estado: x.estado, peso: x.peso, accion: x.accion, evidencia: x.evidencia }); }));
    informe.forEach(x => { if (x.estado !== 'cumple') acciones.push({ pagina: 'Todo el informe', id: x.id, criterio: x.criterio, estado: x.estado, peso: x.peso, accion: x.accion, evidencia: x.evidencia }); });
    // una acción por criterio: se juntan las páginas afectadas y manda el estado más grave
    const grupos = {};
    for (const x of acciones) {
      const g = grupos[x.id];
      if (!g) grupos[x.id] = Object.assign({}, x, { paginas: [x.pagina] });
      else { g.paginas.push(x.pagina); if (x.estado === 'falla' && g.estado !== 'falla') Object.assign(g, { estado: 'falla', evidencia: x.evidencia, accion: x.accion }); }
    }
    const agrupadas = Object.values(grupos).map(g => Object.assign(g, { pagina: g.paginas.length > 2 ? g.paginas.length + ' páginas' : g.paginas.join(' y ') }));
    agrupadas.sort((a, b) => (a.estado === b.estado ? 0 : a.estado === 'falla' ? -1 : 1) || b.peso - a.peso || b.paginas.length - a.paginas.length);
    informe.forEach(x => { if (x.estado === 'cumple') x.accion = ''; });
    return { formato: inf.formato, paginas, informe, nota: notaInf, valoracion: valoracion(notaInf), acciones: agrupadas };
  }

  // Lo que el fichero no permite comprobar: se pregunta a la persona
  const MANUAL = [
    ['B1.5', 'Audiencia y decisión', '¿Sabes quién decide, qué decide y qué sabe ya? Escríbelo en una frase antes de mirar el panel.'],
    ['B2.3', 'Big Idea', '¿Puedes decir la conclusión en una frase completa, con punto de vista y lo que está en juego, sin el gráfico delante?'],
    ['B1.9', 'Hecho, interpretación e hipótesis', '¿Los textos separan lo que dicen los datos de lo que tú interpretas o supones sobre la causa?'],
    ['', 'Cifras correctas', '¿Has comprobado las cifras clave por otro camino (Excel, una consulta, cifras de control)? Una relación mal hecha da números creíbles y falsos.'],
    ['M1-M6', 'Mirada', '¿Encuentra el comité el mensaje en los primeros segundos? Sube una captura al Laboratorio y mira el mapa de calor por audiencia.'],
  ];

  const Comprobador = { analizar, leer, MANUAL, version: '1.0' };
  if (typeof module !== 'undefined' && module.exports) module.exports = Comprobador; else raiz.Comprobador = Comprobador;
})(typeof window !== 'undefined' ? window : this);
