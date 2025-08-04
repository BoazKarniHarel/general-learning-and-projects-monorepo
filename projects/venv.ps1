# venv.ps1
# Usage: .\venv.ps1
# This script finds the current Python interpreter, finds the project root, and activates the venv for that project.

# Get the path to the current Python interpreter
$python = Get-Command python | Select-Object -ExpandProperty Source

if (-not $python) {
    Write-Host "Python interpreter not found in PATH."
    exit 1
}

# Find the venv root by looking for 'pyproject.toml' upwards from the current directory
function Find-ProjectRoot {
    $dir = Get-Location
    while ($dir -ne $null) {
        if (Test-Path (Join-Path $dir 'pyproject.toml')) {
            return $dir
        }
        $parent = Split-Path $dir -Parent
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    return $null
}

$projectRoot = Find-ProjectRoot
if (-not $projectRoot) {
    Write-Host "No project root with pyproject.toml found."
    exit 1
}

# Find the venv directory (look for .venv or any folder with Scripts/Activate)
$venvCandidates = Get-ChildItem -Path $projectRoot -Directory | Where-Object {
    Test-Path (Join-Path $_.FullName 'Scripts/Activate')
}

if ($venvCandidates.Count -eq 0) {
    Write-Host "No virtual environment found in project root: $projectRoot"
    exit 1
}

# Use the first venv found
$venvPath = $venvCandidates[0].FullName

# Change to the project root
Set-Location $projectRoot

# Activate the venv
$activateScript = Join-Path $venvPath 'Scripts/Activate.ps1'
if (Test-Path $activateScript) {
    Write-Host "Activating venv at $venvPath"
    . $activateScript
} else {
    Write-Host "Activation script not found: $activateScript"
    exit 1
}
