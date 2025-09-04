#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
均线策略模块
实现基于均线交叉的交易策略
"""

from tqsdk import TargetPosTask
from tqsdk.ta import MA
from framework.quant_framework import StrategyBase

class MovingAverageStrategy(StrategyBase):
    """
    均线交叉策略
    基于短周期均线和长周期均线的交叉信号进行交易
    """
    def __init__(self, short_period=5, long_period=20, kline_period=60*60*24):
        """
        初始化均线策略
        
        Args:
            short_period: 短周期均线参数，默认为5
            long_period: 长周期均线参数，默认为20
            kline_period: K线周期，单位为秒，默认为日线(60*60*24)
        """
        super().__init__()
        self.short_period = short_period
        self.long_period = long_period
        self.kline_period = kline_period
        self.klines = None
        self.short_ma = None
        self.long_ma = None
        self.target_pos = None
        self.position = 0
        
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
        print(f"均线策略参数: 短周期={self.short_period}, 长周期={self.long_period}")
        
    def run(self):
        """
        运行策略
        """
        while True:
            # 等待K线更新
            self.api.wait_update()
            
            # 如果K线最后一根发生变化
            if self.api.is_changing(self.klines.iloc[-1], "datetime"):
                # 确保有足够的数据计算均线
                if len(self.klines) >= self.long_period:
                    # 计算均线
                    self.short_ma = MA(self.klines, self.short_period)
                    self.long_ma = MA(self.klines, self.long_period)
                    
                    # 计算信号
                    self._generate_signals()
                    
                # 更新性能指标
                self.update_performance()
    
    def _generate_signals(self):
        """
        生成交易信号
        """
        # 确保均线数据有效
        if len(self.short_ma) < 2 or len(self.long_ma) < 2:
            return
        
        # 获取当前和前一期的均线值
        try:
            short_ma_value = self.short_ma.iloc[-1]
            long_ma_value = self.long_ma.iloc[-1]
            short_ma_prev = self.short_ma.iloc[-2]
            long_ma_prev = self.long_ma.iloc[-2]
        except IndexError:
            return
        
        # 金叉信号: 短周期均线从下方穿过长周期均线
        if short_ma_prev <= long_ma_prev and short_ma_value > long_ma_value:
            self._buy_signal()
        
        # 死叉信号: 短周期均线从上方穿过长周期均线
        elif short_ma_prev >= long_ma_prev and short_ma_value < long_ma_value:
            self._sell_signal()
    
    def _buy_signal(self):
        """
        买入信号处理
        """
        if self.position <= 0:
            current_price = self.klines.iloc[-1].close
            print(f"金叉信号: 买入 {self.symbol}, 价格: {current_price:.2f}")
            self.target_pos.set_target_volume(1)  # 设置目标持仓为1手
            self.position = 1
            self.trade_count += 1
    
    def _sell_signal(self):
        """
        卖出信号处理
        """
        if self.position >= 0:
            current_price = self.klines.iloc[-1].close
            print(f"死叉信号: 卖出 {self.symbol}, 价格: {current_price:.2f}")
            self.target_pos.set_target_volume(-1)  # 设置目标持仓为-1手
            self.position = -1
            self.trade_count += 1

class MultipleMovingAverageStrategy(StrategyBase):
    """
    多均线策略
    基于三条均线的组合信号进行交易
    """
    def __init__(self, short_period=5, mid_period=10, long_period=20, kline_period=60*60*24):
        """
        初始化多均线策略
        
        Args:
            short_period: 短周期均线参数，默认为5
            mid_period: 中周期均线参数，默认为10
            long_period: 长周期均线参数，默认为20
            kline_period: K线周期，单位为秒，默认为日线(60*60*24)
        """
        super().__init__()
        self.short_period = short_period
        self.mid_period = mid_period
        self.long_period = long_period
        self.kline_period = kline_period
        self.klines = None
        self.short_ma = None
        self.mid_ma = None
        self.long_ma = None
        self.target_pos = None
        self.position = 0
        
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
        print(f"多均线策略参数: 短周期={self.short_period}, 中周期={self.mid_period}, 长周期={self.long_period}")
        
    def run(self):
        """
        运行策略
        """
        while True:
            # 等待K线更新
            self.api.wait_update()
            
            # 如果K线最后一根发生变化
            if self.api.is_changing(self.klines.iloc[-1], "datetime"):
                # 确保有足够的数据计算均线
                if len(self.klines) >= self.long_period:
                    # 计算均线
                    self.short_ma = MA(self.klines, self.short_period)
                    self.mid_ma = MA(self.klines, self.mid_period)
                    self.long_ma = MA(self.klines, self.long_period)
                    
                    # 计算信号
                    self._generate_signals()
                    
                # 更新性能指标
                self.update_performance()
    
    def _generate_signals(self):
        """
        生成交易信号
        """
        # 确保均线数据有效
        if len(self.short_ma) < 2 or len(self.mid_ma) < 2 or len(self.long_ma) < 2:
            return
        
        # 获取当前和前一期的均线值
        try:
            short_ma_value = self.short_ma.iloc[-1]
            mid_ma_value = self.mid_ma.iloc[-1]
            long_ma_value = self.long_ma.iloc[-1]
            short_ma_prev = self.short_ma.iloc[-2]
            mid_ma_prev = self.mid_ma.iloc[-2]
            long_ma_prev = self.long_ma.iloc[-2]
        except IndexError:
            return
        
        # 买入信号: 短周期均线在中周期均线之上，且中周期均线在长周期均线之上
        if (short_ma_value > mid_ma_value > long_ma_value and 
            not (short_ma_prev > mid_ma_prev > long_ma_prev)):
            self._buy_signal()
        
        # 卖出信号: 短周期均线在中周期均线之下，且中周期均线在长周期均线之下
        elif (short_ma_value < mid_ma_value < long_ma_value and 
              not (short_ma_prev < mid_ma_prev < long_ma_prev)):
            self._sell_signal()
    
    def _buy_signal(self):
        """
        买入信号处理
        """
        if self.position <= 0:
            current_price = self.klines.iloc[-1].close
            print(f"均线多头排列: 买入 {self.symbol}, 价格: {current_price:.2f}")
            self.target_pos.set_target_volume(1)  # 设置目标持仓为1手
            self.position = 1
            self.trade_count += 1
    
    def _sell_signal(self):
        """
        卖出信号处理
        """
        if self.position >= 0:
            current_price = self.klines.iloc[-1].close
            print(f"均线空头排列: 卖出 {self.symbol}, 价格: {current_price:.2f}")
            self.target_pos.set_target_volume(-1)  # 设置目标持仓为-1手
            self.position = -1
            self.trade_count += 1