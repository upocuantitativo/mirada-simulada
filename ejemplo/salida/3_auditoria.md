# Auditoría: «Evolución de la producción» (grafico_antes.png)

## Alertas

ALERTA: «Crecimiento sostenido: +46 unidades» → el aumento 2017-2025 es +175 unidades (+500 %), y el último año +20 unidades (+10,5 %); ninguna operación con produccion.csv da 46 (210 − 35 = 175; 210 − 190 = 20; media anual 175 / 8 = 21,9).

Bloquea el paso a Power BI hasta que una persona decida qué cifra quiso mostrar el autor.

## Tabla de cifras

| Cifra | Población | Operación | Estado |
|---|---|---|---|
| 35 (2017) | Unidades anuales | CSV 2017 = 35 | Correcta |
| 50 (2018) | Unidades anuales | CSV 2018 = 50 | Correcta |
| 75 (2019) | Unidades anuales | CSV 2019 = 75 | Correcta |
| 85 (2020) | Unidades anuales | CSV 2020 = 85 | Correcta |
| 120 (2021) | Unidades anuales | CSV 2021 = 120 | Correcta |
| 140 (2022) | Unidades anuales | CSV 2022 = 140 | Correcta |
| 160 (2023) | Unidades anuales | CSV 2023 = 160 | Correcta |
| 190 (2024) | Unidades anuales | CSV 2024 = 190 | Correcta |
| 210 (2025) | Unidades anuales | CSV 2025 = 210 | Correcta |
| +46 unidades | Sin población declarada | 210 − 35 = 175; 210 − 190 = 20; 175 / 8 = 21,9; ninguna da 46 | Incorrecta |
| "Sostenido" | Serie 2017-2025 | Variaciones anuales: +15, +25, +10, +35, +20, +20, +30, +20; todas positivas, pero irregulares (2020: +10; 2021: +35) | Correcta como "sin caídas"; "sostenido" es interpretación |

Cifra acumulada que el brief dice que la audiencia no conoce: 35+50+75+85+120+140+160+190+210 = 1.065 unidades. No aparece en la pieza.

## Hallazgos

- Gravedad alta, B1.8: la cifra del mensaje (+46) no sale de los datos y no dice de qué periodo ni de qué comparación procede.
- Gravedad media, B1.9: "Crecimiento sostenido" es una interpretación presentada como hecho, sin separar el dato (todas las variaciones anuales son positivas) de la lectura. No hay causas afirmadas.
- Gravedad media, B3.1 y B3.7: línea ámbar, banda naranja, icono y cifra rojiza compiten; no hay gris por defecto ni un único énfasis.
- Gravedad media, B3.11: contraste calculado sobre los píxeles (fórmula WCAG). Texto de ejes y nota (85,85,85) sobre (253,243,228): 6,79:1. Etiquetas de datos (138,106,34): 4,59:1. Cifra «+46» (160,58,16) sobre (249,227,203): 5,43:1. Texto del KPI: 12,14:1. Todo el texto pasa 4,5:1. La línea de datos (215,161,44) sobre el fondo: 2,12:1, por debajo de 3:1 para gráficos. Texto alternativo no verificable en una imagen.
- Gravedad media, B3.15: sin subtítulo con unidad y periodo; la nota «Producción en unidades» no da fuente ni fecha de actualización.
- Gravedad baja, B3.12: el ámbar de la serie y el rojizo del KPI designan la misma magnitud con colores distintos.
- Gravedad baja, B3.14: sin anotación en 2020 (+10) ni en 2021 (+35), los puntos donde la serie cambia de ritmo.
- Gravedad baja, B3.6: banda de marca, icono de barras y rejilla añaden elementos que no aportan al mensaje.
- Eje y tipo de gráfico (B3.8, B3.9): línea para evolución, eje desde 0 a 250; sin problema.
- Sesgo de encuadre: el mensaje destaca una cifra pequeña (+46) frente a la serie, que muestra un crecimiento mayor; cuántas unidades se añadieron en total (175) y el acumulado (1.065) quedan fuera.

## Cobertura

| ID | Estado | Evidencia |
|---|---|---|
| B1.8 | No cumple | «+46 unidades» no sale de produccion.csv (175 total, 20 último año); sin subgrupos ni periodo declarado. |
| B1.9 | No cumple | «Crecimiento sostenido» se da como hecho; el dato solo muestra variaciones anuales positivas e irregulares. |
| B3.1 | No cumple | Banda naranja, línea ámbar, icono y cifra rojiza compiten por la atención. |
| B3.2 | Cumple | Cada etiqueta de dato está pegada a su punto. |
| B3.3 | No aplica | Una sola serie y un solo gráfico: no hay segundo gráfico con el que comparar el color. |
| B3.4 | Cumple | El KPI se agrupa con un fondo suave (249,227,203), sin borde. |
| B3.5 | Cumple | Una línea une los nueve puntos de la serie 2017-2025. |
| B3.6 | No cumple | Banda de marca, icono de barras y rejilla horizontal no aportan al mensaje. |
| B3.7 | No cumple | No hay gris por defecto: la serie, el icono y la cifra están en colores cálidos de acento. |
| B3.8 | Cumple | La pregunta es evolución en el tiempo y se usa un gráfico de líneas. |
| B3.9 | Cumple | Eje vertical de 0 a 250 en un gráfico de líneas, sin recortes. |
| B3.10 | No aplica | Una sola serie en un solo color: no hay paleta que clasificar. |
| B3.11 | No cumple | Texto pasa 4,5:1 (mínimo 4,59:1), pero la línea de datos da 2,12:1 sobre el fondo y no hay texto alternativo verificable. |
| B3.12 | No cumple | Ámbar (serie) y rojizo (KPI) para la misma magnitud de producción. |
| B3.13 | No aplica | Una sola serie, sin leyenda que sustituir. |
| B3.14 | No cumple | Sin anotación en 2020 (+10) ni en 2021 (+35). |
| B3.15 | No cumple | Sin subtítulo con unidad y periodo; la nota «Producción en unidades» no trae fuente ni fecha. |
| B3.16 | Cumple | Todas las cifras son enteros, sin decimales innecesarios. |
