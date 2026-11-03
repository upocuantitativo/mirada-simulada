<#
Prueba en el motor de Power BI Desktop el modelo y las medidas del ejemplo MercaSur de la pestaña «Claude y Codex en Power BI».
Uso: abre Power BI Desktop con un informe en blanco y ejecuta, desde la carpeta del repositorio,
  powershell -ExecutionPolicy Bypass -File tools\probar_dax_mercasur.ps1
Carga los tres CSV de ejemplo_mercasur\datos con Power Query, crea las relaciones y las medidas, y compara
cada medida con su cifra de control. Sustituye el modelo del informe abierto: ciérralo después sin guardar.
#>
param([int]$Puerto, [string]$Modelo, [string]$Datos = (Join-Path $PSScriptRoot '..\ejemplo_mercasur\datos'))
$ErrorActionPreference = 'Stop'
$pbi = (Get-AppxPackage *PowerBIDesktop* | Select-Object -First 1).InstallLocation
if (-not $pbi) { $pbi = "$env:ProgramFiles\Microsoft Power BI Desktop" }
Add-Type -Path (Join-Path $pbi 'bin\Microsoft.PowerBI.AdomdClient.dll')
if (-not $Puerto) {
  $pt = Get-ChildItem "$env:USERPROFILE\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces", "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces" -Recurse -Filter msmdsrv.port.txt -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $pt) { throw 'Abre Power BI Desktop con un informe en blanco y vuelve a ejecutar.' }
  $Puerto = [int]([IO.File]::ReadAllText($pt.FullName, [Text.Encoding]::Unicode).Trim())
}
if (-not $Modelo) {
  $c0 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Puerto"); $c0.Open()
  $k0 = $c0.CreateCommand(); $k0.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'; $r0 = $k0.ExecuteReader(); [void]$r0.Read(); $Modelo = $r0.GetValue(0); $r0.Close(); $c0.Close()
}
"Motor de Power BI en el puerto $Puerto, modelo $Modelo"
$c = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Puerto;Catalog=$Modelo"); $c.Open()
function Ejecuta($texto) { $k = $c.CreateCommand(); $k.CommandText = $texto; [void]$k.ExecuteNonQuery() }
function M($fichero, $tipos, $extra) {
  $ruta = (Resolve-Path (Join-Path $Datos $fichero)).Path.Replace('"', '""')
  $l = @('let', "    Origen = Csv.Document(File.Contents(""$ruta""), [Delimiter = "","", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),",
         '    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),',
         "    Tipos = Table.TransformColumnTypes(Encabezados, {$tipos}, ""en-US"")")
  if ($extra) { $l[-1] += ','; $l += $extra; $ult = ($extra[-1] -split ' = ')[0].Trim() } else { $ult = 'Tipos' }
  ($l + @('in', "    $ult"))
}
function Col($n, $t, $extra) { $o = @{ name = $n; dataType = $t; sourceColumn = $n }; if ($extra) { $extra.GetEnumerator() | ForEach-Object { $o[$_.Key] = $_.Value } }; $o }

$ventas = @{ name = 'Ventas'
  columns = @((Col 'fecha' 'string' @{isHidden=$true}), (Col 'id_tienda' 'string' @{isHidden=$true}), (Col 'linea' 'string'), (Col 'unidades' 'int64'),
              (Col 'ventas_usd' 'double'), (Col 'margen_pct' 'double' @{summarizeBy='none'}), (Col 'Anio' 'int64' @{summarizeBy='none'; isHidden=$true}), (Col 'Mes' 'dateTime'))
  partitions = @(@{ name = 'Ventas'; mode = 'import'; source = @{ type = 'm'; expression = (M 'mercasur360_ventas.csv' '{"fecha", type text}, {"id_tienda", type text}, {"linea", type text}, {"unidades", Int64.Type}, {"ventas_usd", type number}, {"margen_pct", type number}' @(
    '    Columnas = Table.SelectColumns(Tipos, {"fecha", "id_tienda", "linea", "unidades", "ventas_usd", "margen_pct"}),',
    '    ConAnio = Table.AddColumn(Columnas, "Anio", each Number.From(Text.Start([fecha], 4)), Int64.Type),',
    '    ConMes = Table.AddColumn(ConAnio, "Mes", each #date(Number.From(Text.Start([fecha], 4)), Number.From(Text.End([fecha], 2)), 1), type date)')) } }) }
