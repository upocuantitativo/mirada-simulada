# Power BI: pasos para aplicar los cambios aprobados

Estado de la alerta: la ALERTA de `3_auditoria.md` («+46 unidades») está resuelta en `decisiones.md` (A1: el mensaje pasa a +175, comprobado en `produccion.csv`). Se puede continuar.

Alcance: cambios de `4_mejora.md` derivados de A1, A2, A3, N1, M1, M2 y M3. Quedan fuera A4 y N2 (rechazados): no hay medidas ni visuales de capacidad o demanda. Esto son instrucciones para que las aplique una persona; no se ha ejecutado nada en Power BI.

Tabla y columnas (brief): tabla `Produccion`, columnas `Anio` y `Unidades`. Tabla de fechas: [NOMBRE PENDIENTE]; `Anio` es un número de año, no una fecha.

## Pasos

### 1. Power Query y modelo
1. Inicio > Transformar datos > Origen: `produccion.csv`, delimitador punto y coma. Primera fila como encabezados. Nombre de la consulta: `Produccion`.
2. Tipos: `Anio` como número entero, `Unidades` como número entero. Comprobar que hay 9 filas (2017 a 2025) y ninguna vacía ni duplicada.
3. Cerrar y aplicar.
4. Vista de modelo: con una sola tabla no hay relaciones que crear. Como `Anio` es un entero y no una fecha, no se puede marcar como tabla de fechas. Si se añade más adelante una tabla de calendario con granularidad mayor al año, su nombre es [NOMBRE PENDIENTE] y se marcaría como tabla de fechas; no es necesario para este panel.
5. En `Produccion[Anio]`: Resumen = No resumir (para que el eje X no lo sume). En `Produccion[Unidades]`: formato número entero, separador de miles.

### 2. Medidas DAX
Crear en la tabla `Produccion` (Inicio > Nueva medida). Las cifras de control se comprueban con el filtro vacío (2017-2025) y están calculadas sobre `produccion.csv`.

**M1. Unidades totales**
```
Unidades totales = SUM ( Produccion[Unidades] )
```
Control: 1065.

**M2. Año inicial y año final**
```
Anio inicial = MIN ( Produccion[Anio] )
Anio final   = MAX ( Produccion[Anio] )
```
Control: 2017 y 2025.

**M3. Unidades en el año inicial y final**
```
Unidades inicial =
CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = [Anio inicial] )

Unidades final =
CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = [Anio final] )
```
Control: 35 y 210.

**M4. Aumento entre el año inicial y el final**
```
Aumento unidades = [Unidades final] - [Unidades inicial]
```
Control: 175 (es el valor que sustituye a «+46»; 210 − 35).

**M5. Años con bajada** (para que «subió todos los años» sea verdad en cualquier filtro)
```
Anios con bajada =
VAR _anios = VALUES ( Produccion[Anio] )
RETURN
SUMX (
    _anios,
    VAR _a = Produccion[Anio]
    VAR _actual = CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = _a )
    VAR _previo =
        CALCULATE (
            SUM ( Produccion[Unidades] ),
            REMOVEFILTERS ( Produccion[Anio] ),
            Produccion[Anio] = _a - 1
        )
    RETURN
        IF ( ( _a - 1 ) IN _anios && _actual < _previo, 1, 0 )
)
```
Control: 0 con 2017-2025. Con el filtro 2020-2022 también 0.
Nota: solo compara cada año con el anterior si ese año anterior también está en el filtro; si se seleccionan años no consecutivos no inventa comparaciones.

**M6. Número de años en el filtro**
```
Anios en filtro = DISTINCTCOUNT ( Produccion[Anio] )
```
Control: 9.

### 3. Título dinámico
El mensaje depende del filtro de años, así que el título es una medida. Es cierto en todos los estados: afirma «subió todos los años» solo si no hay bajadas y hay al menos 2 años; con un solo año no compara; si hay alguna bajada, no afirma subida.

```
Titulo mensaje =
VAR _n = [Anios en filtro]
VAR _ini = [Anio inicial]
VAR _fin = [Anio final]
VAR _u0 = [Unidades inicial]
VAR _u1 = [Unidades final]
VAR _dif = [Aumento unidades]
RETURN
SWITCH (
    TRUE (),
    _n = 0, "Sin datos para el filtro elegido",
    _n = 1, "En " & _ini & " la producción fue de " & _u1 & " unidades",
    [Anios con bajada] = 0,
        "La producción subió todos los años entre " & _ini & " y " & _fin
            & ": de " & _u0 & " a " & _u1 & " unidades, +" & _dif,
    "La producción pasó de " & _u0 & " a " & _u1 & " unidades entre " & _ini & " y " & _fin
            & " (" & IF ( _dif >= 0, "+", "" ) & _dif & "), con al menos un año a la baja"
)
```
Control: con 2017-2025 devuelve «La producción subió todos los años entre 2017 y 2025: de 35 a 210 unidades, +175». Con un solo año (2021) devuelve «En 2021 la producción fue de 120 unidades».
Límite: si hay años no consecutivos en el filtro, «entre X e Y» describe los extremos del filtro, no de los años intermedios no incluidos.

