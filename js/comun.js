/* Acceso y cabecera común. La sesión vive solo en este navegador: nada se envía a ningún servidor.
   El código de curso es una barrera de cortesía, no seguridad: el repositorio es público. */
(function () {
  const CLAVE = 'mirada.sesion', HUELLA = 'c409b493';   // huella del código de curso (ver montar.html)
  function fnv(t) { let h = 2166136261; for (let i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(16).padStart(8, '0'); }
  function leer() { try { return JSON.parse(localStorage.getItem(CLAVE)) || window.__ses || null; } catch (e) { return window.__ses || null; } }
  function guardar(s) { window.__ses = s; try { localStorage.setItem(CLAVE, JSON.stringify(s)); } catch (e) {} }
  const Acceso = {
    sesion: leer,
    entrar(nombre, correo, codigo) {
      if (fnv(codigo.trim().toUpperCase()) !== HUELLA) return false;
      guardar({ nombre: nombre.trim(), correo: correo.trim(), desde: new Date().toISOString() }); return true;
    },
    salir() { try { localStorage.removeItem(CLAVE); } catch (e) {} window.__ses = null; location.href = 'index.html'; },
    fnv
  };
  window.Acceso = Acceso;
  const pag = document.body.dataset.pagina;
  if (!pag) return;
  const s = leer();
  if (!s) { location.replace('index.html?volver=' + encodeURIComponent(location.pathname.split('/').pop() + location.search)); return; }
  const items = [['centro', 'centro.html', 'Inicio'], ['teoria', 'teoria.html', 'Teoría'], ['lab', 'lab.html', 'Laboratorio'], ['equipo', 'equipo.html', 'Equipo de agentes'], ['ejercicios', 'ejercicios.html', 'Ejercicios'], ['montar', 'montar.html', 'Móntalo tú']];
  const h = document.createElement('header'); h.className = 'barra';
  h.innerHTML = '<a class="marca" href="centro.html">Mirada simulada</a><nav aria-label="Secciones">' + items.map(i => `<a href="${i[1]}"${i[0] === pag ? ' aria-current="page"' : ''}>${i[2]}</a>`).join('') + '</nav><div class="quien"></div>';
  document.body.prepend(h);
  const q = h.querySelector('.quien'); q.textContent = s.nombre;
  const b = document.createElement('button'); b.textContent = 'Salir'; b.onclick = Acceso.salir; q.append(b);
})();
