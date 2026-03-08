#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票盘中监控系统
实时监控重点股票价格，推送提醒
"""

import json
import time
import akshare as ak
import pandas as pd
from datetime import datetime, time as dt_time
from typing import List, Dict, Optional
from feishu_notifier import FeishuNotifier, load_config


class StockMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.watchlist = config.get("watchlist", {}).get("stocks", [])
        self.alert_config = config.get("price_alerts", {})
        self.trading_hours = config.get("trading_hours", {})
        self.notifier = FeishuNotifier(
            webhook_url=config.get("feishu", {}).get("webhook_url", ""),
            user_id=config.get("feishu", {}).get("user_id", "")
        )
        
        # 记录上次价格（用于检测变化）
        self.last_prices = {}
        
        # 提醒冷却时间（避免重复提醒）
        self.alert_cooldown = {}
        self.cooldown_seconds = 600  # 10 分钟冷却
    
    def is_trading_time(self) -> bool:
        """判断是否在交易时间"""
        now = datetime.now().time()
        
        morning_start = dt_time.fromisoformat(self.trading_hours.get("morning_start", "09:30"))
        morning_end = dt_time.fromisoformat(self.trading_hours.get("morning_end", "11:30"))
        afternoon_start = dt_time.fromisoformat(self.trading_hours.get("afternoon_start", "13:00"))
        afternoon_end = dt_time.fromisoformat(self.trading_hours.get("afternoon_end", "15:00"))
        
        is_morning = morning_start <= now <= morning_end
        is_afternoon = afternoon_start <= now <= afternoon_end
        
        # 周末不监控
        is_weekday = datetime.now().weekday() < 5
        
        return is_weekday and (is_morning or is_afternoon)
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict]:
        """获取实时价格"""
        try:
            # 获取实时行情
            if symbol.startswith("6"):
                symbol_full = f"sh{symbol}"
            else:
                symbol_full = f"sz{symbol}"
            
            data = ak.stock_zh_a_spot_em()
            stock_data = data[data['代码'] == symbol]
            
            if len(stock_data) == 0:
                return None
            
            row = stock_data.iloc[0]
            return {
                "code": symbol,
                "name": row.get('名称', ''),
                "price": float(row.get('最新价', 0)),
                "change_percent": float(row.get('涨跌幅', 0)),
                "change_amount": float(row.get('涨跌额', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "open": float(row.get('今开', 0)),
                "prev_close": float(row.get('昨收', 0)),
                "volume": float(row.get('成交量', 0)),
                "turnover": float(row.get('成交额', 0))
            }
        except Exception as e:
            print(f"[获取价格失败 {symbol}] {e}")
            return None
    
    def get_hk_stock_price(self, symbol: str) -> Optional[Dict]:
        """获取港股实时价格"""
        try:
            # 港股代码格式转换
            if symbol.startswith("0") and symbol.endswith(".HK"):
                symbol_clean = symbol.replace(".HK", "")
            else:
                symbol_clean = symbol
            
            data = ak.stock_hk_spot()
            stock_data = data[data['代码'] == symbol_clean]
            
            if len(stock_data) == 0:
                return None
            
            row = stock_data.iloc[0]
            return {
                "code": symbol,
                "name": row.get('名称', ''),
                "price": float(row.get('最新价', 0)),
                "change_percent": float(row.get('涨跌幅', 0)),
                "currency": "HKD"
            }
        except Exception as e:
            print(f"[获取港股价格失败 {symbol}] {e}")
            return None
    
    def check_price_alert(self, stock: Dict) -> Optional[str]:
        """检查价格是否触发提醒"""
        code = stock['code']
        current_price = stock['price']
        change_percent = stock.get('change_percent', 0)
        
        rise_threshold = self.alert_config.get("rise_threshold", 3.0)
        fall_threshold = self.alert_config.get("fall_threshold", -3.0)
        
        # 检查冷却时间
        now = time.time()
        if code in self.alert_cooldown:
            if now - self.alert_cooldown[code] < self.cooldown_seconds:
                return None
        
        # 检查涨跌幅
        alert_type = None
        if change_percent >= rise_threshold:
            alert_type = "rise"
        elif change_percent <= fall_threshold:
            alert_type = "fall"
        
        if alert_type:
            # 设置冷却
            self.alert_cooldown[code] = now
            
            # 生成提醒消息
            message = self.notifier.format_stock_alert(
                {"code": code, "name": stock['name']},
                current_price,
                change_percent,
                alert_type
            )
            
            return message
        
        return None
    
    def check_price_change(self, stock: Dict) -> Optional[str]:
        """检查价格大幅变化"""
        code = stock['code']
        current_price = stock['price']
        
        # 首次记录价格
        if code not in self.last_prices:
            self.last_prices[code] = current_price
            return None
        
        last_price = self.last_prices[code]
        change = ((current_price - last_price) / last_price) * 100
        
        # 更新价格
        self.last_prices[code] = current_price
        
        # 检查是否有显著变化（超过 1%）
        if abs(change) >= 1.0:
            direction = "上涨" if change > 0 else "下跌"
            message = f"""📊 **{stock['name']} ({code})** 快速{direction}

