#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
玻璃期货回测策略 - 均线交叉策略
'''

from datetime import date
from tqsdk import TqApi, TqAuth, TqBacktest, TqSim, TargetPosTask
from tqsdk.ta import MA

# 策略参数
SYMBOL = "SHFE.FG2401"  # 玻璃期货，上海期货交易所，使用具体合约代码
SHORT_PERIOD = 5  # 短周期均线
LONG_PERIOD = 20  # 长周期均线
INITIAL_CAPITAL = 100000  # 初始资金

# 设置回测参数
BACKTEST_START_DATE = date(2022, 1, 1)  # 回测开始日期
BACKTEST_END_DATE = date(2023, 12, 31)  # 回测结束日期

def run_strategy():
    '''
    运行策略
    '''
    print(f"开始回测 {SYMBOL} 均线交叉策略...")
    print(f"参数: 短周期={SHORT_PERIOD}, 长周期={LONG_PERIOD}")
    print(f"回测区间: {BACKTEST_START_DATE} 至 {BACKTEST_END_DATE}")
    
    # 创建API实例，设置回测模式
    # 注意：使用天勤量化SDK需要注册天勤账户，请在以下网址注册：https://account.shinnytech.com/
    # 请填写您的天勤账户和密码
    
    api = TqApi(TqSim(init_balance=INITIAL_CAPITAL), 
               auth=TqAuth("您的天勤账户", "您的天勤密码"), 
               backtest=TqBacktest(start_dt=BACKTEST_START_DATE, end_dt=BACKTEST_END_DATE))
    
    # 获取玻璃期货的K线数据
    klines = api.get_kline_serial(SYMBOL, 60*60*24)  # 日线
    
    # 计算均线
    short_ma = MA(klines, SHORT_PERIOD)
    long_ma = MA(klines, LONG_PERIOD)
    
    # 创建 TargetPosTask 用于自动调整持仓
    target_pos = TargetPosTask(api, SYMBOL)
    
    # 持仓状态，初始为空仓
    position = 0
    
    # 策略循环
    while True:
        # 等待K线更新
        api.wait_update()
        
        # 如果K线最后一根发生变化
        if api.is_changing(klines.iloc[-1], "datetime"):
            # 计算信号
            short_ma_value = short_ma.iloc[-1]
            long_ma_value = long_ma.iloc[-1]
            short_ma_prev = short_ma.iloc[-2]
            long_ma_prev = long_ma.iloc[-2]
            
            # 金叉信号: 短周期均线从下方穿过长周期均线
            if short_ma_prev <= long_ma_prev and short_ma_value > long_ma_value:
                # 买入信号
                if position <= 0:
                    print(f"金叉信号: 买入 {SYMBOL}, 价格: {klines.iloc[-1].close}")
                    target_pos.set_target_volume(1)  # 设置目标持仓为1手
                    position = 1
            
            # 死叉信号: 短周期均线从上方穿过长周期均线
            elif short_ma_prev >= long_ma_prev and short_ma_value < long_ma_value:
                # 卖出信号
                if position >= 0:
                    print(f"死叉信号: 卖出 {SYMBOL}, 价格: {klines.iloc[-1].close}")
                    target_pos.set_target_volume(-1)  # 设置目标持仓为-1手
                    position = -1
    
    # 关闭API实例
    api.close()

if __name__ == "__main__":
    try:
        run_strategy()
    except Exception as e:
        print(f"策略运行出错: {e}")