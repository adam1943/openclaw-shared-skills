# 📈 A 股选股与监控系统

一个基于 Python 的股票选股和盘中监控系统，支持 A 股和港股。

## 🎯 功能

### 1. 盘后选股（每日 15:30 自动运行）
- **基本面筛选**：PE、PB、ROE、市值等
- **技术面筛选**：均线、MACD、RSI 等
- **混合策略**：综合评估，输出选股理由
- **飞书推送**：选股结果自动发送到飞书

### 2. 盘中监控（交易时间实时运行）
- **价格提醒**：涨跌幅超过阈值时推送
- **快速变化**：检测到快速上涨/下跌时提醒
- **买卖建议**：根据走势给出操作建议
- **冷却机制**：避免重复提醒

## 📦 安装

### 1. 安装依赖

```bash
cd ~/stock-monitor
pip3 install -r requirements.txt
```

### 2. 配置

编辑 `config.json`：

```json
{
    "feishu": {
        "webhook_url": "你的飞书 webhook URL",
        "user_id": "你的飞书用户 ID"
    },
    "watchlist": {
        "stocks": [
            {"code": "600519", "name": "贵州茅台", "market": "SH"},
            {"code": "000858", "name": "五粮液", "market": "SZ"},
            {"code": "300750", "name": "宁德时代", "market": "SZ"}
        ]
    }
}
```

### 3. 设置定时任务

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

## 🚀 使用

### 手动运行选股

```bash
python3 stock_selector.py
```

### 手动运行监控

```bash
# 持续监控（交易时间）
python3 stock_monitor.py

# 单次检查
python3 stock_monitor.py once

# 测试连接
python3 stock_monitor.py test
```

### 查看日志

```bash
# 选股日志
tail -f logs/selector.log

# 监控日志
tail -f logs/monitor.log
```

## 📊 选股策略

### 基本面条件（可配置）
| 指标 | 默认值 | 说明 |
|------|--------|------|
| PE 最大 | 30 | 市盈率上限 |
| PB 最大 | 5 | 市净率上限 |
| ROE 最小 | 10% | 净资产收益率下限 |
| 市值最小 | 100 亿 | 市值下限 |
| 市值最大 | 5000 亿 | 市值上限 |

### 技术面条件（可配置）
| 指标 | 默认值 | 说明 |
|------|--------|------|
| 均线 | MA5>MA20 | 短期均线在长期之上 |
| RSI 范围 | 30-70 | 相对强弱指数合理区间 |
| 成交量 | >1.5 倍 | 量比要求 |

## 🔔 价格提醒

### 触发条件
- **大涨**：涨幅 ≥ 3%（可配置）
- **大跌**：跌幅 ≤ -3%（可配置）
- **快速变化**：5 分钟内变化 ≥ 1%

### 冷却时间
- 同一股票提醒间隔 ≥ 10 分钟（避免刷屏）

## ⚙️ 配置说明

### config.json 完整结构

```json
{
    "feishu": {
        "webhook_url": "",
        "user_id": ""
    },
    "watchlist": {
        "stocks": [
            {"code": "股票代码", "name": "股票名称", "market": "SH/SZ/HK"}
        ]
    },
    "price_alerts": {
        "rise_threshold": 3.0,
        "fall_threshold": -3.0,
        "check_interval_seconds": 300
    },
    "selection_criteria": {
        "fundamentals": {
            "pe_ratio_max": 30,
            "pb_ratio_max": 5,
            "roe_min": 10,
            "market_cap_min": 100,
            "market_cap_max": 5000
        },
        "technicals": {
            "ma5_above_ma20": true,
            "volume_ratio_min": 1.5,
            "rsi_max": 70,
            "rsi_min": 30
        }
    },
    "trading_hours": {
        "morning_start": "09:30",
        "morning_end": "11:30",
        "afternoon_start": "13:00",
        "afternoon_end": "15:00"
    }
}
```

## 📝 定时任务

安装后自动添加以下 cron 任务：

```bash
# 每个交易日 15:30 选股
30 15 * * 1-5 cd ~/stock-monitor && python3 stock_selector.py

# 交易日盘中监控（每 5 分钟）
*/5 9-11 * * 1-5 cd ~/stock-monitor && python3 stock_monitor.py once
*/5 13-15 * * 1-5 cd ~/stock-monitor && python3 stock_monitor.py once
```

## ⚠️ 注意事项

1. **数据源**：使用 AKShare 免费数据，可能有延迟
2. **投资建议**：仅供参考，不构成投资建议
3. **风险提示**：股市有风险，投资需谨慎
4. **合规**：个人使用，请勿对外荐股

## 🔧 故障排查

### 数据获取失败
```bash
# 测试数据源
python3 -c "import akshare as ak; print(ak.stock_zh_a_spot_em())"
```

### 飞书通知失败
- 检查 webhook URL 是否正确
- 检查网络连接
- 查看日志：`tail -f logs/monitor.log`

### 定时任务不执行
```bash
# 检查 cron 服务
systemctl status cron

# 查看 cron 日志
grep CRON /var/log/syslog
```

## 📚 依赖

- **akshare**: 股票数据获取
- **pandas**: 数据处理
- **numpy**: 数值计算
- **requests**: HTTP 请求

## 📄 许可证

MIT License - 个人学习使用

---

**祝投资顺利！📈**
