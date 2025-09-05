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

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入量化框架和策略
from framework.quant_framework import QuantFramework, StrategyBase
from strategies.moving_average_strategy import MovingAverageStrategy, MultipleMovingAverageStrategy

app = Flask(__name__)

# 模拟数据生成函数，用于前端展示
def generate_simulation_data(days=252, initial_capital=1000000, strategy_name='简单均线交叉策略'):
    """生成模拟回测数据"""
    np.random.seed(42)
    
    # 生成基础收益率序列
    base_returns = np.random.normal(0.0005, 0.02, days)
    
    # 根据策略调整收益率特征
    if strategy_name == '多均线策略':
        # 多均线策略表现稍好
        base_returns = base_returns * 1.2 + 0.0002
    elif strategy_name == '玻璃位策略':
        # 玻璃位策略波动性更大
        base_returns = base_returns * 1.5
        # 添加一些趋势
        trend = np.linspace(0, 0.001 * days, days) * 0.05
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
    sharpe_ratio = np.sqrt(252) * daily_returns.mean() / (daily_returns.std() + 1e-8)  # 添加小值避免除零
    
    # 计算最大回撤
    running_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min() * 100
    
    # 计算卡玛比率 (收益率/最大回撤的绝对值)
    calmar_ratio = total_return / (abs(max_drawdown) + 1e-8) if max_drawdown != 0 else 0
    
    # 生成日期序列
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    
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

@app.route('/api/strategies')
def get_strategies():
    """获取可用策略列表"""
    strategies = [
        {'id': 'ma_cross', 'name': '简单均线交叉策略', 'description': '基于短期均线与长期均线交叉的策略'},
        {'id': 'multi_ma', 'name': '多均线策略', 'description': '基于三条不同周期均线组合的策略'},
        {'id': 'glass', 'name': '玻璃位策略', 'description': '基于价格支撑阻力位的策略'}
    ]
    return jsonify(strategies)

@app.route('/api/run_backtest', methods=['POST'])
def run_backtest():
    """运行回测接口"""
    try:
        # 获取请求参数
        data = request.json
        strategy_id = data.get('strategy_id', 'ma_cross')
        symbol = data.get('symbol', 'IF2312')
        initial_capital = data.get('initial_capital', 1000000)
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        # 根据策略ID获取策略名称
        strategy_names = {
            'ma_cross': '简单均线交叉策略',
            'multi_ma': '多均线策略',
            'glass': '玻璃位策略'
        }
        strategy_name = strategy_names.get(strategy_id, '简单均线交叉策略')
        
        # 模拟回测过程
        # 在实际应用中，这里应该调用真实的回测引擎
        
        # 模拟进度更新
        progress = 0
        for i in range(1, 101):
            time.sleep(0.02)  # 模拟处理时间
            progress = i
        
        # 生成模拟回测数据
        simulation_data = generate_simulation_data(
            days=252, 
            initial_capital=initial_capital,
            strategy_name=strategy_name
        )
        
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
            'symbol': symbol,
            'performance': {
                'total_return': round(simulation_data['total_return'], 2),
                'sharpe_ratio': round(simulation_data['sharpe_ratio'], 2),
                'max_drawdown': round(simulation_data['max_drawdown'], 2),
                'calmar_ratio': round(simulation_data['calmar_ratio'], 2)
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
def get_strategy_params(strategy_id):
    """获取策略参数配置"""
    params = {
        'ma_cross': [
            {'name': 'short_period', 'label': '短周期均线', 'type': 'number', 'default': 5, 'min': 2, 'max': 50},
            {'name': 'long_period', 'label': '长周期均线', 'type': 'number', 'default': 20, 'min': 5, 'max': 200}
        ],
        'multi_ma': [
            {'name': 'short_period', 'label': '短周期均线', 'type': 'number', 'default': 5, 'min': 2, 'max': 50},
            {'name': 'mid_period', 'label': '中周期均线', 'type': 'number', 'default': 10, 'min': 5, 'max': 100},
            {'name': 'long_period', 'label': '长周期均线', 'type': 'number', 'default': 20, 'min': 10, 'max': 200}
        ],
        'glass': [
            {'name': 'window_size', 'label': '窗口大小', 'type': 'number', 'default': 20, 'min': 5, 'max': 100},
            {'name': 'threshold', 'label': '突破阈值(%)', 'type': 'number', 'default': 0.5, 'min': 0.1, 'max': 5, 'step': 0.1}
        ]
    }
    
    return jsonify(params.get(strategy_id, []))

if __name__ == '__main__':
    # 开发模式运行，生产环境应使用WSGI服务器
    app.run(debug=True, host='0.0.0.0', port=5000)