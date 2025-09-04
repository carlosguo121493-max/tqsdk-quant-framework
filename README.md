# 量化交易框架与策略

## 项目简介

这是一个基于天勤量化（TqSdk）的量化交易框架，提供了策略基类、均线策略、筹码分布分析等功能，可用于期货和股票的回测和实盘交易。

## 项目结构

项目采用模块化设计，将不同功能的代码组织在独立的目录中，便于维护和扩展。主要包括以下目录：

```
├── framework/                # 框架核心模块
│   ├── __init__.py
│   └── quant_framework.py    # 量化框架基类和策略基类
├── strategies/               # 交易策略模块
│   ├── __init__.py
│   ├── moving_average_strategy.py  # 均线策略实现
│   └── glass_strategy.py     # 玻璃期货回测策略
├── analysis_tools/           # 分析工具模块
│   ├── __init__.py
│   ├── chip_distribution.py  # 传统筹码分布计算
│   └── chip_distribution_with_increment.py  # 基于持仓增量的筹码分布计算
├── examples/                 # 使用示例
│   ├── strategy_demo.ipynb   # 策略演示笔记本
│   ├── chip_distribution_example.ipynb  # 筹码分布示例
│   └── chip_distribution_comparison.ipynb  # 筹码分布对比分析
├── tests/                    # 测试模块
│   ├── test_chip_distribution.py  # 筹码分布测试
│   ├── validate_notebook.py  # 笔记本验证
│   ├── validate_notebook_json.py  # 笔记本JSON验证
│   └── validate_strategy_framework.py  # 策略框架验证
└── requirements.txt          # 项目依赖
```

## 安装与依赖

1. 克隆或下载本项目
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

主要依赖包：
- tqsdk：天勤量化SDK，用于获取行情数据和回测
- numpy：科学计算库
- pandas：数据处理库
- matplotlib：图表绘制库

## 使用方法

### 1. 使用均线策略进行回测

参考 `examples/strategy_demo.ipynb` 中的示例，主要步骤如下：

```python
from framework.quant_framework import QuantFramework
from strategies.moving_average_strategy import MovingAverageStrategy
from datetime import date

# 初始化量化框架
framework = QuantFramework()

# 设置回测参数
symbol = 'CZCE.FG601'  # 玻璃期货合约
start_date = date(2023, 1, 1)  # 回测开始日期
end_date = date(2023, 12, 31)  # 回测结束日期
initial_capital = 100000  # 初始资金

# 初始化框架
framework.initialize(symbol, start_date, end_date, initial_capital)

# 创建均线策略实例（短周期5，长周期20）
ma_strategy = MovingAverageStrategy(short_period=5, long_period=20)

# 设置策略
framework.set_strategy(ma_strategy)

# 运行回测
framework.run_backtest()
```

### 2. 使用筹码分布进行分析

参考 `examples/chip_distribution_example.ipynb` 中的示例，主要步骤如下：

```python
from analysis_tools.chip_distribution import ChipDistribution
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 创建筹码分布实例
chip_dist = ChipDistribution(decay_coefficient=0.9)

# 添加数据并计算筹码分布
for idx, row in df.iterrows():
    # 计算换手率
    turnover_rate = row['volume'] / total_shares * 100
    # 计算平均价格
    avg_price = (row['high'] + row['low'] + row['close']) / 3
    # 更新筹码分布
    chip_dist.calculate_triangle_distribution(idx, row['high'], row['low'], avg_price, row['volume'], turnover_rate)

# 绘制筹码分布图
chip_dist.plot_chip_distribution()
```

### 3. 自定义策略开发

可以通过继承 `StrategyBase` 类来开发自定义策略，主要需要实现 `run()` 方法：

```python
from framework.quant_framework import StrategyBase
from tqsdk import TargetPosTask

class MyCustomStrategy(StrategyBase):
    def __init__(self, param1=1, param2=2):
        super().__init__()
        # 初始化自定义参数
        self.param1 = param1
        self.param2 = param2
        self.target_pos = None
        
    def initialize(self, api, symbol):
        super().initialize(api, symbol)
        # 初始化策略所需的数据
        self.target_pos = TargetPosTask(api, symbol)
        # 初始化其他资源
        
    def run(self):
        # 实现策略逻辑
        while True:
            # 获取最新数据
            # 计算交易信号
            # 执行交易
            # 更新性能指标
            self.api.wait_update()
```

## 注意事项

1. 使用天勤量化SDK需要注册天勤账户，请在以下网址注册：https://account.shinnytech.com/
2. 在实际使用时，需要在代码中填写您的天勤账户信息
3. 本项目提供的策略仅供参考，在实际交易中请谨慎使用

## 项目贡献

欢迎提交Issue和Pull Request来改进本项目。

## 免责声明

本项目提供的所有代码、策略和分析工具仅供学习和参考，不构成任何投资建议。使用本项目进行交易操作所产生的风险和损失，由用户自行承担。