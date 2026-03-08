#!/bin/bash
# 设置定时任务脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=$(which python3)

echo "🔧 设置股票监控定时任务..."
echo "脚本目录：$SCRIPT_DIR"
echo "Python: $PYTHON"

# 创建日志目录
mkdir -p $SCRIPT_DIR/logs

# 添加 cron 任务
(crontab -l 2>/dev/null; cat << EOF
# 股票监控系统定时任务

# 每个交易日 15:30 运行选股（收盘后）
30 15 * * 1-5 cd $SCRIPT_DIR && $PYTHON stock_selector.py >> $SCRIPT_DIR/logs/selector.log 2>&1

# 盘中监控（每 5 分钟检查一次，仅交易日）
*/5 9-11 * * 1-5 cd $SCRIPT_DIR && $PYTHON stock_monitor.py once >> $SCRIPT_DIR/logs/monitor.log 2>&1
*/5 13-15 * * 1-5 cd $SCRIPT_DIR && $PYTHON stock_monitor.py once >> $SCRIPT_DIR/logs/monitor.log 2>&1
EOF
) | crontab -

echo ""
echo "✅ 定时任务设置完成！"
echo ""
echo "查看定时任务：crontab -l"
echo "查看选股日志：tail -f $SCRIPT_DIR/logs/selector.log"
echo "查看监控日志：tail -f $SCRIPT_DIR/logs/monitor.log"
echo ""
echo "📋 定时任务说明："
echo "  - 每个交易日 15:30 自动选股并推送结果"
echo "  - 交易日 9-11 点、13-15 点，每 5 分钟监控一次重点股票"
