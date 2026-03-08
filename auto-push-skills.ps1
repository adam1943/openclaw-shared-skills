# OpenClaw Skills 自动推送脚本
# 监控 skills 目录变化，自动推送到 GitHub

$ErrorActionPreference = "Stop"
$watchPath = "C:\Users\Adams Dun\.openclaw\workspace\skills"
$gitPath = "C:\Users\Adams Dun\.openclaw\workspace"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  OpenClaw Skills - 自动推送监控" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "监控目录：$watchPath" -ForegroundColor Yellow
Write-Host "检查时间：$(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# 检查是否有未提交的更改
Set-Location $gitPath
$status = git status --porcelain 2>$null

if ($status) {
    Write-Host "检测到更改：" -ForegroundColor Green
    Write-Host $status -ForegroundColor White
    Write-Host ""
    
    # 提交并推送
    Write-Host "正在提交..." -ForegroundColor Yellow
    git add -A
    git commit -m "Auto-update skills: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    Write-Host "正在推送..." -ForegroundColor Yellow
    $result = git push origin main 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ 推送成功！" -ForegroundColor Green
        Write-Host "仓库：https://github.com/adam1943/openclaw-shared-skills" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ 推送失败：$result" -ForegroundColor Red
    }
} else {
    Write-Host "✅ 没有更改，无需推送" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
