<#
Prueba en el motor de Power BI Desktop las medidas DAX del agente Power BI (ejemplo «Evolución de la producción»).
Uso: abre Power BI Desktop con un informe en blanco y ejecuta
  powershell -ExecutionPolicy Bypass -File tools\probar_dax_powerbi.ps1 -Csv ejemplo\entrada\produccion.csv
Sustituye el modelo del informe abierto: úsalo con un informe en blanco y ciérralo sin guardar.
#>
param([int]$Puerto, [string]$Modelo, [Parameter(Mandatory)][string]$Csv, [switch]$SinCrear)
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
$c = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Puerto;Catalog=$Modelo")
$c.Open()
function Ejecuta($texto) { $k = $c.CreateCommand(); $k.CommandText = $texto; [void]$k.ExecuteNonQuery() }

# datos: se leen del CSV del ejemplo, no se escriben a mano
$filas = Import-Csv $Csv -Delimiter ';' | ForEach-Object { "{$($_.Anio),$($_.Unidades)}" }
$datatable = 'DATATABLE("Anio", INTEGER, "Unidades", INTEGER, {' + ($filas -join ',') + '})'

# medidas tal como las escribe el agente Power BI en 5_powerbi.md
$medidas = [ordered]@{
 'Unidades totales' = 'SUM ( Produccion[Unidades] )'
 'Unidades ultimo anio' = 'CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MAX ( Produccion[Anio] ) )'
 'Unidades primer anio' = 'CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MIN ( Produccion[Anio] ) )'
 'Aumento acumulado' = '[Unidades ultimo anio] - [Unidades primer anio]'
 'Veces que se multiplica' = 'DIVIDE ( [Unidades ultimo anio], [Unidades primer anio] )'
 'Aumento anual' = 'SUM ( Produccion[Unidades] ) - CALCULATE ( SUM ( Produccion[Unidades] ), Produccion[Anio] = MAX ( Produccion[Anio] ) - 1 )'
 'Aumento anual medio' = 'DIVIDE ( [Aumento acumulado], DISTINCTCOUNT ( Produccion[Anio] ) - 1 )'
 'Anios con caida' = 'COALESCE ( COUNTROWS ( FILTER ( VALUES ( Produccion[Anio] ), Produccion[Anio] > MIN ( Produccion[Anio] ) && [Aumento anual] < 0 ) ), 0 )'
 'Titulo pagina 1' = 'IF ( HASONEVALUE ( Produccion[Anio] ), "Producción de " & VALUES ( Produccion[Anio] ) & ": " & FORMAT ( [Unidades totales], "#,##0" ) & " unidades", "La producción pasó de " & [Unidades primer anio] & " a " & [Unidades ultimo anio] & " unidades entre " & MIN ( Produccion[Anio] ) & " y " & MAX ( Produccion[Anio] ) & " (+" & [Aumento acumulado] & ")" )'
}
$prod = @{
 name = 'Produccion'
 columns = @(
  @{ name = 'Anio'; type = 'calculatedTableColumn'; dataType = 'int64'; sourceColumn = '[Anio]'; isNameInferred = $true; isDataTypeInferred = $true; summarizeBy = 'none' },
  @{ name = 'Unidades'; type = 'calculatedTableColumn'; dataType = 'int64'; sourceColumn = '[Unidades]'; isNameInferred = $true; isDataTypeInferred = $true },
  @{ name = 'Fecha'; type = 'calculated'; dataType = 'dateTime'; expression = 'DATE ( Produccion[Anio], 12, 31 )'; isHidden = $true }
 )
 partitions = @(@{ name = 'Produccion'; source = @{ type = 'calculated'; expression = $datatable } })
 measures = @($medidas.Keys | ForEach-Object { @{ name = $_; expression = $medidas[$_] } })
}
$cal = @{
 name = 'Calendario'; dataCategory = 'Time'
 columns = @(
  @{ name = 'Date'; type = 'calculatedTableColumn'; dataType = 'dateTime'; sourceColumn = '[Date]'; isNameInferred = $true; isDataTypeInferred = $true; isKey = $true; isHidden = $true },
  @{ name = 'Anio'; type = 'calculatedTableColumn'; dataType = 'int64'; sourceColumn = '[Anio]'; isNameInferred = $true; isDataTypeInferred = $true }
 )
 partitions = @(@{ name = 'Calendario'; source = @{ type = 'calculated'; expression = 'ADDCOLUMNS ( CALENDAR ( DATE ( 2017, 1, 1 ), DATE ( 2025, 12, 31 ) ), "Anio", YEAR ( [Date] ) )' } })
}
$dbdef = @{ name = $Modelo; id = $Modelo; compatibilityLevel = 1606; model = @{ name = 'Model'; culture = 'es-ES'; defaultPowerBIDataSourceVersion = 'powerBI_V3'; tables = @($prod, $cal); relationships = @(@{ name = 'Produccion_Calendario'; fromTable = 'Produccion'; fromColumn = 'Fecha'; toTable = 'Calendario'; toColumn = 'Date' }) } }
Ejecuta (@{ createOrReplace = @{ object = @{ database = $Modelo }; database = $dbdef } } | ConvertTo-Json -Depth 12)
Ejecuta (@{ refresh = @{ type = 'full'; objects = @(@{ database = $Modelo; table = 'Produccion' }, @{ database = $Modelo; table = 'Calendario' }) } } | ConvertTo-Json -Depth 10)

