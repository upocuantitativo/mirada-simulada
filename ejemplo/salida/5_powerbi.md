# Despliegue en Power BI: «Evolución de la producción»

No hay fichero .pbix. Este documento son instrucciones para que las aplique una persona; no se ha ejecutado nada en Power BI.

La ALERTA de la auditoría sobre «+46» está resuelta en `decisiones.md` (B1.8): el mensaje es +175 unidades (210 − 35), comprobado en `produccion.csv`. Se escriben, por tanto, los pasos. Se consideran aprobados los cambios de los hallazgos aceptados de `4_mejora.md`.

Datos: `produccion.csv`, separador «;», columnas Anio y Unidades (9 filas, 2017 a 2025). Tabla del brief: Produccion, columnas Anio y Unidades.

## Pasos

### Power Query y modelo
1. Inicio > Obtener datos > Texto/CSV > `produccion.csv`, delimitador punto y coma. Elegir Transformar datos.
2. Nombrar la consulta `Produccion`. Tipos: Anio = Número entero; Unidades = Número entero. Comprobar 9 filas, sin vacías ni duplicados.
3. Añadir la columna `Fecha` = `#date([Anio], 12, 31)` (tipo Fecha); el dato es anual y se fija al 31 de diciembre.
4. Crear la tabla de fechas (Modelado > Nueva tabla): `Calendario = ADDCOLUMNS ( CALENDAR ( DATE ( 2017, 1, 1 ), DATE ( 2025, 12, 31 ) ), "Anio", YEAR ( [Date] ) )`.
5. Herramientas de tabla > Marcar como tabla de fechas > columna `Date`.
6. Relacionar `Produccion[Fecha]` con `Calendario[Date]` (muchos a uno, filtro en una dirección). Ocultar `Fecha` y `Date` de la vista de informe.

### Medidas DAX
Crear en la tabla `Produccion`. Cifras de control con todos los años seleccionados salvo que se indique.

7. `Unidades totales = SUM ( Produccion[Unidades] )`. Control: 1.065 (35+50+75+85+120+140+160+190+210).
8. `Unidades ultimo anio = CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MAX ( Produccion[Anio] ) )`. Control: 210 (2025).
9. `Unidades primer anio = CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MIN ( Produccion[Anio] ) )`. Control: 35 (2017).
10. `Aumento acumulado = [Unidades ultimo anio] - [Unidades primer anio]`. Control: 175 (210 − 35). Es la cifra del mensaje y sustituye a +46.
11. `Veces que se multiplica = DIVIDE ( [Unidades ultimo anio], [Unidades primer anio] )`. Control: 6,0 (210 / 35).
12. `Aumento anual = SUM ( Produccion[Unidades] ) - CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MAX ( Produccion[Anio] ) - 1 )`, pensada para un solo año en contexto. Control: 2025 da 20 (210 − 190); 2020 da 10 (85 − 75); 2021 da 35 (120 − 85).
13. `Aumento anual medio = DIVIDE ( [Aumento acumulado], DISTINCTCOUNT ( Produccion[Anio] ) - 1 )`. Control: 21,875 (175 / 8), que se muestra como 21,9.
14. `Anios con caida = COUNTROWS ( FILTER ( VALUES ( Produccion[Anio] ), Produccion[Anio] > MIN ( Produccion[Anio] ) && [Aumento anual] < 0 ) )`. Control: 0 (las variaciones 2018 a 2025 son +15, +25, +10, +35, +20, +20, +30, +20).

### Visuales
15. Página 1 «Crecimiento acumulado». Tarjeta con `Aumento acumulado`. Formato: Valor de llamada con fuente 40 pt y el color de acento único; Etiqueta de categoría «unidades entre 2017 y 2025»; título del visual desactivado (el título va en el cuadro de texto de la página). Posición: arriba a la izquierda, junto al título.
16. Página 1. Gráfico de líneas: Eje X = `Produccion[Anio]` (sin agregar); Eje Y = `Unidades totales`. Formato: Eje X con título desactivado; Eje Y con inicio 0 y máximo 250; rejilla desactivada; Líneas con el acento (contraste mínimo 3:1 sobre el fondo) y grosor 3; Marcadores activados; Etiquetas de datos activadas con contraste mínimo 4,5:1; Leyenda desactivada (una sola serie); Título con subtítulo «Unidades producidas por año, 2017-2025».
17. Página 1. Cuadro de texto al pie: «Fuente: produccion.csv. Actualizado: [FECHA PENDIENTE]».
18. No recrear la banda, el icono de barras ni la rejilla. Usar solo gris por defecto y un acento, el mismo para serie y tarjeta.
19. Anotaciones: dos cuadros de texto junto a los puntos 2020 («+10, menor aumento anual») y 2021 («+35, mayor aumento anual»). Si se mueve el visual hay que recolocarlos.
20. Página 2 «Ritmo anual». Gráfico de columnas agrupadas: Eje X = `Anio`; Eje Y = `Aumento anual`, desde 0. Columnas en gris; 2020 y 2021 con el acento (Formato > Columnas > Colores por punto de datos). Control: 2018 +15, 2019 +25, 2020 +10, 2021 +35, 2022 +20, 2023 +20, 2024 +30, 2025 +20.
21. Página 3 «Anexo». Tabla con `Anio` y `Unidades totales`, 9 filas y total al pie de 1.065.

