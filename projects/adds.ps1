param(
    [Parameter(Mandatory=$true, Position=0)][string]$PackageAndConstraint,
    [string]$Group
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = "python"

$cmd = @("$scriptRoot\uv_add_sync.py", $PackageAndConstraint)
if ($Group) { $cmd += @("--group", $Group) }

& $pythonExe $cmd
