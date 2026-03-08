#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股选股策略 - 盘后运行
混合策略：基本面 + 技术面
"""

import json
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from feishu_notifier import FeishuNotifier, load_config


class StockSelector:
    def __init__(self, config: Dict):
        self.config = config
        self.criteria = config.get("selection_criteria", {})
        self.notifier = FeishuNotifier(
            webhook_url=config.get("feishu", {}).get("webhook_url", ""),
            user_id=config.get("feishu", {}).get("user_id", "")
        )
    
    def get_all_stocks(self) -> pd.DataFrame:
        """获取全市场 A 股列表"""
        print("[选股] 获取 A 股列表...")
        try:
            # 获取沪深 A 股列表
            stocks_sh = ak.stock_info_a_code_name()
            return stocks_sh
        except Exception as e:
            print(f"[获取股票列表失败] {e}")
            return pd.DataFrame()
    
    def get_stock_basic_info(self, symbol: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            # 实时行情
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
                "change": float(row.get('涨跌幅', 0)),
                "volume": float(row.get('成交量', 0)),
                "turnover": float(row.get('成交额', 0)),
                "market_cap": float(row.get('总市值', 0)),
                "pe": float(row.get('市盈率 - 动态', 0)),
                "pb": float(row.get('市净率', 0))
            }
        except Exception as e:
            print(f"[获取股票信息失败 {symbol}] {e}")
            return None
    
    def get_financial_indicators(self, symbol: str) -> Optional[Dict]:
        """获取财务指标"""
        try:
            # 获取财务指标
            data = ak.stock_financial_analysis_indicator(symbol=symbol)
            if len(data) == 0:
                return None
            
            latest = data.iloc[0]
            return {
                "roe": float(latest.get('净资产收益率 (%)', 0)),
                "gross_margin": float(latest.get('销售毛利率 (%)', 0)),
                "debt_ratio": float(latest.get('资产负债率 (%)', 0)),
                "revenue_growth": float(latest.get('主营业务收入增长率 (%)', 0))
            }
        except Exception as e:
            print(f"[获取财务指标失败 {symbol}] {e}")
            return None
    
    def get_technical_indicators(self, symbol: str, period: str = "60") -> Optional[Dict]:
        """获取技术指标"""
        try:
            # 获取历史行情
            if symbol.startswith("6"):
                df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")
            
            if len(df) < 20:
                return None
            
            # 计算均线
            df['MA5'] = df['收盘'].rolling(5).mean()
            df['MA20'] = df['收盘'].rolling(20).mean()
            df['MA60'] = df['收盘'].rolling(60).mean()
            
            # 计算 RSI
            delta = df['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 计算 MACD
            exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
            exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            return {
                "ma5": float(latest['MA5']),
                "ma20": float(latest['MA20']),
                "ma60": float(latest['MA60']),
                "rsi": float(latest['RSI']) if not np.isnan(latest['RSI']) else 50,
                "macd": float(latest['MACD']) if not np.isnan(latest['MACD']) else 0,
                "macd_signal": float(latest['Signal']) if not np.isnan(latest['Signal']) else 0,
                "ma5_above_ma20": latest['MA5'] > latest['MA20'],
                "golden_cross": latest['MA5'] > latest['MA20'] and prev['MA5'] <= prev['MA20']
            }
        except Exception as e:
            print(f"[获取技术指标失败 {symbol}] {e}")
            return None
    
    def check_fundamentals(self, info: Dict, financial: Dict) -> tuple:
        """检查基本面条件"""
        criteria = self.criteria.get("fundamentals", {})
        reasons = []
        
        # PE 检查
        pe_max = criteria.get("pe_ratio_max", 30)
        if info.get('pe', 0) > pe_max or info.get('pe', 0) <= 0:
            return False, [f"PE({info.get('pe', 0):.1f}) 超出范围"]
        reasons.append(f"PE 合理 ({info.get('pe', 0):.1f})")
        
        # PB 检查
        pb_max = criteria.get("pb_ratio_max", 5)
        if info.get('pb', 0) > pb_max or info.get('pb', 0) <= 0:
            return False, [f"PB({info.get('pb', 0):.1f}) 超出范围"]
        reasons.append(f"PB 合理 ({info.get('pb', 0):.1f})")
        
        # ROE 检查
        roe_min = criteria.get("roe_min", 10)
        if financial.get('roe', 0) < roe_min:
            return False, [f"ROE({financial.get('roe', 0):.1f}%) 低于{roe_min}%"]
        reasons.append(f"ROE 良好 ({financial.get('roe', 0):.1f}%)")
        
        # 市值检查
        cap_min = criteria.get("market_cap_min", 100)
        cap_max = criteria.get("market_cap_max", 5000)
        market_cap = info.get('market_cap', 0) / 100000000  # 转换为亿
        if market_cap < cap_min or market_cap > cap_max:
            return False, [f"市值 ({market_cap:.1f}亿) 超出范围"]
        reasons.append(f"市值适中 ({market_cap:.1f}亿)")
        
        return True, reasons
    
    def check_technicals(self, technical: Dict) -> tuple:
        """检查技术面条件"""
        criteria = self.criteria.get("technicals", {})
        reasons = []
        
        # 均线检查
        if criteria.get("ma5_above_ma20", True):
            if not technical.get('ma5_above_ma20', False):
                return False, ["MA5 未站上 MA20"]
            reasons.append("MA5>MA20 多头排列")
        
        # RSI 检查
        rsi = technical.get('rsi', 50)
        rsi_min = criteria.get("rsi_min", 30)
        rsi_max = criteria.get("rsi_max", 70)
        if rsi < rsi_min or rsi > rsi_max:
            return False, [f"RSI({rsi:.1f}) 超出合理区间"]
        reasons.append(f"RSI 合理 ({rsi:.1f})")
        
        # 金叉加分
        if technical.get('golden_cross', False):
            reasons.append("⭐ 金叉信号")
        
        return True, reasons
    
    def select_stocks(self, stock_list: List[str] = None) -> List[Dict]:
        """执行选股"""
        print(f"[选股] 开始选股...")
        selected = []
        
        # 如果没有指定股票列表，获取全市场
        if not stock_list:
            all_stocks = self.get_all_stocks()
            if len(all_stocks) == 0:
                print("[选股] 获取股票列表失败")
                return []
            stock_list = all_stocks['代码'].tolist()[:100]  # 先测试前 100 只
            print(f"[选股] 待筛选股票：{len(stock_list)}只")
        
        for i, symbol in enumerate(stock_list):
            if i % 10 == 0:
                print(f"[选股] 进度：{i}/{len(stock_list)}")
            
            try:
                # 获取基本信息
                info = self.get_stock_basic_info(symbol)
                if not info:
                    continue
                
                # 获取财务指标
                financial = self.get_financial_indicators(symbol)
                if not financial:
                    continue
                
                # 获取技术指标
                technical = self.get_technical_indicators(symbol)
                if not technical:
                    continue
                
                # 基本面检查
                fundamental_pass, fundamental_reasons = self.check_fundamentals(info, financial)
                if not fundamental_pass:
                    continue
                
                # 技术面检查
                technical_pass, technical_reasons = self.check_technicals(technical)
                if not technical_pass:
                    continue
                
                # 通过筛选
                selected_stock = {
                    **info,
                    **financial,
                    **technical,
                    "reason": " | ".join(fundamental_reasons + technical_reasons)
                }
                selected.append(selected_stock)
                print(f"✓ 选中：{info['name']} ({symbol})")
                
            except Exception as e:
                print(f"[处理股票失败 {symbol}] {e}")
                continue
        
        return selected
    
    def run(self, send_notification: bool = True) -> List[Dict]:
        """运行选股并发送通知"""
        print(f"\n{'='*50}")
        print(f"🎯 A 股选股系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 执行选股
        selected = self.select_stocks()
        
        print(f"\n[选股完成] 共选中 {len(selected)} 只股票")
        
        # 发送通知
        if send_notification and selected:
            message = self.notifier.format_selection_result(selected)
            self.notifier.send_text(message, "今日选股结果")
        
        # 保存到文件
        self._save_results(selected)
        
        return selected
    
    def _save_results(self, selected: List[Dict]):
        """保存选股结果"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"selection_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(selected, f, ensure_ascii=False, indent=2)
            print(f"[保存成功] {filename}")
        except Exception as e:
            print(f"[保存失败] {e}")


def main():
    """主函数"""
    config = load_config()
    selector = StockSelector(config)
    selector.run(send_notification=True)


if __name__ == "__main__":
    main()
