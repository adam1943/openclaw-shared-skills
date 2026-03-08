# Model Router Test

$configPath = "C:\Users\Adams Dun\.openclaw\workspace\skills\model-router\config\routing-rules.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

Write-Host "Testing Model Router..." -ForegroundColor Cyan
Write-Host ""

$questions = @(
    "Python code function",
    "logic reasoning analysis",
    "write report document",
    "creative story",
    "translate to English",
    "daily chat"
)

foreach ($q in $questions) {
    $model = $config.fallback_model
    foreach ($rule in $config.routing_rules) {
        foreach ($kw in $rule.keywords) {
            if ($q -like "*$kw*") {
                $model = $rule.model
                break
            }
        }
        if ($model -ne $config.fallback_model) { break }
    }
    $display = $model -replace 'bailian/', ''
    Write-Host "Q: $q -> Model: $display" -ForegroundColor Green
}

Write-Host ""
Write-Host "Test Complete!" -ForegroundColor Cyan
