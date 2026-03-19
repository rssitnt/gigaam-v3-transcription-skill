param(
  [string]$PythonCommand = "",
  [string]$FfmpegMode = "auto"
)

$ErrorActionPreference = "Stop"

function Resolve-PythonCommand {
  param([string]$Preferred)
  if ($Preferred -and (Get-Command $Preferred -ErrorAction SilentlyContinue)) {
    return $Preferred
  }
  foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
      return $candidate
    }
  }
  return $null
}

function Ensure-Winget {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget не найден. Установи App Installer / winget и повтори запуск."
  }
}

function Ensure-Python {
  param([string]$Preferred)
  $resolved = Resolve-PythonCommand -Preferred $Preferred
  if ($resolved) {
    return $resolved
  }

  Ensure-Winget
  Write-Host "Python не найден. Ставлю Python через winget..."
  winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements

  $resolved = Resolve-PythonCommand -Preferred $Preferred
  if (-not $resolved) {
    throw "Python был установлен, но команда python/py всё ещё не видна. Открой новый терминал и повтори запуск."
  }
  return $resolved
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$bootstrap = Join-Path $repoRoot "skill\scripts\bootstrap_gigaam_runtime.py"
$python = Ensure-Python -Preferred $PythonCommand

Write-Host "Использую Python: $python"
& $python $bootstrap --ffmpeg-mode $FfmpegMode
