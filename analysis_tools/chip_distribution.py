# 筹码分布计算模块
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ChipDistribution:
    """
    筹码分布计算类
    基于股票的历史交易数据计算筹码分布
    """
    def __init__(self, decay_coefficient = 1):
        # 价格和筹码量的分布
        self.price_vol = {}
        # 历史衰减系数
        self.decay_coefficient = decay_coefficient
        # 价格精度
        self.price_precision = 0.01
    
    def calculate_triangle_distribution(self, date, high, low, avg, volume, turnover_rate, min_d=0.01):
        """
        三角形分布算法计算筹码分布
        将当日的换手筹码在当日的最高价、最低价和平均价之间三角形分布
        
        Args:
            date: 日期
            high: 最高价
            low: 最低价
            avg: 平均价
            volume: 成交量
            turnover_rate: 换手率（百分比）
            min_d: 价格精度
        """
        # 检查输入数据有效性
        if np.isnan(high) or np.isnan(low) or np.isnan(avg) or np.isnan(volume) or np.isnan(turnover_rate):
            return
        
        # 确保 high > low
        if high <= low:
            high = low + min_d
            
        # 生成价格序列
        price_range = np.arange(low, high + min_d, min_d)
        price_range = [round(p, 2) for p in price_range]
        
        # 计算当日筹码分布
        today_chip = {}
        
        # 使用三角形分布算法
        for price in price_range:
            x1 = price
            x2 = price + min_d
            h = 2 / (high - low)
            s = 0
            
            if price < avg:
                y1 = h / (avg - low) * (x1 - low)
                y2 = h / (avg - low) * (x2 - low)
                s = min_d * (y1 + y2) / 2
                s = s * volume
            else:
                y1 = h / (high - avg) * (high - x1)
                y2 = h / (high - avg) * (high - x2)
                s = min_d * (y1 + y2) / 2
                s = s * volume
            
            today_chip[price] = s
        
        # 更新历史筹码分布
        for price in self.price_vol:
            self.price_vol[price] = self.price_vol[price] * (1 - turnover_rate * self.decay_coefficient / 100)
        
        for price in today_chip:
            if price in self.price_vol:
                self.price_vol[price] += today_chip[price] * (turnover_rate * self.decay_coefficient / 100)
            else:
                self.price_vol[price] = today_chip[price] * (turnover_rate * self.decay_coefficient / 100)
    
    def calculate_even_distribution(self, date, high, low, volume, turnover_rate, min_d=0.01):
        """
        均匀分布算法计算筹码分布
        将当日的换手筹码在当日的最高价和最低价之间均匀分布
        
        Args:
            date: 日期
            high: 最高价
            low: 最低价
            volume: 成交量
            turnover_rate: 换手率（百分比）
            min_d: 价格精度
        """
        # 检查输入数据有效性
        if np.isnan(high) or np.isnan(low) or np.isnan(volume) or np.isnan(turnover_rate):
            return
        
        # 确保 high > low
        if high <= low:
            high = low + min_d
            
        # 生成价格序列
        price_range = np.arange(low, high + min_d, min_d)
        price_range = [round(p, 2) for p in price_range]
        
        # 计算每个价格点的筹码量
        each_vol = volume / len(price_range)
        
        # 更新历史筹码分布
        for price in self.price_vol:
            self.price_vol[price] = self.price_vol[price] * (1 - turnover_rate * self.decay_coefficient / 100)
        
        for price in price_range:
            if price in self.price_vol:
                self.price_vol[price] += each_vol * (turnover_rate * self.decay_coefficient / 100)
            else:
                self.price_vol[price] = each_vol * (turnover_rate * self.decay_coefficient / 100)
    
    def calculate_from_klines(self, klines, method='triangle', decay_coefficient=1):
        """
        从K线数据计算筹码分布
        
        Args:
            klines: K线数据，pandas.DataFrame格式，需要包含high, low, close, volume, turnover_rate字段
            method: 分布算法，'triangle'为三角形分布，'even'为均匀分布
            decay_coefficient: 历史衰减系数
        """
        # 检查输入数据
        if klines is None or len(klines) == 0:
            print("K线数据为空，无法计算筹码分布")
            return
            
        # 检查必要的列是否存在
        required_columns = ['high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in klines.columns:
                print(f"K线数据缺少必要的列: {col}")
                return
        
        self.price_vol = {}
        self.decay_coefficient = decay_coefficient
        
        for i in range(len(klines)):
            try:
                date = klines.index[i]
                high = klines['high'].iloc[i]
                low = klines['low'].iloc[i]
                close = klines['close'].iloc[i]
                volume = klines['volume'].iloc[i]
                
                # 检查数据有效性
                if np.isnan(high) or np.isnan(low) or np.isnan(close) or np.isnan(volume):
                    continue
                
                # 如果没有换手率字段，使用成交量/流通股本计算
                if 'turnover_rate' in klines.columns:
                    turnover_rate = klines['turnover_rate'].iloc[i]
                    if np.isnan(turnover_rate):
                        # 假设流通股本为1000万股
                        turnover_rate = volume / 10000000 * 100
                else:
                    # 假设流通股本为1000万股
                    turnover_rate = volume / 10000000 * 100
                
                if method == 'triangle':
                    avg = (high + low + close) / 3
                    self.calculate_triangle_distribution(date, high, low, avg, volume, turnover_rate)
                else:
                    self.calculate_even_distribution(date, high, low, volume, turnover_rate)
            except Exception as e:
                print(f"处理第{i}行数据时出错: {e}")
                continue
    
    def get_profit_ratio(self, price):
        """
        计算获利比例
        获利比例 = 当前价格以下的筹码总量 / 筹码总量
        
        Args:
            price: 当前价格
        
        Returns:
            获利比例，0-1之间的浮点数
        """
        total_chips = sum(self.price_vol.values())
        if total_chips == 0:
            return 0
        
        profit_chips = sum([v for p, v in self.price_vol.items() if p < price])
        return profit_chips / total_chips
    
    def get_cost_distribution(self, percentile):
        """
        计算成本分布
        COST(10)表示10%获利盘的价格是多少
        
        Args:
            percentile: 百分位数，0-100之间的整数
        
        Returns:
            对应百分位的价格
        """
        if not self.price_vol:
            return 0
        
        # 将百分位数转换为0-1之间的小数
        percentile = percentile / 100
        
        # 按价格排序
        sorted_prices = sorted(self.price_vol.keys())
        total_chips = sum(self.price_vol.values())
        
        if total_chips == 0:
            return 0
        
        cumulative = 0
        for price in sorted_prices:
            cumulative += self.price_vol[price]
            if cumulative / total_chips >= percentile:
                return price
        
        return sorted_prices[-1] if sorted_prices else 0
    
    def plot_chip_distribution(self, current_price=None):
        """
        绘制筹码分布图
        
        Args:
            current_price: 当前价格，如果提供则会在图中标记当前价格线
        """
        if not self.price_vol:
            print("没有筹码分布数据")
            return
        
        # 按价格排序
        sorted_items = sorted(self.price_vol.items())
        prices = [item[0] for item in sorted_items]
        volumes = [item[1] for item in sorted_items]
        
        plt.figure(figsize=(12, 6))
        plt.bar(prices, volumes, width=self.price_precision, alpha=0.7)
        plt.xlabel('价格')
        plt.ylabel('筹码量')
        plt.title('筹码分布图')
        
        if current_price:
            plt.axvline(x=current_price, color='r', linestyle='--', label=f'当前价格: {current_price}')
            profit_ratio = self.get_profit_ratio(current_price)
            plt.text(current_price, max(volumes) * 0.9, f'获利比例: {profit_ratio:.2%}', 
                     bbox=dict(facecolor='white', alpha=0.5))
            plt.legend()
        
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def get_chip_distribution(self):
        """
        获取筹码分布数据
        
        Returns:
            tuple: (价格列表, 筹码密度列表)
        """
        if not self.price_vol:
            # 如果没有筹码分布数据，返回默认数据
            return [], []
        
        # 按价格排序
        sorted_items = sorted(self.price_vol.items())
        prices = [item[0] for item in sorted_items]
        volumes = [item[1] for item in sorted_items]
        
        return prices, volumes