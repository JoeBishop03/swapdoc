<#
.SYNOPSIS
  Deploys SwapDoc to Azure Container Apps and sets up the visitor dashboard.

.DESCRIPTION
  Run from the SwapDoc folder in PowerShell:   .\deploy\deploy.ps1

  1. Signs you in to Azure if needed.
  2. Finds the existing "swapdoc" Container App.
  3. Creates (or updates) Application Insights and the "SwapDoc visitors" dashboard.
  4. Builds the new code in Azure and switches the app over to it.

  Safe to run again: each run just deploys the latest code.

.PARAMETER SkipAnalytics  Only deploy code; don't touch the dashboard.
.PARAMETER SkipCode       Only set up the dashboard; don't rebuild the app.
#>
param(
    [string]$AppName = "swapdoc",
    [string]$ResourceGroup = "",
    [switch]$SkipAnalytics,
    [switch]$SkipCode
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Step($msg) { Write-Host "`n== $msg" -ForegroundColor Cyan }
function AzCli {
    # Runs the Azure CLI and stops the script if it fails. Warnings that az
    # prints on stderr shouldn't stop the script, only a failing exit code.
    $ErrorActionPreference = "Continue"
    $out = & az.cmd @args --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "az $($args[0..2] -join ' ') failed (see the error above)" }
    return $out
}

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "The Azure CLI isn't installed. Install it with:  winget install -e --id Microsoft.AzureCLI   then open a new PowerShell window."
}

Step "Checking you're signed in to Azure"
& az account show 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { AzCli login | Out-Null }
$sub = AzCli account show --query "{name:name, id:id}" -o json | ConvertFrom-Json
Write-Host "Subscription: $($sub.name)"
AzCli extension add --name containerapp --upgrade | Out-Null

Step "Finding the '$AppName' Container App"
if (-not $ResourceGroup) {
    $ResourceGroup = AzCli containerapp list --query "[?name=='$AppName'].resourceGroup | [0]" -o tsv
    if (-not $ResourceGroup) { throw "No Container App called '$AppName' in this subscription. Use -ResourceGroup / -AppName, or 'az account set' to switch subscription." }
}
$app = AzCli containerapp show -n $AppName -g $ResourceGroup -o json | ConvertFrom-Json
$location = $app.location.Replace(" ", "").ToLower()   # "UK South" -> "uksouth"
$image = $app.properties.template.containers[0].image
Write-Host "Resource group: $ResourceGroup   Region: $location"
Write-Host "Current image:  $image"

$envVars = @()
if (-not $SkipAnalytics) {
    Step "Creating Application Insights and the 'SwapDoc visitors' dashboard"
    $outputs = AzCli deployment group create -g $ResourceGroup -n "swapdoc-analytics" `
        --template-file "infra/analytics.json" --parameters location=$location `
        --query "properties.outputs" -o json | ConvertFrom-Json
    $cs = $outputs.connectionString.value

    $secretNames = AzCli containerapp secret list -n $AppName -g $ResourceGroup --query "[].name" -o json | ConvertFrom-Json
    $secrets = @("appinsights-cs=$cs")
    if ($secretNames -notcontains "visitor-salt") {
        # Secret key for the anonymous daily visitor ID. Created once, then kept.
        $bytes = New-Object byte[] 32
        [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
        $secrets += "visitor-salt=$(-join ($bytes | ForEach-Object { $_.ToString('x2') }))"
    }
    AzCli containerapp secret set -n $AppName -g $ResourceGroup --secrets @secrets -o none
    $envVars = @("APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-cs", "VISITOR_SALT=secretref:visitor-salt")
    Write-Host "Dashboard: $($outputs.workbookUrl.value)" -ForegroundColor Green
}

if (-not $SkipCode) {
    $tag = Get-Date -Format "yyyyMMdd-HHmmss"
    if ($image -match '^([a-z0-9]+)\.azurecr\.io/([^:@]+)') {
        $registry = $Matches[1]; $repo = $Matches[2]
        $newImage = "$registry.azurecr.io/$($repo):$tag"
        Step "Building the new version in Azure ($newImage). This takes about 5-10 minutes"
        # --no-logs: on Windows, az crashes trying to print some characters in
        # the build log, so start the build quietly and check on it instead.
        $run = AzCli acr build --registry $registry --image "$($repo):$tag" --file Dockerfile --no-logs . -o json | ConvertFrom-Json
        $runId = $run.runId
        do {
            Start-Sleep -Seconds 15
            $status = AzCli acr task show-run -r $registry --run-id $runId --query status -o tsv
            Write-Host "  build $runId : $status"
        } while ($status -in @("Queued", "Started", "Running"))
        if ($status -ne "Succeeded") {
            throw "Build $runId ended as '$status'. See the log with:  az acr task logs -r $registry --run-id $runId"
        }
        Step "Switching the app to the new version"
        $update = @("containerapp", "update", "-n", $AppName, "-g", $ResourceGroup, "--image", $newImage, "-o", "none")
        if ($envVars) { $update += @("--set-env-vars") + $envVars }
        AzCli @update
    } else {
        Step "Image isn't in an Azure Container Registry; building with 'az containerapp up'"
        AzCli containerapp up -n $AppName -g $ResourceGroup --source . | Out-Host
        if ($envVars) { AzCli containerapp update -n $AppName -g $ResourceGroup --set-env-vars @envVars -o none }
    }
} elseif ($envVars) {
    Step "Adding the Application Insights settings to the app"
    AzCli containerapp update -n $AppName -g $ResourceGroup --set-env-vars @envVars -o none
}

Step "Checking the live site"
Start-Sleep -Seconds 20
foreach ($u in "https://www.swapdoc.co.uk/healthz", "https://www.swapdoc.co.uk/word-to-pdf", "https://www.swapdoc.co.uk/sitemap.xml") {
    try { $r = Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 30; Write-Host "$($r.StatusCode)  $u" }
    catch { Write-Host "FAILED  $u  ($($_.Exception.Message))" -ForegroundColor Yellow }
}
Write-Host "`nDone." -ForegroundColor Green
