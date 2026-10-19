# Instalador del curso para PowerShell (Windows):
#   powershell -ExecutionPolicy Bypass -File instalar.ps1
# Deja instalado uv, las dependencias y el entorno, y lanza el configurador de tu modelo.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "== Curso «Más allá de los chatbots»: instalación =="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Aviso: no encuentro git. No hace falta para ejecutar el curso, pero sí para actualizar el repositorio (https://git-scm.com/download/win)."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "No encuentro uv, el gestor de Python del curso. Lo voy a instalar con el instalador oficial de Astral"
    Write-Host "(https://astral.sh/uv/install.ps1); se instala en tu carpeta de usuario, sin permisos de administrador."
    $r = Read-Host "¿Continuar? [S/n]"
    if ($r -and $r -notmatch '^[sSyY]') { Write-Host "Cancelado."; exit 1 }
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    # uv se instala en %USERPROFILE%\.local\bin
    $env:Path = "$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "uv se instaló pero esta terminal no lo ve: ciérrala, ábrela y repite."
        exit 1
    }
}

Write-Host "Instalando Python 3.12 y las dependencias (la primera vez tarda unos minutos)..."
uv sync
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
uv run copiloto-configurar @args
exit $LASTEXITCODE