function Valor($dax) { $k = $c.CreateCommand(); $k.CommandText = $dax; $r = $k.ExecuteReader(); [void]$r.Read(); $v = $r.GetValue(0); $r.Close(); $v }
$m = { param($medida, $filtro) if ($filtro) { "EVALUATE ROW(""v"", CALCULATE([$medida], $filtro))" } else { "EVALUATE ROW(""v"", [$medida])" } }
$pruebas = @(
 @('Unidades totales', $null, 1065), @('Unidades primer anio', $null, 35), @('Unidades ultimo anio', $null, 210),
 @('Aumento acumulado', $null, 175), @('Veces que se multiplica', $null, 6), @('Aumento anual medio', $null, 21.875),
 @('Anios con caida', $null, $null),
 @('Aumento anual', 'Produccion[Anio] = 2025', 20), @('Aumento anual', 'Produccion[Anio] = 2020', 10), @('Aumento anual', 'Produccion[Anio] = 2021', 35),
 @('Aumento acumulado', 'Produccion[Anio] <= 2021', 85), @('Veces que se multiplica', 'Produccion[Anio] <= 2021', 3.4286),
 @('Titulo pagina 1', $null, 'La producción pasó de 35 a 210 unidades entre 2017 y 2025 (+175)'),
 @('Titulo pagina 1', 'Produccion[Anio] = 2020', 'Producción de 2020: 85 unidades'),
 @('Aumento acumulado', 'Calendario[Anio] <= 2021', 85), @('Titulo pagina 1', 'Calendario[Anio] = 2020', 'Producción de 2020: 85 unidades'), @('Unidades totales', 'Calendario[Anio] = 2025', 210)
)
$mal = 0
foreach ($p in $pruebas) {
 $v = Valor (& $m $p[0] $p[1])
 # «Anios con caida» = 0: COUNTROWS de una tabla vacía devuelve BLANK, que la tarjeta muestra como (En blanco)
 $ok = if ($p[2] -is [string]) { "$v" -eq $p[2] } elseif ($null -eq $p[2]) { $v -is [DBNull] -or $v -eq 0 } else { [math]::Abs([double]$v - $p[2]) -lt 0.001 }
 if (-not $ok) { $mal++ }
 $mostrar = if ($v -is [DBNull]) { '(en blanco)' } else { "$v" }
 "{0} {1} | {2} -> {3}" -f ($(if ($ok) { 'OK  ' } else { 'MAL ' })), $p[0], $(if ($p[1]) { $p[1] } else { 'sin filtro' }), $mostrar
}
"Fallos: $mal"
$c.Close()

$c2 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Puerto;Catalog=$Modelo"); $c2.Open(); $k=$c2.CreateCommand(); $k.CommandText='SELECT [Name],[IsActive] FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS'; $r=$k.ExecuteReader(); while($r.Read()){ "relacion: $($r.GetValue(0)) activa=$($r.GetValue(1))" }; $r.Close(); $c2.Close()