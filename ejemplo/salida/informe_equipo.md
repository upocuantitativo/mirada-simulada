# Informe del equipo: gráfico «Evolución de la producción»

## Mensaje
El brief pide transmitir que la producción ha crecido de forma sostenida desde 2017, a la Alta Dirección (con Finanzas y Operaciones), que decide si mantiene el plan de capacidad. La pieza original no lo cumple como está escrita: su cifra destacada («+46 unidades») no sale de los datos. Con `produccion.csv`, la producción pasó de 35 (2017) a 210 (2025): +175 unidades, con subida todos los años.

## Alertas
- **Resuelta.** «+46 unidades» no se obtiene de ninguna operación sobre `produccion.csv` (aumento 2017-2025: +175; media anual 21,9; último año +20; acumulado 1.065). La persona la resolvió en A1: el mensaje pasa a +175 unidades.

## Decisiones de la persona
- Aceptados: A1 (alerta resuelta, +175), A2 («subió todos los años» en lugar de «sostenido»), A3 (fuente, corte y fecha), N1 (título de acción), M1 (Dirección no encuentra pronto el mensaje), M2 (el mensaje pasa al título), M3 (quitar la banda decorativa).
- Rechazados por ahora: A4 (datos de capacidad y demanda) y N2 (plantear la decisión sobre capacidad). Motivo: la pieza solo enseña producción; sin esos datos no se puede pedir una decisión honesta. Queda pendiente pedirlos antes del comité.
- No decididos (no figuran en la tabla): H4 y H5 de la mirada (llegada tardía en Comercial y Operaciones; la nota casi no se lee) y los hallazgos de narrativa sobre el acumulado de 1.065 y el BLUF.

## Cambios aprobados
Los cambios 1 a 7 de `4_mejora.md` derivan de hallazgos aceptados: cifra +175, «subió todos los años», título de acción con el mensaje («La producción subió todos los años entre 2017 y 2025: de 35 a 210 unidades, +175»), línea de fuente/corte/fecha, banda fuera, foco en la serie y eje con unidad. Los pasos de Power BI (modelo, medidas con cifra de control, título dinámico, accesibilidad y publicación) están en `5_powerbi.md`. Nada se ha ejecutado en Power BI.

## Prueba A/B
Versión A (`grafico_antes.png`) frente a versión B (con los cambios), mismo comité de 30 personas simuladas (Dirección 10, Finanzas 8, Comercial 5, Operaciones 5, Analista 2) y semilla 2026. Métricas que se espera que mejoren: M1 (Dirección hoy 70 %), M2 (hoy 4009 ms) y M3 en Operaciones (hoy 11,8 % en decoración). Sin promesa de cuánto.

## Qué queda sin resolver
- Fuente, periodo de corte y fecha de extracción: [DATO PENDIENTE] del autor.
- Nombre de la tabla de fechas, si se añade una: [NOMBRE PENDIENTE]. Con `Anio` entero no hace falta.
- Conflictos de `4_mejora.md` por decidir: (1) título solo con el hecho o con una implicación suave, dado que N2 está rechazado; (2) eliminar o conservar el recuadro del mensaje; (3) si se añade el acumulado 1.065.
- Datos de capacidad y demanda (A4): sin ellos la pieza no dice qué implica para el plan de capacidad, y la serie creciente por sí sola no prueba que el plan actual sea adecuado.
- Los umbrales M1 a M4 son reglas de trabajo del curso. Con M4 el informe de la mirada dejó el umbral pendiente; `CRITERIOS.md` fija el 50 % y el valor global es 0,633, aunque en Analista (0,333) y Comercial (0,467) queda por debajo.
- Límites de la simulación: no es una medición, los perfiles pequeños tienen intervalos anchos, y no dice si el mensaje se entiende ni si cambia la decisión. Falta la prueba con personas reales (al menos 20, 5 o más por perfil).
- No se ha verificado qué entra en «producción» (plantas, líneas) ni si 2025 es año completo.

La IA ha propuesto; las decisiones de esta tabla las ha tomado Docente de la microcredencial (ejemplo).