💰 当前价格：¥{current_price:.2f}
📈 变化：{change:+.2f}%（上次：¥{last_price:.2f}）
⏰ 时间：{datetime.now().strftime('%H:%M:%S')}

💡 建议：关注成交量变化，判断是否为有效突破
"""
            return message
        
        return None
    
    def monitor_once(self) -> List[str]:
        """执行一次监控"""
        alerts = []
        
        for stock in self.watchlist:
            code = stock['code']
            
            # 获取价格
            if stock.get('market') == 'HK':
                price_data = self.get_hk_stock_price(code)
            else:
                price_data = self.get_realtime_price(code)
            
            if not price_data:
                continue
            
            # 检查涨跌幅提醒
            alert = self.check_price_alert(price_data)
            if alert:
                alerts.append(alert)
            
            # 检查价格变化
            change_alert = self.check_price_change(price_data)
            if change_alert:
                alerts.append(change_alert)
        
        return alerts
    
    def run(self, interval: int = None):
        """运行监控"""
        if interval is None:
            interval = self.alert_config.get("check_interval_seconds", 300)
        
        print(f"\n{'='*50}")
        print(f"👁️ 股票盘中监控系统启动")
        print(f"{'='*50}")
        print(f"监控股票：{len(self.watchlist)}只")
        print(f"检查间隔：{interval}秒")
        print(f"交易时间：{self.trading_hours.get('morning_start', '09:30')}-{self.trading_hours.get('afternoon_end', '15:00')}")
        print(f"按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                now = datetime.now()
                
                # 检查是否在交易时间
                if self.is_trading_time():
                    print(f"[{now.strftime('%H:%M:%S')}] 监控中...")
                    
                    alerts = self.monitor_once()
                    
                    for alert in alerts:
                        print(f"\n🔔 触发提醒:")
                        print(alert)
                        self.notifier.send_text(alert, "价格提醒")
                
                else:
                    next_trading = self._get_next_trading_time()
                    print(f"[{now.strftime('%H:%M:%S')}] 非交易时间，下次监控：{next_trading}")
                
                # 等待
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n[监控停止] 用户中断")
    
    def _get_next_trading_time(self) -> str:
        """获取下次交易时间"""
        now = datetime.now()
        
        # 如果是周末
        if now.weekday() >= 5:
            return "下周一 09:30"
        
        # 如果已过今日交易时间
        if now.hour >= 15:
            return "明日 09:30"
        
        # 如果在中休时间
        if now.hour >= 11 and now.minute >= 30 and now.hour < 13:
            return "今日 13:00"
        
        return "今日 09:30"
    
    def run_once(self) -> List[str]:
        """只执行一次监控（用于测试）"""
        print(f"\n[单次监控] 开始检查 {len(self.watchlist)} 只股票...")
        alerts = self.monitor_once()
        
        if alerts:
            print(f"[单次监控] 触发 {len(alerts)} 个提醒")
            for alert in alerts:
                self.notifier.send_text(alert, "价格提醒")
        else:
            print("[单次监控] 无触发提醒")
        
        return alerts


def main():
    """主函数"""
    import sys
    
    config = load_config()
    monitor = StockMonitor(config)
    
    # 命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # 单次监控
            monitor.run_once()
        elif sys.argv[1] == "test":
            # 测试模式
            print("[测试模式] 检查所有关注股票...")
            for stock in monitor.watchlist:
                price = monitor.get_realtime_price(stock['code'])
                if price:
                    print(f"✓ {price['name']} ({price['code']}): ¥{price['price']:.2f} ({price['change_percent']:+.2f}%)")
                else:
                    print(f"✗ {stock['name']} ({stock['code']}): 获取失败")
        else:
            print("用法：python stock_monitor.py [once|test]")
    else:
        # 持续监控
        monitor.run()


if __name__ == "__main__":
    main()
