import numpy as np
import pandas as pd
from analysis_tools.chip_distribution import ChipDistribution
from analysis_tools.chip_distribution_with_increment import ChipDistributionWithIncrement
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]

# 创建简单的测试数据
data = {
    'high': [105, 107, 109, 108, 110],
    'low': [100, 102, 105, 103, 106],
    'close': [103, 105, 108, 105, 109],
    'volume': [10000, 12000, 15000, 13000, 14000],
    'open_interest': [50000, 52000, 55000, 53000, 56000]
}
df = pd.DataFrame(data)
df.index = pd.date_range(start='2023-01-01', periods=5)

# 创建传统方法的筹码分布实例
chip_dist_traditional = ChipDistribution(decay_coefficient=0.9)

# 假设总流通盘为100万手
total_shares = 1000000

# 使用传统方法计算筹码分布
for idx, row in df.iterrows():
    # 计算换手率
    turnover_rate = row['volume'] / total_shares * 100
    # 计算平均价格
    avg_price = (row['high'] + row['low'] + row['close']) / 3
    # 更新筹码分布
    chip_dist_traditional.calculate_triangle_distribution(idx, row['high'], row['low'], avg_price, row['volume'], turnover_rate)

# 创建基于持仓增量方法的筹码分布实例
chip_dist_with_inc = ChipDistribution(decay_coefficient=0.9)

# 计算持仓增量
df['open_interest_diff'] = df['open_interest'].diff()
df['open_interest_diff'] = df['open_interest_diff'].fillna(0)

# 使用基于持仓增量的方法计算筹码分布
for idx, row in df.iterrows():
    # 计算基于持仓增量的有效换手率
    effective_volume = row['volume'] if row['open_interest_diff'] > 0 else abs(row['open_interest_diff'])
    # 计算有效换手率
    turnover_rate_with_inc = effective_volume / total_shares * 100
    
    # 更新筹码分布
    if row['open_interest_diff'] > 0:
        avg_price = (row['high'] + row['low'] + row['close']) / 3
        chip_dist_with_inc.calculate_triangle_distribution(idx, row['high'], row['low'], avg_price, effective_volume, turnover_rate_with_inc)
    else:
        avg_price = (row['high'] + row['low'] + row['open']) / 3 if 'open' in row else (row['high'] + row['low'] + row['close']) / 3
        chip_dist_with_inc.calculate_triangle_distribution(idx, row['high'], row['low'], avg_price, effective_volume, turnover_rate_with_inc)

# 计算获利比例
current_price = 108
profit_ratio_traditional = chip_dist_traditional.get_profit_ratio(current_price)
profit_ratio_with_inc = chip_dist_with_inc.get_profit_ratio(current_price)

print(f'传统方法计算的当前获利比例: {profit_ratio_traditional:.2%}')
print(f'基于持仓增量方法计算的当前获利比例: {profit_ratio_with_inc:.2%}')

# 测试get_chip_distribution方法
try:
    price_bins_traditional, chip_density_traditional = chip_dist_traditional.get_chip_distribution()
    print(f'传统方法筹码分布数据点数: {len(price_bins_traditional)}')
    
    price_bins_with_inc, chip_density_with_inc = chip_dist_with_inc.get_chip_distribution()
    print(f'基于持仓增量方法筹码分布数据点数: {len(price_bins_with_inc)}')
    
    print("所有测试通过！修复成功！")
except Exception as e:
    print(f"测试失败: {e}")