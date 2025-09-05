#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
玻璃位策略模块
基于价格支撑阻力位的交易策略
"""

from tqsdk import TargetPosTask
from framework.quant_framework import StrategyBase

class GlassPositionStrategy(StrategyBase):
    """
    玻璃位策略
    基于价格支撑阻力位的交易策略
    通过计算一定时间窗口内的价格波动范围来确定支撑和阻力位
    """
    def __init__(self, window_size=20, threshold=0.5, kline_period=60*60*24):
        """
        初始化玻璃位策略
        
        Args:
            window_size: 计算支撑阻力位的窗口大小，默认为20
            threshold: 突破阈值百分比，默认为0.5%，当价格突破支撑或阻力位一定百分比时触发交易
            kline_period: K线周期，单位为秒，默认为日线(60*60*24)
        """
        super().__init__()
        self.window_size = window_size
        self.threshold = threshold  # 百分比，如0.5表示0.5%
        self.kline_period = kline_period
        self.klines = None
        self.target_pos = None
        self.position = 0
        self.resistance_level = None  # 阻力位
        self.support_level = None  # 支撑位
        
    def initialize(self, api, symbol):
        """
        初始化策略
        
        Args:
            api: TqApi实例
            symbol: 交易品种代码
        """
        super().initialize(api, symbol)
        
        # 获取K线数据
        self.klines = api.get_kline_serial(symbol, self.kline_period)
        
        # 创建TargetPosTask用于自动调整持仓
        self.target_pos = TargetPosTask(api, symbol)
        
        # 打印策略参数
        print(f"玻璃位策略参数: 窗口大小={self.window_size}, 突破阈值={self.threshold}%")
        
    def run(self):
        """
        运行策略
        """
        while True:
            # 等待K线更新
            self.api.wait_update()
            
            # 如果K线最后一根发生变化
            if self.api.is_changing(self.klines.iloc[-1], "datetime"):
                # 确保有足够的数据计算支撑阻力位
                if len(self.klines) >= self.window_size:
                    # 计算支撑阻力位
                    self._calculate_support_resistance()
                    # 生成交易信号
                    self._generate_signals()
                
                # 更新性能指标
                self.update_performance()
    
    def _calculate_support_resistance(self):
        """
        计算支撑位和阻力位
        使用最近window_size根K线的最高价和最低价
        """
        # 检查数据有效性
        if len(self.klines) < self.window_size:
            return
        
        # 取最近window_size根K线
        recent_klines = self.klines.iloc[-self.window_size:]
        
        # 计算阻力位（最高价）
        self.resistance_level = recent_klines.high.max()
        
        # 计算支撑位（最低价）
        self.support_level = recent_klines.low.min()
    
    def _generate_signals(self):
        """
        生成交易信号
        当价格突破阻力位一定百分比时买入
        当价格跌破支撑位一定百分比时卖出
        """
        # 获取当前价格
        current_price = self.klines.iloc[-1].close
        
        # 计算阈值的价格值
        price_threshold = current_price * (self.threshold / 100)
        
        # 买入信号：价格突破阻力位加上阈值
        if current_price > self.resistance_level + price_threshold:
            if self.position <= 0:
                print(f"突破阻力位信号: 买入 {self.symbol}, 价格: {current_price:.2f}, 阻力位: {self.resistance_level:.2f}")
                self.target_pos.set_target_volume(1)  # 设置目标持仓为1手
                self.position = 1
                self.trade_count += 1
        
        # 卖出信号：价格跌破支撑位减去阈值
        elif current_price < self.support_level - price_threshold:
            if self.position >= 0:
                print(f"跌破支撑位信号: 卖出 {self.symbol}, 价格: {current_price:.2f}, 支撑位: {self.support_level:.2f}")
                self.target_pos.set_target_volume(-1)  # 设置目标持仓为-1手
                self.position = -1
                self.trade_count += 1