### Títulos dinámicos
22. Crear la medida:
`Titulo pagina 1 = IF ( HASONEVALUE ( Produccion[Anio] ), "Producción de " & VALUES ( Produccion[Anio] ) & ": " & FORMAT ( [Unidades totales], "#,##0" ) & " unidades", "La producción pasó de " & [Unidades primer anio] & " a " & [Unidades ultimo anio] & " unidades entre " & MIN ( Produccion[Anio] ) & " y " & MAX ( Produccion[Anio] ) & " (+" & [Aumento acumulado] & ")" )`
Es cierta en todos los estados de filtro: con un año muestra ese año y su total; con varios, el primero y el último del rango filtrado y su diferencia real. No repite «se multiplicó por seis», que solo vale para el rango completo.
23. Aplicarla: Título > fx > Valor de campo > `Titulo pagina 1`.
24. Controles: sin filtro, «La producción pasó de 35 a 210 unidades entre 2017 y 2025 (+175)»; con 2020, «Producción de 2020: 85 unidades»; con 2017 a 2021, aumento 85 (120 − 35) y factor 3,43 (120 / 35).

### Accesibilidad
25. Texto alternativo (Formato > General > Texto alternativo):
   - Tarjeta: «Aumento de la producción entre 2017 y 2025: 175 unidades.»
   - Gráfico de líneas: «Gráfico de líneas de la producción anual en unidades, de 35 en 2017 a 210 en 2025. Sube cada año; el menor aumento es en 2020 (+10) y el mayor en 2021 (+35).»
   - Gráfico de columnas: «Aumento anual de la producción en unidades: 15, 25, 10, 35, 20, 20, 30 y 20 entre 2018 y 2025.»
   - Tabla: «Tabla de producción anual de 2017 a 2025 con total de 1.065 unidades.»
26. Orden de tabulación (Vista > Panel de selección): título, tarjeta, gráfico de líneas, anotaciones, pie. Lo decorativo se marca como tal o no existe.
27. Tema de contraste (Vista > Temas > Personalizar): texto mínimo 4,5:1 y colores de gráfico mínimo 3:1. Nada va solo por color: las anotaciones llevan texto y signo.

### Arquitectura (B2.12)
28. Tres páginas en el orden de la historia, no en el orden de construcción: Crecimiento acumulado, Ritmo anual, Anexo.
29. Marcadores «Todo el periodo» (sin filtros) y «Desde 2021» (años 2021 a 2025), y botones de navegación entre páginas arriba a la izquierda con texto alternativo («Ir a ritmo anual», etc.).
30. Los títulos de las tres páginas, leídos seguidos, forman el resumen ejecutivo (ver `4_mejora.md`).

### Publicación y seguimiento
31. Publicar en un área de trabajo de revisión y compartir primero con quien decide: Alta Dirección, con Finanzas y Operaciones como audiencias secundarias. Responsable de publicar: [NOMBRE PENDIENTE].
32. Tras publicar: comprobar que las medidas dan las cifras de control, que el título dinámico es cierto con filtros por año y que los textos alternativos se leen bien con lector de pantalla.
33. Comprobar con personas reales: seguimiento ocular con miembros de Dirección, Finanzas y Operaciones, con la tarea «decidir si se mantiene el plan de capacidad». La simulación no sustituye esta prueba.

## Cifras de control (resumen)

| Medida | Estado de filtro | Valor esperado |
|---|---|---|
| Unidades totales | 2017 a 2025 | 1.065 |
| Unidades primer anio | 2017 a 2025 | 35 |
| Unidades ultimo anio | 2017 a 2025 | 210 |
| Aumento acumulado | 2017 a 2025 | 175 |
| Veces que se multiplica | 2017 a 2025 | 6,0 |
| Aumento anual | 2025 / 2020 / 2021 | 20 / 10 / 35 |
| Aumento anual medio | 2017 a 2025 | 21,9 (21,875) |
| Anios con caida | 2017 a 2025 | 0 |

## Lista de comprobación final
- [ ] Tabla `Produccion` con 9 filas y Anio/Unidades enteros.
- [ ] `Calendario` marcada como tabla de fechas y relacionada.
- [ ] Todas las medidas dan sus cifras de control.
- [ ] El mensaje dice +175, no +46.
- [ ] Un solo acento, resto en gris; sin banda, icono ni rejilla.
- [ ] Eje Y desde 0.
- [ ] Anotaciones en 2020 y 2021; subtítulo, fuente y fecha (la fecha sigue pendiente).
- [ ] Título dinámico cierto con y sin filtros.
- [ ] Textos alternativos, orden de tabulación y tema de contraste aplicados.
- [ ] Prueba con personas reales programada.

## Cobertura

| ID | Estado | Evidencia |
|---|---|---|
| B2.12 | Cumple | Pasos 28 a 30: tres páginas (Crecimiento acumulado, Ritmo anual, Anexo), marcadores «Todo el periodo» y «Desde 2021» y navegación en el orden de la historia. |
