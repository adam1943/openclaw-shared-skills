#!/usr/bin/env pwsh
# 免费网页搜索脚本 - 无需 API 密钥
# 使用 Bing 搜索引擎

param(
    [string]$query,
    [int]$count = 5
)

# Bing 搜索 URL
$bingUrl = "https://www.bing.com/search?q=" + [System.Web.HttpUtility]::UrlEncode($query)

Write-Host "正在搜索：$query"
Write-Host "搜索引擎：Bing"
Write-Host "URL: $bingUrl"
Write-Host ""

# 输出搜索结果链接
Write-Host "请在浏览器中打开以上链接查看搜索结果"
Write-Host ""
Write-Host "或者使用以下命令直接获取网页内容："
Write-Host "openclaw browser open '$bingUrl'"
