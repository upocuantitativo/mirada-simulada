# Mejora: gráfico «Evolución de la producción»

Trabajo solo con los hallazgos aceptados en `decisiones.md`: A1, A2, A3, N1, M1, M2, M3. No entran A4 ni N2 (rechazados por ahora): no se pide ninguna decisión sobre capacidad ni se añade capacidad o demanda. Tampoco entran H4 ni H5 de la mirada ni los hallazgos de narrativa 5 y 7 (acumulado, BLUF), que no figuran en la tabla de decisiones.

## Tabla priorizada

| Prioridad | Cambio | Hallazgo | Criterio | Impacto | Esfuerzo |
|---|---|---|---|---|---|
| 1 | Sustituir el recuadro «Crecimiento sostenido: +46 unidades» por la cifra real: +175 unidades (210 − 35, `produccion.csv`, 2017-2025). Corrige un error de datos. | A1 | B1.5, B1.6 | Alto: la cifra que ve Dirección deja de ser falsa | Bajo |
| 2 | Quitar «sostenido» de todo el texto y escribir «subió todos los años», que es un hecho (ningún año baja). | A2 | B1.6 | Alto: separa hecho de interpretación | Bajo |
| 3 | Reemplazar el título-etiqueta por un título de acción que lleve el mensaje (ver Títulos nuevos). El mensaje pasa al título y se elimina el recuadro como segundo mensaje. | N1, M2, M1 | B2.6, B2.2, M1, M2 | Alto: el título recibe hoy el 64,9 % del tiempo de Dirección y llega a 21 ms; con el mensaje dentro, la atención va al mensaje | Bajo |
| 4 | Añadir bajo el título una línea con unidad, fuente, periodo de corte y fecha de extracción. Datos de fuente, corte y fecha: [DATO PENDIENTE] del autor. | A3 | B1.5 | Medio | Bajo (el dato depende del autor) |
| 5 | Quitar la banda «APLICANDO / Antes / Después». Es de la plantilla de clase y no aporta. | M3 | B3.3, M3 | Bajo en el comité global (7,1 %), pero en Operaciones pasa del 10 % (11,8 %) | Bajo |
| 6 | Dar foco a la serie: línea en un solo color con contraste, etiquetas solo en 2017 y 2025 (35 y 210), resto en gris o sin etiqueta, y una anotación directa «+175 unidades». Se quita el icono de barras del recuadro, que sugiere un gráfico que no existe. | M1, M2 (apoyo) | B3.1, B3.3, B3.4, B3.8 | Medio: ayuda a que la mirada llegue al mensaje | Medio |
| 7 | Rotular el eje Y con la unidad («Unidades producidas») y mantener el eje desde 0. | A3 | B3.6 | Bajo | Bajo |

Cada cambio se puede deshacer (la versión original se conserva como versión A) y se explica a la audiencia con una frase: «el número ahora sale de los datos» (1), «solo afirmamos lo que se ve» (2), «el título dice lo que pasó» (3).

El cambio 6 va más allá de lo aceptado en M1/M2 (es una consecuencia de B3.4). Si la persona lo considera excesivo, se puede aplicar solo del 1 al 5 y el 7.

## Títulos nuevos

- **Título principal (propuesta):** «La producción subió todos los años entre 2017 y 2025: de 35 a 210 unidades, +175».
- **Subtítulo:** «Unidades producidas por año. Fuente: [DATO PENDIENTE]. Datos hasta [DATO PENDIENTE: corte y fecha de extracción].»
- **Anotación sobre la serie:** «+175 unidades (2017-2025)».

El título no dice qué implica para el plan de capacidad: esa implicación depende de datos de capacidad que no se tienen (A4 y N2, rechazados por ahora). Si más adelante se aceptan, el título pasaría a completarse con la consecuencia.

## Conflictos por decidir

1. **Título de acción frente a lo rechazado en N2.** B2.6 pide que el título diga qué pasó y qué implica. La persona ha rechazado plantear la decisión sobre capacidad. Opciones: (a) título solo con el hecho, como arriba (coherente con lo decidido, cumple B2.6 a medias); (b) añadir una implicación suave sin cifras de capacidad, por ejemplo «…; falta contrastarlo con la capacidad instalada» (honesta, pero introduce un pendiente en el título). Recomendación: (a), hasta tener los datos. Decide la persona.
2. **Qué hacer con el recuadro del mensaje.** M2 acepta que título y mensaje sean lo mismo. Opciones: (a) eliminar el recuadro (menos elementos, una sola zona de mensaje); (b) conservarlo con «+175 unidades» como refuerzo (Finanzas lo encuentra al 100 % en el KPI actual, así que se perdería algo en esa audiencia). El informe de la mirada no resuelve cuál funciona mejor; es lo que mide la prueba A/B. Decide la persona.
3. **Cifra a destacar.** A1 fija +175 (aumento total). Los datos permiten también 1.065 (acumulado) y +20 (último año). Narrativa señaló que la audiencia no conoce el acumulado, pero esa cifra no está en las decisiones. No se incluye. Decide la persona si se añade.

## Prueba A/B

- **Versión A:** `grafico_antes.png`, sin cambios.
- **Versión B:** gráfico con los cambios 1 a 7 y la opción elegida en los conflictos 1 y 2.
- **Comité y semilla:** el mismo en las dos versiones: Dirección 10, Finanzas 8, Comercial 5, Operaciones 5, Analista 2 (30 personas simuladas) y semilla 2026. Las zonas se redefinen en B (el mensaje es el título y la anotación) y se anota qué zona cuenta como mensaje en cada versión.
- **Métricas que esperaría que mejoren:** M1 (proporción de Dirección que mira el mensaje, hoy 70 %), M2 (primera mirada al mensaje, hoy 4009 ms) y M3 en Operaciones (tiempo en decoración, hoy 11,8 %). Sin promesa de cuánto.
- **Límite:** una simulación con 30 personas es un indicio; los perfiles pequeños tienen intervalos anchos. Validarlo exige personas reales: al menos 20 en total y 5 o más por perfil, con prueba de cinco segundos y pregunta de recuerdo del mensaje («¿cuánto ha subido la producción y entre qué años?»).
