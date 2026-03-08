#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书通知模块
发送选股结果和价格提醒到飞书
"""

import json
import requests
from datetime import datetime
from typing import Optional, List, Dict


class FeishuNotifier:
    def __init__(self, webhook_url: str = "", user_id: str = ""):
        """
        初始化飞书通知器
        
        Args:
            webhook_url: 飞书机器人 webhook URL（可选）
            user_id: 接收消息的飞书用户 ID（可选）
        """
        self.webhook_url = webhook_url
        self.user_id = user_id
        
        # 如果配置了 OpenClaw，使用 OpenClaw 的消息接口
        self.use_openclaw = False
    
    def send_text(self, content: str, title: str = "股票提醒") -> bool:
        """发送文本消息"""
        message = f"📈 {title}\n\n{content}"
        print(f"[飞书通知] {message}")
        
        # 如果有 webhook，发送到飞书
        if self.webhook_url:
            return self._send_webhook(message)
        
        # 否则打印到控制台
        return True
    
    def send_card(self, title: str, content_list: List[Dict]) -> bool:
        """发送交互式卡片消息"""
        print(f"[飞书卡片] {title}")
        for item in content_list:
            print(f"  - {item.get('key', '')}: {item.get('value', '')}")
        return True
    
    def _send_webhook(self, text: str) -> bool:
        """通过 webhook 发送消息"""
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[飞书通知失败] {e}")
            return False
    
    def format_stock_alert(self, stock: Dict, current_price: float, 
                          change_percent: float, alert_type: str) -> str:
        """格式化股票提醒消息"""
        emoji = "🔴" if change_percent > 0 else "🟢"
        direction = "上涨" if change_percent > 0 else "下跌"
        
        message = f"""{emoji} **{stock['name']} ({stock['code']})** {direction}提醒

💰 当前价格：¥{current_price:.2f}
📊 涨跌幅：{change_percent:+.2f}%
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 建议：{self._get_suggestion(change_percent, alert_type)}
"""
        return message
    
    def format_selection_result(self, selected_stocks: List[Dict]) -> str:
        """格式化选股结果"""
        if not selected_stocks:
            return "😐 今日未选出符合要求的股票"
        
        message = f"""🎯 **今日选股结果** ({len(selected_stocks)}只)
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        for i, stock in enumerate(selected_stocks[:10], 1):  # 最多显示 10 只
            message += f"""{i}. **{stock['name']} ({stock['code']})**
   价格：¥{stock.get('price', 0):.2f} | 涨跌：{stock.get('change', 0):+.2f}%
   PE: {stock.get('pe', 0):.1f} | PB: {stock.get('pb', 0):.1f} | ROE: {stock.get('roe', 0):.1f}%
   理由：{stock.get('reason', '')}

"""
        
        if len(selected_stocks) > 10:
            message += f"... 还有{len(selected_stocks) - 10}只，详见日志\n"
        
        return message
    
    def _get_suggestion(self, change_percent: float, alert_type: str) -> str:
        """根据涨跌幅给出建议"""
        if change_percent > 5:
            return "涨幅较大，注意追高风险，可等待回调"
        elif change_percent > 3:
            return "关注成交量，如有突破可轻仓跟进"
        elif change_percent > 0:
            return "温和上涨，持续观察"
        elif change_percent > -3:
            return "小幅回调，关注支撑位"
        elif change_percent > -5:
            return "跌幅较大，注意风险，不宜盲目抄底"
        else:
            return "大幅下跌，谨慎观望"


def load_config(config_path: str = "config.json") -> Dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[配置加载失败] {e}")
        return {}


if __name__ == "__main__":
    # 测试
    config = load_config()
    notifier = FeishuNotifier(
        webhook_url=config.get("feishu", {}).get("webhook_url", ""),
        user_id=config.get("feishu", {}).get("user_id", "")
    )
    
    test_stock = {"code": "600519", "name": "贵州茅台"}
    message = notifier.format_stock_alert(test_stock, 1800.50, 3.5, "rise")
    notifier.send_text(message)
