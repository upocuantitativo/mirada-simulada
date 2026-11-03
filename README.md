# Mirada simulada

Laboratorio web de atención simulada de la microcredencial «Visualización y narrativa de datos con Power BI» (UPO · FP-UNA).

Sube un gráfico, panel, informe o web, elige un comité (Alta Dirección, Comercial, Finanzas, Analista, Operaciones) y obtén mapa de calor, recorrido de la mirada y métricas por audiencia. Después, un equipo de cinco agentes de IA revisa la pieza con los criterios del Módulo 1 y con validación humana.

**Es una simulación didáctica, no un registro ocular.** No está calibrada con datos humanos; los tiempos y pesos de cada audiencia son supuestos del curso. Sirve para comparar versiones de un diseño, no para validarlo.

## Publicar tu copia

Haz fork y activa GitHub Pages: Settings, Pages, Deploy from a branch, `main`, `/ (root)`. No hay servidor ni base de datos, y las imágenes no salen del navegador. Guía completa en `montar.html`.

## Estructura

| Ruta | Contenido |
|---|---|
| `js/motor.js` | Saliencia, recorridos, métricas y audiencias (`PERSONAS`) |
| `data/instrumento.json` | Error del aparato calculado con PyEtSimul |
| `casos/`, `data/casos.json` | Casos de ejemplo y sus zonas |
| `.claude/agents/`, `.claude/skills/revisar-visual/` | Equipo de agentes para Claude Code |
| `modulo1/CRITERIOS.md` | Conceptos del Módulo 1 que aplican los agentes |
| `ejemplo/` | Ejecución real del equipo sobre el gráfico de producción |
| `tools/` | Generadores y prueba de extremo a extremo |

## Base científica y créditos

Residuo espectral (Hou y Zhang, 2007), contraste centro-periferia (Itti et al., 1998), influencia de la tarea (Yarbus, 1967) y sesgo central (Tatler, 2007). La capa de instrumento usa resultados de [PyEtSimul](https://github.com/mh-salari/pyetsimul) (GPL-3.0); su código no se incluye aquí, solo se ejecuta en `tools/`. Las cifras de Road Bikes son un escenario docente, no datos nativos de Adventure Works.

Licencia MIT para el código de este repositorio.
