# Mejora: «Evolución de la producción» (grafico_antes.png)

Se trabaja solo con los hallazgos marcados como aceptados en `decisiones.md`. Los rechazados por ahora quedan fuera de este documento: faltan datos de capacidad y demanda.

Cifra del mensaje: la ALERTA de la auditoría está resuelta por la persona. El mensaje pasa a +175 unidades (210 − 35, de 2017 a 2025), comprobado en `produccion.csv`.

## Tabla priorizada

| Prioridad | Cambio | Hallazgo | Criterio | Impacto | Esfuerzo |
|---|---|---|---|---|---|
| 1 | Sustituir «+46 unidades» por «+175 unidades» en el recuadro del mensaje y fijar periodo (2017-2025) y comparación (2025 frente a 2017). | B1.8 | B1.8 El titular evidente | Alto: corrige un error de datos | Bajo |
| 2 | Separar hecho e interpretación: hecho «La producción subió cada año, de 35 a 210 unidades»; la lectura («sostenido») va en frase aparte y marcada como interpretación. | B1.9 | B1.9 Hecho, interpretación e hipótesis | Alto | Bajo |
| 3 | Sustituir el título-etiqueta por el título de acción nuevo (ver más abajo). | B2.9 | B2.9 Título de acción | Alto | Bajo |
| 4 | Convertir el recuadro inferior en una Big Idea de frase completa, sin cifra inventada: «La producción se multiplicó por seis entre 2017 y 2025 (+175 unidades)». | B2.3 | B2.3 Big Idea | Alto | Bajo |
| 5 | Poner la respuesta arriba (título) y dos argumentos debajo: volumen (35 a 210) y ritmo (+10 en 2020, +35 en 2021); la serie queda como evidencia al fondo. | B2.5 | B2.5 Pirámide de Minto | Medio | Medio |
| 6 | Dejar un único énfasis: serie y cifra en el mismo acento; el resto en gris. | B3.1 | B3.1 Atributos preatentivos | Alto | Bajo |
| 7 | Gris por defecto para icono, nota y puntos no destacados; acento solo para la serie y los dos hitos anotados. | B3.7 | B3.7 Foco | Alto | Bajo |
| 8 | Un solo color para la magnitud de producción (serie y cifra del mensaje). | B3.12 | B3.12 Un color, un significado | Medio | Bajo |
| 9 | Quitar la banda «Aplicando», el icono de barras y la rejilla horizontal. | B3.6 | B3.6 Desorden y carga cognitiva | Medio | Bajo |
| 10 | Oscurecer la línea de datos hasta superar 3:1 sobre el fondo, mantener el texto sobre 4,5:1 y añadir texto alternativo al visual. | B3.11 | B3.11 Daltonismo y contraste | Medio | Bajo |
| 11 | Anotar 2020 («+10, menor aumento anual») y 2021 («+35, mayor aumento anual»). | B3.14 | B3.14 Anotación | Medio | Bajo |
| 12 | Añadir subtítulo «Unidades producidas por año, 2017-2025» y pie «Fuente: produccion.csv. Actualizado: [FECHA PENDIENTE]». | B3.15 | B3.15 Subtítulo, fuente y fecha | Medio | Bajo |
| 13 | Mover el mensaje a la zona superior izquierda, junto al título, y bajar el peso visual del título (el mensaje recibe el 12,1 % del tiempo; el título, el 41,2 %). | M1 | M1 Encuentra el mensaje | Alto | Bajo |
| 14 | Hacer la cifra más grande y colocarla antes de la serie para acortar el recorrido hasta ella (primera mirada a 4009 ms). | M2 | M2 Pronto | Alto | Bajo |
| 15 | Dar a la pieza una secuencia de tres páginas: 1) crecimiento acumulado, 2) ritmo anual con hitos, 3) anexo con la serie completa. Una idea, un título y un gráfico por página. | B2.11 | B2.11 Storyboard | Medio | Alto |
| 16 | Hacer que los títulos de las tres páginas, leídos seguidos, formen el resumen ejecutivo. | B2.10 | B2.10 Titles test | Medio | Medio |
| 17 | Añadir arco: contexto (la producción ha crecido, ya sabido), hallazgo (+175 y ritmo irregular) y cierre con lo que el comité ya sabe; lo que falta de la resolución queda pendiente de datos. | B2.1 | B2.1 Arco narrativo | Medio | Medio |
| 18 | Elegir una perla (el aumento acumulado de 175 unidades) y llevar el detalle anual al anexo. | B1.2 | B1.2 Explicar, no explorar | Medio | Medio |
| 19 | Unir datos, narrativa y visual: título que explica, anotación que ilumina, un solo acento que engancha. | B1.3 | B1.3 Tres elementos | Medio | Medio |

Primero van los cambios que corrigen datos (1 y 2), luego los que cambian el mensaje y por último el diseño.

## Títulos nuevos

Todas las cifras salen de `produccion.csv`.

- Página 1: «La producción se multiplicó por seis entre 2017 y 2025: de 35 a 210 unidades (+175)».
- Página 2: «El aumento anual fue irregular: +10 unidades en 2020 y +35 en 2021, sin caídas en ningún año».
- Página 3 (anexo): «Producción anual de 2017 a 2025, en unidades».
- Recuadro del mensaje: «+175 unidades entre 2017 y 2025».

Los títulos no afirman nada sobre capacidad ni demanda, que no están en los datos.

## Conflictos por decidir

- Dirección quiere menos elementos y el Analista busca la serie con detalle (49,1 % de su tiempo en la serie). Opción A: una página con serie y dos anotaciones. Opción B: página 1 solo con el mensaje y serie completa en el anexo. Decide la persona.
- El título largo ayuda a Dirección, pero compite con el mensaje en tiempo de mirada. Opción A: título de dos líneas y mensaje debajo. Opción B: título corto en la cabecera y la frase completa dentro del recuadro. Decide la persona.
- Estas elecciones deben cerrarse antes de la prueba A/B.

## Prueba A/B

- Versión A: `grafico_antes.png`, sin cambios.
- Versión B: la pieza con los cambios 1 a 14 aplicados (cifra corregida, título de acción, un acento, anotaciones, mensaje arriba). Los cambios de storyboard y arco (15 a 19) se prueban aparte.
- Comité y semilla: el mismo comité del informe de mirada (Dirección 10, Comercial 5, Finanzas 8, Analista 2, Operaciones 5; 30 personas simuladas) y la misma semilla, 2026, para que la diferencia venga de la pieza y no del muestreo.
- Métricas que se espera que mejoren: porcentaje que mira el mensaje (M1), tiempo hasta la primera mirada al mensaje (M2) y proporción del tiempo en el mensaje frente al título. No se promete cuánto.
- Límite: es una simulación, no una medición; los umbrales son reglas de trabajo del curso. Validar exige seguimiento ocular con personas reales de Dirección, Finanzas y Operaciones.
- Cada cambio se puede deshacer: la versión A se conserva y los cambios son independientes entre sí en la tabla.
