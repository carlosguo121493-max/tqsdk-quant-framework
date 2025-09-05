#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于Flask的量化交易策略交互网页
提供策略选择、参数配置、回测运行和结果可视化功能
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import time

# 导入数据库模块
from db import db, FuturesProduct, FuturesContract, init_db, initialize_data

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入量化框架和策略
from framework.quant_framework import QuantFramework, StrategyBase
from strategies.moving_average_strategy import MovingAverageStrategy, MultipleMovingAverageStrategy
# 导入策略配置模块
from strategies.strategy_config import get_all_strategies, get_strategy_params

app = Flask(__name__)

# 初始化数据库
init_db(app)

# 模拟数据生成函数，用于前端展示
def generate_simulation_data(days=252, initial_capital=1000000, strategy_name='简单均线交叉策略', backtest_level='D'):
    """生成模拟回测数据"""
    np.random.seed(42)
    
    # 根据回测级别调整数据点数量
    level_adjustment = {
        'D': 1,      # 日线
        'W': 5,      # 周线
        'M': 20,     # 月线
        '30min': 0.5, # 30分钟线
        '15min': 0.25, # 15分钟线
        '5min': 0.083, # 5分钟线
        '1min': 0.017  # 1分钟线
    }
    
    adj_factor = level_adjustment.get(backtest_level, 1)
    data_points = max(10, int(days * adj_factor))
    
    # 生成基础收益率序列
    base_returns = np.random.normal(0.0005 / adj_factor, 0.02 / np.sqrt(adj_factor), data_points)
    
    # 根据策略调整收益率特征
    if strategy_name == '多均线策略':
        # 多均线策略表现稍好
        base_returns = base_returns * 1.2 + 0.0002 / adj_factor
    elif strategy_name == '玻璃位策略':
        # 玻璃位策略波动性更大
        base_returns = base_returns * 1.5
        # 添加一些趋势
        trend = np.linspace(0, 0.001 * data_points, data_points) * 0.05 / adj_factor
        base_returns = base_returns + trend
    
    # 计算资金曲线
    capital = initial_capital
    equity_curve = [capital]
    
    for r in base_returns:
        capital *= (1 + r)
        equity_curve.append(capital)
    
    # 计算性能指标
    total_return = (equity_curve[-1] / initial_capital - 1) * 100
    
    # 计算日收益率
    daily_returns = np.diff(equity_curve) / equity_curve[:-1]
    
    # 计算夏普率 (假设无风险收益率为0)
    # 根据回测级别调整年化因子
    annual_factor = {
        'D': 252,      # 日线：252个交易日
        'W': 52,       # 周线：52周
        'M': 12,       # 月线：12个月
        '30min': 252 * 24,  # 30分钟线：每天24根
        '15min': 252 * 48,  # 15分钟线：每天48根
        '5min': 252 * 144,  # 5分钟线：每天144根
        '1min': 252 * 720   # 1分钟线：每天720根
    }
    
    sharpe_ratio = np.sqrt(annual_factor.get(backtest_level, 252)) * daily_returns.mean() / (daily_returns.std() + 1e-8)
    
    # 计算最大回撤
    running_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min() * 100
    
    # 计算卡玛比率 (收益率/最大回撤的绝对值)
    calmar_ratio = total_return / (abs(max_drawdown) + 1e-8) if max_drawdown != 0 else 0
    
    # 计算盈亏比
    # 模拟交易次数（为了简化，使用日收益率的符号来判断盈亏）
    winning_trades = daily_returns[daily_returns > 0]
    losing_trades = daily_returns[daily_returns < 0]
    
    # 计算平均盈利和平均亏损
    avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
    avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 0
    
    # 计算盈亏比
    profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
    
    # 生成日期序列，根据回测级别调整频率
    freq_map = {
        'D': 'B',       # 日线：工作日
        'W': 'W-FRI',   # 周线：每周五
        'M': 'BM',      # 月线：每月最后一个工作日
        '30min': '30T', # 30分钟线
        '15min': '15T', # 15分钟线
        '5min': '5T',   # 5分钟线
        '1min': 'T'     # 1分钟线
    }
    
    freq = freq_map.get(backtest_level, 'B')
    end_date = datetime.now()
    
    # 估算需要的时间范围
    if backtest_level in ['1min', '5min', '15min', '30min']:
        # 对于分钟级别的数据，使用较短的时间范围
        start_date = end_date - timedelta(days=int(data_points / 24))  # 假设每天24根K线
    else:
        # 对于日线及以上级别的数据
        start_date = end_date - timedelta(days=int(data_points * 1.5))  # 考虑非交易日
    
    date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # 确保date_range长度与equity_curve匹配
    if len(date_range) < len(equity_curve):
        # 如果交易日少于模拟天数，填充缺失日期
        while len(date_range) < len(equity_curve):
            end_date += timedelta(days=1)
            date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    else:
        # 如果交易日多于模拟天数，截断
        date_range = date_range[:len(equity_curve)]
    
    return {
        'dates': date_range.strftime('%Y-%m-%d').tolist(),
        'equity_curve': equity_curve,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar_ratio,
        'profit_factor': profit_factor,
        'daily_returns': daily_returns.tolist()
    }

