# Publish World Bank WDI panel to Kaggle
# Prerequisites:
#   1. kaggle CLI installed (pip install kaggle)
#   2. %USERPROFILE%\.kaggle\kaggle.json from https://www.kaggle.com/settings
#   3. YOUR_USERNAME replaced in dataset-metadata.json

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$metaPath = Join-Path $here "dataset-metadata.json"
$meta = Get-Content $metaPath -Raw
if ($meta -match "YOUR_USERNAME") {
    Write-Host "ERROR: Edit dataset-metadata.json and replace YOUR_USERNAME with your Kaggle username." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$env:USERPROFILE\.kaggle\kaggle.json")) {
    Write-Host "ERROR: Missing $env:USERPROFILE\.kaggle\kaggle.json" -ForegroundColor Red
    Write-Host "Download token from https://www.kaggle.com/settings -> Create New Token"
    exit 1
}

Write-Host "Creating Kaggle dataset from $here ..." -ForegroundColor Cyan
kaggle datasets create -p $here --dir-mode zip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Create failed — trying version update (dataset may already exist)..." -ForegroundColor Yellow
    kaggle datasets version -p $here -m "Update WDI panel" --dir-mode zip
}
