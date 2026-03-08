# Model Router 测试脚本

$ErrorActionPreference = "Stop"
$configPath = "C:\Users\Adams Dun\.openclaw\workspace\skills\model-router\config\routing-rules.json"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Model Router 测试工具 v0.1" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 加载路由配置
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# 测试问题列表
$testQuestions = @(
    @{ Question = "帮我写一个 Python 函数，计算斐波那契数列"; Expected = "qwen3-coder-plus" },
    @{ Question = "分析这个逻辑推理题的解题思路"; Expected = "qwen3-max" },
    @{ Question = "帮我写一份季度工作总结报告"; Expected = "kimi-k2.5" },
    @{ Question = "创作一个科幻短篇故事"; Expected = "MiniMax" },
    @{ Question = "把这段话翻译成英文"; Expected = "glm-5" },
    @{ Question = "今天天气怎么样"; Expected = "qwen3.5-plus" }
)

Write-Host "测试问题列表：" -ForegroundColor Yellow
Write-Host ""

foreach ($test in $testQuestions) {
    $question = $test.Question
    $expected = $test.Expected
    
    # 简单路由逻辑
    $selectedModel = $config.fallback_model
    
    foreach ($rule in $config.routing_rules) {
        foreach ($keyword in $rule.keywords) {
            if ($question -like "*$keyword*") {
                $selectedModel = $rule.model
                break
            }
        }
        if ($selectedModel -ne $config.fallback_model) { break }
    }
    
    # 简化模型名称显示
    $displayName = $selectedModel -replace 'bailian/', ''
    $expectedDisplay = $expected -replace 'bailian/', ''
    
    # 判断是否匹配
    $match = if ($displayName -like "*$expected*") { "✅" } else { "❌" }
    
    Write-Host "$match 问题：$question" -ForegroundColor $(if ($match -eq "✅") { "Green" } else { "Red" })
    Write-Host "   路由模型：$displayName" -ForegroundColor Gray
    Write-Host "   预期模型：$expectedDisplay" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
