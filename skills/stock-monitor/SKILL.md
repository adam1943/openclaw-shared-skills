---
name: stock-monitor
description: A 股和港股选股、监控、买卖建议。Use when user asks about: stock selection, stock monitoring, price alerts, trading suggestions, market analysis for Chinese A-shares or HK stocks. Triggers: "选股", "股票", "炒股", "买入", "卖出", "股价", "行情", "监控", "推荐股票"
---

# Stock Monitor - A 股选股与监控

## 核心功能

### 1. 盘后选股（每日收盘后运行）
- 基本面筛选：PE、PB、ROE、市值
- 技术面筛选：均线、MACD、RSI
- 混合策略：综合评估输出选股理由
- 飞书推送：选股结果自动发送

### 2. 盘中监控（交易时间实时）
- 价格提醒：涨跌幅超阈值推送
- 快速变化：检测快速上涨/下跌
- 买卖建议：根据走势给出操作建议

## 快速使用

### 选股
```bash
# 运行选股策略
python ~/stock-monitor/stock_selector.py
```

### 监控
```bash
# 单次检查
python ~/stock-monitor/stock_monitor.py once

# 持续监控
python ~/stock-monitor/stock_monitor.py
```

### 查看结果
选股结果保存在：`~/stock-monitor/selection_*.json`

## 配置文件

位置：`~/stock-monitor/config.json`

### 关注股票列表
```json
{
    "watchlist": {
        "stocks": [
            {"code": "600519", "name": "贵州茅台", "market": "SH"},
            {"code": "000858", "name": "五粮液", "market": "SZ"}
        ]
    }
}
```

### 选股条件
```json
{
    "selection_criteria": {
        "fundamentals": {
            "pe_ratio_max": 30,
            "pb_ratio_max": 5,
            "roe_min": 10
        },
        "technicals": {
            "ma5_above_ma20": true,
            "rsi_min": 30,
            "rsi_max": 70
        }
    }
}
```

## 定时任务

已配置 cron 任务（通过 `setup_cron.sh` 设置）：

- **15:30** - 每日选股（交易日）
- **9-11 点/13-15 点** - 每 5 分钟盘中监控

## 飞书通知

配置 `config.json` 中的飞书信息：
```json
{
    "feishu": {
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
        "user_id": "ou_xxx"
    }
}
```

## 数据源

- **A 股**：AKShare（免费，实时）
- **港股**：AKShare（免费，实时）
- **财务数据**：AKShare（季报更新）

## 注意事项

⚠️ **重要提醒**：
1. 仅供参考，不构成投资建议
2. 免费数据可能有延迟
3. 个人使用，请勿对外荐股
4. 投资有风险，决策需谨慎

## 相关文件

- `scripts/stock_selector.py` - 选股策略主程序
- `scripts/stock_monitor.py` - 盘中监控程序
- `scripts/feishu_notifier.py` - 飞书通知模块
- `config.json` - 配置文件

## 常见用法

**用户说**："帮我选股"
→ 运行：`python ~/stock-monitor/stock_selector.py`

**用户说**："看看茅台现在多少钱"
→ 运行：`python ~/stock-monitor/stock_monitor.py test`

**用户说**："设置股价提醒"
→ 编辑 `config.json` 中的 `watchlist` 和 `price_alerts`

**用户说**："查看今天的选股结果"
→ 读取：`~/stock-monitor/selection_*.json`（最新文件）