$tiendas = @{ name = 'Tiendas'
  columns = @((Col 'id_tienda' 'string'), (Col 'tienda' 'string'), (Col 'departamento' 'string'), (Col 'es_nueva' 'string'))
  partitions = @(@{ name = 'Tiendas'; mode = 'import'; source = @{ type = 'm'; expression = (M 'mercasur360_tiendas.csv' '{"id_tienda", type text}, {"tienda", type text}, {"departamento", type text}, {"es_nueva", type text}' @(
    '    Columnas = Table.SelectColumns(Tipos, {"id_tienda", "tienda", "departamento", "es_nueva"})')) } }) }
$presu = @{ name = 'Presupuesto'
  columns = @((Col 'id_tienda' 'string' @{isHidden=$true}), (Col 'linea' 'string'), (Col 'semestre' 'string'), (Col 'objetivo_usd' 'double'), (Col 'Anio' 'int64' @{summarizeBy='none'; isHidden=$true}))
  partitions = @(@{ name = 'Presupuesto'; mode = 'import'; source = @{ type = 'm'; expression = (M 'mercasur360_presupuesto.csv' '{"id_tienda", type text}, {"linea", type text}, {"semestre", type text}, {"objetivo_usd", type number}' @(
    '    ConAnio = Table.AddColumn(Tipos, "Anio", each Number.From(Text.Start([semestre], 4)), Int64.Type)')) } }) }
$anios = @{ name = 'Anios'
  columns = @(@{ name = 'Anio'; type = 'calculatedTableColumn'; dataType = 'int64'; sourceColumn = '[Anio]'; isNameInferred = $true; isDataTypeInferred = $true; summarizeBy = 'none' })
  partitions = @(@{ name = 'Anios'; source = @{ type = 'calculated'; expression = 'SELECTCOLUMNS ( GENERATESERIES ( 2024, 2025, 1 ), "Anio", [Value] )' } }) }

# Medidas: las mismas que la pestaña «Claude y Codex en Power BI» pide al agente (ia_powerbi.html, paso 4)
$medidas = [ordered]@{
 'Ventas' = 'SUM ( Ventas[ventas_usd] )'
 'Ventas ultimo anio' = 'CALCULATE ( [Ventas], Anios[Anio] = MAX ( Anios[Anio] ) )'
 'Ventas anio anterior' = 'CALCULATE ( [Ventas], Anios[Anio] = MAX ( Anios[Anio] ) - 1 )'
 'Crecimiento' = 'DIVIDE ( [Ventas ultimo anio] - [Ventas anio anterior], [Ventas anio anterior] )'
 'Ventas comparables' = 'CALCULATE ( [Ventas], Tiendas[es_nueva] = "no" )'
 'Crecimiento comparables' = 'VAR Actual = CALCULATE ( [Ventas comparables], Anios[Anio] = MAX ( Anios[Anio] ) ) VAR Previo = CALCULATE ( [Ventas comparables], Anios[Anio] = MAX ( Anios[Anio] ) - 1 ) RETURN DIVIDE ( Actual - Previo, Previo )'
 'Ventas tiendas nuevas' = 'CALCULATE ( [Ventas], Tiendas[es_nueva] <> "no" )'
 'Ventas tiendas nuevas ultimo anio' = 'CALCULATE ( [Ventas tiendas nuevas], Anios[Anio] = MAX ( Anios[Anio] ) )'
 'Objetivo' = 'SUM ( Presupuesto[objetivo_usd] )'
 'Cumplimiento' = 'DIVIDE ( [Ventas], [Objetivo] )'
 'Desviacion objetivo' = '[Cumplimiento] - 1'
 'Margen ponderado' = 'DIVIDE ( SUMX ( Ventas, Ventas[ventas_usd] * Ventas[margen_pct] / 100 ), [Ventas] )'
 'Titulo panel' = 'VAR T = [Crecimiento] VAR TC = [Crecimiento comparables] VAR Total = IF ( T < 0, "caen un ", "suben un " ) & FORMAT ( ABS ( T ), "0.0 %" ) VAR Comp = IF ( TC < 0, "caen un ", "suben un " ) & FORMAT ( ABS ( TC ), "0.0 %" ) RETURN IF ( NOT ISBLANK ( T ), "En " & MAX ( Anios[Anio] ) & " las ventas " & Total & IF ( SIGN ( T ) <> SIGN ( TC ), ", pero en las tiendas comparables ", " y en las tiendas comparables " ) & Comp, "Ventas de MercaSur 360: " & FORMAT ( [Ventas], "#,##0" ) & " USD" )'
}
$ventas.measures = @($medidas.Keys | ForEach-Object { @{ name = $_; expression = $medidas[$_] } })
$rel = @(
 @{ name = 'Ventas_Tiendas'; fromTable = 'Ventas'; fromColumn = 'id_tienda'; toTable = 'Tiendas'; toColumn = 'id_tienda' },
 @{ name = 'Presupuesto_Tiendas'; fromTable = 'Presupuesto'; fromColumn = 'id_tienda'; toTable = 'Tiendas'; toColumn = 'id_tienda' },
 @{ name = 'Ventas_Anios'; fromTable = 'Ventas'; fromColumn = 'Anio'; toTable = 'Anios'; toColumn = 'Anio' },
 @{ name = 'Presupuesto_Anios'; fromTable = 'Presupuesto'; fromColumn = 'Anio'; toTable = 'Anios'; toColumn = 'Anio' })
