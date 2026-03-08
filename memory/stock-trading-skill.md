# OpenClaw 股票交易 Skill

## 📈 技能位置
`~/.openclaw/skills/stock-trading/`

## ✅ 已完成

1. **Skill 结构创建**
   - SKILL.md 配置文件
   - 使用说明文档

2. **功能设计**
   - 股票行情查询（A 股/美股/港股）
   - 股票代码搜索
   - 财经新闻聚合
   - 简单技术分析

3. **数据源**
   - 新浪财经（A 股实时）
   - Yahoo Finance（美股/港股）
   - 网络搜索补充

4. **登记到 Skills 发现库**
   - ✅ 已记录到多维表格
   - 链接：https://my.feishu.cn/base/RmrNb1JWkaAAXSsFwj3cCw1rnYc

## 🔧 使用方式

### 方法 1：直接对话查询

```
查询 AAPL 股价
腾讯控股行情
茅台股票价格
搜索 宁德时代
```

### 方法 2：使用 Skill 调用

Skill 会自动识别股票相关请求并调用相应的工具。

## 📊 示例输出

```
📈 贵州茅台 (600519)
市场：A 股
当前价格：1680.50
涨跌：🔺 +15.30 (+0.92%)
最高：1695.00
最低：1665.20
开盘：1670.00
昨收：1665.20
成交量：1,234,567
更新时间：2026-03-08 15:00:00
```

## 🎯 下一步优化

1. **配置 Brave API Key**（用于 web_search）
   - 访问 https://brave.com/search/api/
   - 申请免费 API Key（每天 2000 次）
   - 在 OpenClaw 配置中添加

2. **测试数据源**
   - 验证新浪财经 API
   - 验证 Yahoo Finance
   - 测试响应时间

3. **添加更多功能**
   - K 线数据可视化
   - 技术指标计算
   - 股价提醒功能

## 📝 配置文件位置

- Skill 配置：`~/.openclaw/skills/stock-trading/SKILL.md`
- 使用文档：`~/.openclaw/skills/stock-trading/README.md`

---

*创建日期：2026-03-08*
*状态：✅ 已完成基础版本*