Subtítulo (fuente, corte y fecha; A3):
```
Subtitulo =
"Unidades producidas por año. Fuente: [DATO PENDIENTE]. Datos hasta [DATO PENDIENTE: corte y fecha de extracción]."
```
Los textos pendientes los completa el autor; no se inventan. El subtítulo no depende del filtro, pero se deja como medida para poder cambiarlo en un solo sitio.

Anotación sobre la serie: usar `"+" & [Aumento unidades] & " unidades (" & [Anio inicial] & "-" & [Anio final] & ")"`. Control: «+175 unidades (2017-2025)».

### 4. Visuales (orden del panel Formato)
Lienzo: 16:9. Sin banda de plantilla (M3) y sin recuadro con icono de barras (M2; conflicto 2 de `4_mejora.md` pendiente: si la persona decide conservar un recuadro, usar una tarjeta con `[Aumento unidades]`).

**Visual 1: gráfico de líneas**
- Campos: Eje X = `Produccion[Anio]`; Eje Y = `Unidades totales`. Sin leyenda, sin eje secundario.
- Pestaña Visual:
  1. Eje X: tipo categórico, título oculto (los años se explican solos).
  2. Eje Y: inicio fijo en 0, título «Unidades producidas» (cambio 7, B3.6).
  3. Cuadrícula: horizontal muy suave o desactivada (B3.3).
  4. Líneas: un solo color de contraste alto (B3.7); marcadores en 2017 y 2025.
  5. Etiquetas de datos: solo en 2017 y 2025 (35 y 210), resto desactivadas (cambio 6; B3.4).
  6. Anotación: cuadro de texto sobre la serie con la medida de anotación.
- Pestaña General: Título activado con fx > formato de campo > `Titulo mensaje`; Subtítulo con fx > `Subtitulo`; texto alternativo (ver abajo).

**Visual 2 (opcional, solo si se decide conservar el recuadro):** tarjeta con `Aumento unidades`, etiqueta «unidades entre 2017 y 2025». No se crea por defecto.

### 5. Accesibilidad
- Tema: Vista > Temas > personalizado con texto oscuro sobre fondo claro y relación de contraste de 4,5:1 como mínimo en texto (B3.7). Las etiquetas ocre sobre crema del original parecían quedar por debajo; comprobar con un medidor de contraste, no a ojo.
- Información no solo por color: título, anotación y etiquetas dicen la cifra con texto.
- Orden de tabulación (Vista > Panel de selección > Orden de tabulación): 1 título (cuadro o encabezado), 2 gráfico de líneas, 3 anotación, 4 nota de fuente.
- Texto alternativo (Formato > General > Texto alternativo):
  - Gráfico de líneas: «Gráfico de líneas de unidades producidas por año, de 2017 a 2025. La producción sube todos los años: de 35 unidades en 2017 a 210 en 2025, un aumento de 175. El año de menor subida es 2020 (+10).»
  - Anotación: «Aumento de 175 unidades entre 2017 y 2025.»
  - Si el texto alternativo no es dinámico, revisarlo cuando cambien los datos.

### 6. Publicación y seguimiento
1. Publicar en un área de trabajo de prueba; compartir solo con quien decide la versión (Docente de la microcredencial, ejemplo) antes de abrirlo a Dirección, Finanzas y Operaciones.
2. Tras publicar, comprobar: la medida `Titulo mensaje` en los estados 2017-2025, un solo año y 2020-2022; que ninguna cifra dice 46; que fuente y corte ya no son [DATO PENDIENTE].
3. Prueba con personas reales (versión A frente a versión B): al menos 20 en total y 5 o más por perfil; prueba de cinco segundos y pregunta de recuerdo («¿cuánto ha subido la producción y entre qué años?»). La simulación de `1_mirada.md` no la sustituye.
4. Revisar tras cada actualización de `produccion.csv` si «subió todos los años» sigue siendo cierto: lo comprueba `Anios con bajada` = 0.

## Lista de comprobación final
- [ ] `Unidades totales` = 1065; `Unidades inicial` = 35; `Unidades final` = 210; `Aumento unidades` = 175; `Anios con bajada` = 0; `Anios en filtro` = 9.
- [ ] El título dinámico da el texto esperado en tres estados de filtro y nunca afirma subida cuando hay una bajada.
- [ ] No aparece «+46» ni «sostenido» en ningún texto.
- [ ] Eje Y desde 0 y con unidad rotulada.
- [ ] Fuente, corte y fecha completados por el autor (hoy [DATO PENDIENTE]).
- [ ] Sin banda decorativa de plantilla.
- [ ] Contraste de texto medido y de al menos 4,5:1.
- [ ] Texto alternativo y orden de tabulación aplicados.
- [ ] Conflictos 1, 2 y 3 de `4_mejora.md` decididos por la persona.
- [ ] No hay visuales de capacidad ni petición de decisión (A4 y N2 siguen rechazados).
