#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量化交易框架基类
提供回测、策略运行的基本结构
"""

from datetime import date
from tqsdk import TqApi, TqAuth, TqBacktest, TqSim

class QuantFramework:
    """
    量化交易框架基类
    """
    def __init__(self):
        """
        初始化量化交易框架
        """
        self.api = None
        self.strategy = None
        self.symbol = None
        self.start_date = None
        self.end_date = None
        self.initial_capital = None
        self.auth = None
    
    def initialize(self, symbol, start_date, end_date, initial_capital=100000, tq_account=None, tq_password=None):
        """
        初始化回测参数
        
        Args:
            symbol: 交易品种代码
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金，默认为100000
            tq_account: 天勤账户，默认为None
            tq_password: 天勤密码，默认为None
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # 设置认证信息
        if tq_account and tq_password:
            self.auth = TqAuth(tq_account, tq_password)
        else:
            self.auth = None
    
    def set_strategy(self, strategy):
        """
        设置交易策略
        
        Args:
            strategy: 交易策略实例
        """
        self.strategy = strategy
        
    def run_backtest(self):
        """
        运行回测
        """
        if not self.strategy:
            raise ValueError("请先设置交易策略")
        
        if not self.symbol or not self.start_date or not self.end_date:
            raise ValueError("请先初始化回测参数")
        
        print(f"开始回测 {self.symbol} 策略...")
        print(f"回测区间: {self.start_date} 至 {self.end_date}")
        print(f"初始资金: {self.initial_capital}")
        
        try:
            # 创建API实例，设置回测模式
            self.api = TqApi(
                TqSim(init_balance=self.initial_capital), 
                auth=self.auth, 
                backtest=TqBacktest(start_dt=self.start_date, end_dt=self.end_date)
            )
            
            # 初始化策略
            self.strategy.initialize(self.api, self.symbol)
            
            # 运行策略
            self.strategy.run()
            
            # 输出回测结果
            self._output_results()
            
        except Exception as e:
            print(f"回测过程中出现错误: {e}")
        finally:
            # 关闭API实例
            if self.api:
                self.api.close()
    
    def _output_results(self):
        """
        输出回测结果
        """
        if self.api:
            # 获取账户信息
            account = self.api.get_account()
            print(f"\n回测结果:")
            print(f"最终资金: {account.balance:.2f}")
            print(f"最大回撤: {(self.strategy.max_drawdown * 100):.2f}%")
            print(f"交易次数: {self.strategy.trade_count}")
            
            # 计算收益率
            if self.initial_capital > 0:
                total_return = (account.balance - self.initial_capital) / self.initial_capital * 100
                print(f"总收益率: {total_return:.2f}%")

class StrategyBase:
    """
    策略基类
    所有具体策略都应该继承这个类
    """
    def __init__(self):
        """
        初始化策略
        """
        self.api = None
        self.symbol = None
        self.trade_count = 0
        self.max_drawdown = 0
        self.highest_balance = 0
        
    def initialize(self, api, symbol):
        """
        初始化策略
        
        Args:
            api: TqApi实例
            symbol: 交易品种代码
        """
        self.api = api
        self.symbol = symbol
        self.highest_balance = api.get_account().balance
        
    def run(self):
        """
        运行策略
        需要在子类中实现
        """
        raise NotImplementedError("子类必须实现run方法")
        
    def update_performance(self):
        """
        更新策略性能指标
        """
        if self.api:
            account = self.api.get_account()
            
            # 更新最高资金
            if account.balance > self.highest_balance:
                self.highest_balance = account.balance
            
            # 计算最大回撤
            if self.highest_balance > 0:
                current_drawdown = (self.highest_balance - account.balance) / self.highest_balance
                if current_drawdown > self.max_drawdown:
                    self.max_drawdown = current_drawdown