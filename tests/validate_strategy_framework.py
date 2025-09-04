#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证量化框架和策略模块是否能正常导入和工作
"""

def validate_framework_and_strategies():
    """
    验证框架和策略模块
    """
    print("开始验证量化框架和策略模块...")
    
    try:
        # 尝试导入量化框架
        from framework.quant_framework import QuantFramework, StrategyBase
        print("✅ 量化框架导入成功")
        
        # 尝试导入均线策略
        from strategies.moving_average_strategy import MovingAverageStrategy, MultipleMovingAverageStrategy
        print("✅ 均线策略模块导入成功")
        
        # 验证策略类是否正确继承自StrategyBase
        assert issubclass(MovingAverageStrategy, StrategyBase)
        assert issubclass(MultipleMovingAverageStrategy, StrategyBase)
        print("✅ 策略类继承关系验证成功")
        
        # 验证策略类的必要方法是否存在
        ma_strategy = MovingAverageStrategy()
        assert hasattr(ma_strategy, 'initialize')
        assert hasattr(ma_strategy, 'run')
        print("✅ 策略类必要方法验证成功")
        
        # 验证框架类的必要方法是否存在
        framework = QuantFramework()
        assert hasattr(framework, 'initialize')
        assert hasattr(framework, 'set_strategy')
        assert hasattr(framework, 'run_backtest')
        print("✅ 框架类必要方法验证成功")
        
        print("\n🎉 所有验证通过！量化框架和策略模块可以正常使用。")
        print("\n使用说明：")
        print("1. 打开 strategy_demo.ipynb 查看详细的使用示例")
        print("2. 在实际使用时，需要注册天勤量化账户并在代码中填写您的账户信息")
        print("3. 可以根据需要修改策略参数或开发自定义策略")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
    except AssertionError as e:
        print(f"❌ 验证失败: {e}")
    except Exception as e:
        print(f"❌ 出现未知错误: {e}")

if __name__ == "__main__":
    validate_framework_and_strategies()