param(
    [Parameter(Mandatory = $true, Position = 0)][string]$ProjectName
)

$root = "C:\Users\boazk\git\pet-projects-monorepo\Projects"
$queue = New-Object System.Collections.Queue
$queue.Enqueue($root)
$found = $null

while ($queue.Count -gt 0 -and -not $found) {
    $current = $queue.Dequeue()
    $dirs = Get-ChildItem -Path $current -Directory -ErrorAction SilentlyContinue
    foreach ($dir in $dirs) {
        if ($dir.Name -eq $ProjectName) {
            $found = $dir.FullName
            break
        }
        $queue.Enqueue($dir.FullName)
    }
}

if ($found) {
    Set-Location $found
    $venvActivate = ".venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        . $venvActivate
    } else {
        Write-Host "Found project '$ProjectName', but no virtual environment at $venvActivate"
    }
} else {
    Write-Host "Project '$ProjectName' not found under $root"
}