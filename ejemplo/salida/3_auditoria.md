# Auditoría de integridad: «Evolución de la producción»

## Alertas

ALERTA: «Crecimiento sostenido: +46 unidades» → el aumento 2017-2025 es +175 unidades (210 − 35), una media de +21,9 unidades por año (175 / 8), y el último año +20 (210 − 190). Ninguna operación sobre `produccion.csv` da 46. Alerta bloqueante: no pasa a Power BI hasta que una persona la resuelva.

## Tabla de cifras

| Cifra | Población | Operación | Estado |
|---|---|---|---|
| 35 (2017) | Unidades producidas, año 2017 | CSV: 2017;35 | Correcta |
| 50 (2018) | Unidades, 2018 | CSV: 2018;50 | Correcta |
| 75 (2019) | Unidades, 2019 | CSV: 2019;75 | Correcta |
| 85 (2020) | Unidades, 2020 | CSV: 2020;85 | Correcta |
| 120 (2021) | Unidades, 2021 | CSV: 2021;120 | Correcta |
| 140 (2022) | Unidades, 2022 | CSV: 2022;140 | Correcta |
| 160 (2023) | Unidades, 2023 | CSV: 2023;160 | Correcta |
| 190 (2024) | Unidades, 2024 | CSV: 2024;190 | Correcta |
| 210 (2025) | Unidades, 2025 | CSV: 2025;210 | Correcta |
| +46 unidades | No declarada (¿periodo? ¿total?) | Aumento total 210 − 35 = 175; media anual 175 / 8 = 21,875; variaciones anuales 15, 25, 10, 35, 20, 20, 30, 20 (ninguna es 46); suma de la serie 1065 | Incorrecta |
| Ejes 0-250 | Escala del eje Y | Rango de datos 35-210, entra en la escala | Correcta |

## Hallazgos

1. **B1.5, B1.6 (crítica).** La cifra del recuadro destacado, que es el mensaje principal, no se corresponde con los datos. Tampoco dice a qué población ni periodo se refiere (¿total 2017-2025, un año, media?). La Alta Dirección decide sobre capacidad con una cifra que no sale de la serie.
2. **B1.6 (alta).** «Sostenido» es una interpretación, no un hecho mostrado. Los datos la respaldan en cuanto a que no hay ningún año a la baja, pero el crecimiento no es uniforme: 2020 sube solo +10 y 2021 sube +35. No hay causa afirmada, pero tampoco se explica qué hay detrás de esos saltos.
3. **B1.5 (media).** No se indica si 2025 es año completo ni qué entra en «producción» (todas las plantas, líneas o productos). Es no verificable con lo entregado. Esto importa porque Operaciones y Finanzas leerán la cifra con comparables distintos.
4. **B2.6 (media).** El título «Evolución de la producción» es una etiqueta, no dice qué pasó ni qué implica para el plan de capacidad.
5. **B3.6 (baja).** Eje Y desde 0, línea y una sola serie: escala honesta, sin doble eje. El tipo de gráfico (línea para evolución) es adecuado a la pregunta (B3.5).
6. **Fuente, unidad y fecha (media).** Solo figura «Producción en unidades». Falta la fuente, el periodo de corte y la fecha de extracción. La unidad no aparece en el eje ni en el título.
7. **B3.7 (media, estimado a ojo, sin medir píxeles).** Las etiquetas de valor, de color ocre sobre fondo crema y de tamaño pequeño, parecen quedar por debajo de 4,5:1. El texto del recuadro (rojo oscuro sobre melocotón) probablemente cumple. La información no depende solo del color: los valores están rotulados. No hay texto alternativo comprobable en un PNG.
8. **B3.3 (baja).** Rejilla horizontal y etiquetas en todos los puntos: aceptable, pero el icono de barras del recuadro es decorativo y sugiere un gráfico de barras que no existe.
9. **Sesgos.** Encuadre: la palabra «sostenido» junto a una cifra errónea refuerza la lectura favorable. Omisión: no se muestra ningún dato de capacidad ni demanda, que es lo que la decisión (mantener o no el plan de capacidad) requiere. Una serie creciente por sí sola no prueba que el plan actual sea adecuado.
