param(
  [Parameter(Mandatory=$true)][string]$RepoUrl,
  [string]$TargetDir = "",
  [string]$PythonCommand = "",
  [string]$FfmpegMode = "auto"
)

$ErrorActionPreference = "Stop"

if (-not $TargetDir) {
  $name = [System.IO.Path]::GetFileNameWithoutExtension($RepoUrl)
  $TargetDir = Join-Path (Get-Location) $name
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git не найден. Установи git и повтори запуск."
}

if (-not (Test-Path $TargetDir)) {
  git clone $RepoUrl $TargetDir
}

Push-Location $TargetDir
try {
  powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -PythonCommand $PythonCommand -FfmpegMode $FfmpegMode
  python .\scripts\verify_install.py
}
finally {
  Pop-Location
}
