# Check if Ollama is running
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue

if (-not $ollamaProcess) {
    Write-Host "Starting Ollama..." -ForegroundColor Green
    Start-Process ollama -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 3 # Wait for it to initialize
} else {
    Write-Host "Ollama is already running." -ForegroundColor Yellow
}

# Python checks
Write-Host "Checking environment..." -ForegroundColor Green
if (Test-Path "venv") {
    Write-Host "Activating venv..."
    .\venv\Scripts\Activate.ps1
}

# Migrations (just in case)
Write-Host "Applying database migrations..."
python manage.py migrate

# Server
Write-Host "Starting Django Server..." -ForegroundColor Cyan
Write-Host "Go to: http://127.0.0.1:8000/"
python manage.py runserver