$dbdef = @{ name = $Modelo; id = $Modelo; compatibilityLevel = 1606; model = @{ name = 'Model'; culture = 'es-ES'; defaultPowerBIDataSourceVersion = 'powerBI_V3'; tables = @($ventas, $tiendas, $presu, $anios); relationships = $rel } }
Ejecuta (@{ createOrReplace = @{ object = @{ database = $Modelo }; database = $dbdef } } | ConvertTo-Json -Depth 14)
Ejecuta (@{ refresh = @{ type = 'full'; objects = @(@{ database = $Modelo }) } } | ConvertTo-Json -Depth 6)

function Valor($dax) { $k = $c.CreateCommand(); $k.CommandText = $dax; $r = $k.ExecuteReader(); [void]$r.Read(); $v = $r.GetValue(0); $r.Close(); $v }
# Cifras de control: calculadas sobre los CSV con Python (tabla de ia_powerbi.html)
$pruebas = @(
 @('Ventas', $null, 25610000.06, 0.01), @('Ventas', 'Anios[Anio] = 2024', 11764148.43, 0.01), @('Ventas', 'Anios[Anio] = 2025', 13845851.63, 0.01),
 @('Crecimiento', 'Anios[Anio] = 2025', 0.17695, 0.0001), @('Ventas comparables', 'Anios[Anio] = 2025', 11049222.28, 0.01),
 @('Crecimiento comparables', 'Anios[Anio] = 2025', -0.01145, 0.0001), @('Ventas tiendas nuevas', 'Anios[Anio] = 2025', 2796629.35, 0.01),
 @('Objetivo', 'Anios[Anio] = 2025', 13897696, 0.5), @('Cumplimiento', 'Anios[Anio] = 2025', 0.99627, 0.0001),
 @('Margen ponderado', 'Anios[Anio] = 2025', 0.2220, 0.0001), @('Margen ponderado', $null, 0.2240, 0.0001),
 @('Cumplimiento', 'Tiendas[id_tienda] = "H"', 1.0240, 0.0001), @('Cumplimiento', 'Tiendas[id_tienda] = "L"', 0.9809, 0.0001),
 @('Crecimiento', 'Anios[Anio] = 2024', $null, 0), @('Crecimiento', $null, 0.17695, 0.0001), @('Ventas tiendas nuevas ultimo anio', $null, 2796629.35, 0.01), @('Crecimiento comparables', $null, -0.01145, 0.0001),
 @('Desviacion objetivo', 'Tiendas[id_tienda] = "H"', 0.0240, 0.0001), @('Desviacion objetivo', 'Tiendas[id_tienda] = "L"', -0.0191, 0.0001),
 @('Titulo panel', 'Anios[Anio] = 2025', 'contiene:En 2025 las ventas suben un 17,7 %, pero en las tiendas comparables caen un 1,1 %', 0), @('Titulo panel', $null, 'contiene:En 2025 las ventas suben un 17,7 %, pero en las tiendas comparables caen un 1,1 %', 0), @('Titulo panel', 'Anios[Anio] = 2024', 'contiene:Ventas de MercaSur 360: 11.764.148 USD', 0)
)
$mal = 0
foreach ($p in $pruebas) {
  $dax = if ($p[1]) { "EVALUATE ROW(""v"", CALCULATE([$($p[0])], $($p[1])))" } else { "EVALUATE ROW(""v"", [$($p[0])])" }
  $v = Valor $dax
  $ok = if ($p[2] -is [string]) { "$v".Contains($p[2].Substring(9)) } elseif ($null -eq $p[2]) { $null -eq $v -or $v -is [DBNull] } else { -not ($v -is [DBNull]) -and [math]::Abs([double]$v - $p[2]) -le $p[3] }
  if (-not $ok) { $mal++ }
  "{0} {1} | {2} -> {3}" -f $(if ($ok) { 'OK  ' } else { 'MAL ' }), $p[0], $(if ($p[1]) { $p[1] } else { 'sin filtro' }), $(if ($v -is [DBNull]) { '(en blanco)' } else { "$v" })
}
"Fallos: $mal de $($pruebas.Count)"
$c.Close()
