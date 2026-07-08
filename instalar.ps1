# Instala dependências e configura agendamento diário do clipping
# Execute como Administrador no PowerShell

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  INSTALAÇÃO - Clipping Renan Santos" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERRO] Python não encontrado. Instale em https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python encontrado: $($python.Source)" -ForegroundColor Green

# Instala dependências
Write-Host ""
Write-Host "Instalando dependências Python..." -ForegroundColor Yellow
python -m pip install feedparser requests --quiet
Write-Host "[OK] Dependências instaladas" -ForegroundColor Green

# Caminho do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "clipping.py"

# Cria o agendamento no Windows Task Scheduler
$taskName = "ClippingRenanSantos"
$hora = "08:00"

Write-Host ""
Write-Host "Configurando agendamento diário às $hora..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute "python" -Argument "`"$scriptPath`"" -WorkingDirectory $scriptDir
$trigger = New-ScheduledTaskTrigger -Daily -At $hora
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Remove tarefa anterior se existir
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Clipping diário de imprensa - Renan Santos" | Out-Null

Write-Host "[OK] Tarefa agendada: '$taskName' - todo dia às $hora" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ""
Write-Host "  Relatórios serão salvos em:" -ForegroundColor White
Write-Host "  $scriptDir\relatorios\" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Para executar agora: python `"$scriptPath`"" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