def generate_equity_curve_chart(dates, equity_curve):
    """生成资金曲线图并返回base64编码"""
    plt.figure(figsize=(10, 6))
    plt.plot(dates, equity_curve, 'b-', linewidth=2)
    plt.title('资金曲线图', fontsize=14)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('资金量', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 设置x轴日期标签格式
    if len(dates) > 60:
        plt.xticks(dates[::len(dates)//10], rotation=45)
    else:
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # 转换为base64编码
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_drawdown_chart(dates, equity_curve):
    """生成回撤曲线图并返回base64编码"""
    running_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - running_max) / running_max * 100
    
    plt.figure(figsize=(10, 4))
    plt.fill_between(dates, drawdown, 0, where=(drawdown < 0), facecolor='red', alpha=0.5)
    plt.plot(dates, drawdown, 'r-', linewidth=1)
    plt.title('回撤曲线图', fontsize=14)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('回撤百分比 (%)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 设置x轴日期标签格式
    if len(dates) > 60:
        plt.xticks(dates[::len(dates)//10], rotation=45)
    else:
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # 转换为base64编码
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

@app.route('/api/futures_products')
def get_futures_products():
    """从数据库获取所有期货品种"""
    # 从数据库查询期货品种，并按交易所分类
    products = db.session.query(FuturesProduct).order_by(FuturesProduct.exchange, FuturesProduct.name).all()
    
    # 按交易所分类整理数据
    products_by_exchange = {}
    for product in products:
        if product.exchange not in products_by_exchange:
            products_by_exchange[product.exchange] = []
        products_by_exchange[product.exchange].append({
            'id': product.product_id,
            'name': product.name
        })
    
    return jsonify(products_by_exchange)

@app.route('/api/contracts')
def get_contracts():
    """从数据库获取指定品种的所有合约"""
    product_id = request.args.get('product_id', '')
    
    try:
        # 从数据库查询指定产品的所有合约
        contracts = db.session.query(FuturesContract).filter_by(product_id=product_id).all()
        
        # 构建合约列表响应
        contract_list = []
        for contract in contracts:
            contract_list.append({
                'code': contract.code,
                'name': contract.name
            })
        
        return jsonify(contract_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh_products')
def refresh_products():
    """从API拉取最新期货品种数据并更新数据库"""
    try:
        # 在实际应用中，这里应该调用TQSDK API获取最新的期货品种数据
        # 由于这里是模拟环境，我们直接调用initialize_data函数重新初始化数据
        
        # 清空现有数据库中的期货品种和合约数据
        db.session.query(FuturesContract).delete()
        db.session.query(FuturesProduct).delete()
        db.session.commit()
        
        # 重新初始化数据
        initialize_data(app)
        
        return jsonify({'success': True, 'message': '期货品种数据已成功更新'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/strategies')
def get_strategies():
    """获取可用策略列表"""
    strategies = get_all_strategies()
    return jsonify(strategies)

@app.route('/api/run_backtest', methods=['POST'])
def run_backtest():
    """运行回测接口"""
    try:
        # 获取请求参数
        data = request.json
        strategy_id = data.get('strategy_id', 'ma_cross')
        symbol = data.get('symbol', 'CFFEX.IF2312')
        initial_capital = data.get('initial_capital', 1000000)
        commission_rate = data.get('commission_rate', 0.01)
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        backtest_level = data.get('backtest_level', 'D')
        
        # 提取合约代码（去除交易所前缀）
        symbol_code = symbol.split('.')[-1] if '.' in symbol else symbol
        
        # 从策略配置中获取策略名称
        strategies_info = get_all_strategies()
        strategy_map = {s['id']: s['name'] for s in strategies_info}
        strategy_name = strategy_map.get(strategy_id, '简单均线交叉策略')
        
        # 模拟回测过程
        # 在实际应用中，这里应该调用真实的回测引擎，并传入手续费率和回测级别参数
        
        # 模拟进度更新
        progress = 0
        for i in range(1, 101):
            time.sleep(0.02)  # 模拟处理时间
            progress = i
        
        # 生成模拟回测数据
        # 在实际应用中，这里应该根据手续费率和回测级别调整回测逻辑
        # 调用generate_simulation_data函数并传入回测级别参数
        simulation_data = generate_simulation_data(
            days=252, 
            initial_capital=initial_capital,
            strategy_name=strategy_name,
            backtest_level=backtest_level
        )
        
        # 在模拟环境中，为了体现手续费的影响，我们对最终收益进行调整
        # 注意：这只是一个简单的模拟，实际应用中应该在每笔交易中计算手续费
        fee_adjustment = 1 - (commission_rate / 100 * 10)  # 简单模拟手续费对收益的影响
        simulation_data['equity_curve'] = [e * fee_adjustment for e in simulation_data['equity_curve']]
        
        # 重新计算性能指标
        total_return = (simulation_data['equity_curve'][-1] / initial_capital - 1) * 100
        daily_returns = np.diff(simulation_data['equity_curve']) / simulation_data['equity_curve'][:-1]
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / (daily_returns.std() + 1e-8)
        running_max = np.maximum.accumulate(simulation_data['equity_curve'])
        drawdown = (simulation_data['equity_curve'] - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        calmar_ratio = total_return / (abs(max_drawdown) + 1e-8) if max_drawdown != 0 else 0
        
        # 重新计算盈亏比
        winning_trades = daily_returns[daily_returns > 0]
        losing_trades = daily_returns[daily_returns < 0]
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        simulation_data.update({
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'profit_factor': profit_factor,
            'daily_returns': daily_returns.tolist()
        })
        
        # 生成图表
        equity_chart = generate_equity_curve_chart(
            simulation_data['dates'], 
            simulation_data['equity_curve']
        )
        
        drawdown_chart = generate_drawdown_chart(
            simulation_data['dates'], 
            simulation_data['equity_curve']
        )
        
        # 构建回测结果
        result = {
            'success': True,
            'strategy_name': strategy_name,
            'symbol': symbol_code,  # 使用不带交易所前缀的合约代码显示结果
            'commission_rate': commission_rate,
            'backtest_level': backtest_level,
            'performance': {
                'total_return': round(simulation_data['total_return'], 2),
                'sharpe_ratio': round(simulation_data['sharpe_ratio'], 2),
                'max_drawdown': round(simulation_data['max_drawdown'], 2),
                'calmar_ratio': round(simulation_data['calmar_ratio'], 2),
                'profit_factor': round(simulation_data['profit_factor'], 2)
            },
            'charts': {
                'equity_curve': equity_chart,
                'drawdown': drawdown_chart
            },
            'equity_data': {
                'dates': simulation_data['dates'],
                'values': [round(val, 2) for val in simulation_data['equity_curve']]
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy_params/<strategy_id>')
def get_strategy_params_api(strategy_id):
    """获取策略参数配置"""
    params = get_strategy_params(strategy_id)
    return jsonify(params)

if __name__ == '__main__':
    # 开发模式运行，生产环境应使用WSGI服务器
    app.run(debug=True, host='0.0.0.0', port=5001)