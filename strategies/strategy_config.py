# -*- coding: utf-8 -*-

"""
策略配置模块
集中管理所有策略的名称、描述和参数配置
便于统一维护和扩展
"""

# 策略配置字典，key为策略ID
strategy_configs = {
    'ma_cross': {
        'name': '简单均线交叉策略',
        'description': '基于短期均线与长期均线交叉的策略',
        'class_name': 'MovingAverageStrategy',
        'module': 'strategies.moving_average_strategy',
        'params': [
            {'name': 'short_period', 'label': '短周期均线', 'type': 'number', 'default': 5, 'min': 2, 'max': 50},
            {'name': 'long_period', 'label': '长周期均线', 'type': 'number', 'default': 20, 'min': 5, 'max': 200},
            {'name': 'kline_period', 'label': 'K线周期(秒)', 'type': 'number', 'default': 60*60*24, 'min': 60, 'max': 60*60*24*30, 'hidden': True}
        ]
    },
    'multi_ma': {
        'name': '多均线策略',
        'description': '基于三条不同周期均线组合的策略',
        'class_name': 'MultipleMovingAverageStrategy',
        'module': 'strategies.moving_average_strategy',
        'params': [
            {'name': 'short_period', 'label': '短周期均线', 'type': 'number', 'default': 5, 'min': 2, 'max': 50},
            {'name': 'mid_period', 'label': '中周期均线', 'type': 'number', 'default': 10, 'min': 5, 'max': 100},
            {'name': 'long_period', 'label': '长周期均线', 'type': 'number', 'default': 20, 'min': 10, 'max': 200},
            {'name': 'kline_period', 'label': 'K线周期(秒)', 'type': 'number', 'default': 60*60*24, 'min': 60, 'max': 60*60*24*30, 'hidden': True}
        ]
    },
    'glass': {
        'name': '玻璃位策略',
        'description': '基于价格支撑阻力位的策略',
        'class_name': 'GlassPositionStrategy',
        'module': 'strategies.glass_strategy',
        'params': [
            {'name': 'window_size', 'label': '窗口大小', 'type': 'number', 'default': 20, 'min': 5, 'max': 100},
            {'name': 'threshold', 'label': '突破阈值(%)', 'type': 'number', 'default': 0.5, 'min': 0.1, 'max': 5, 'step': 0.1},
            {'name': 'kline_period', 'label': 'K线周期(秒)', 'type': 'number', 'default': 60*60*24, 'min': 60, 'max': 60*60*24*30, 'hidden': True}
        ]
    }
}

def get_all_strategies():
    """
    获取所有可用策略的基本信息
    返回策略ID、名称和描述的列表
    """
    return [
        {
            'id': strategy_id,
            'name': config['name'],
            'description': config['description']
        }
        for strategy_id, config in strategy_configs.items()
    ]

def get_strategy_params(strategy_id):
    """
    获取指定策略的参数配置
    过滤掉标记为hidden的参数
    """
    if strategy_id not in strategy_configs:
        return []
    
    # 过滤掉隐藏参数
    return [
        param for param in strategy_configs[strategy_id]['params']
        if not param.get('hidden', False)
    ]

def get_strategy_class(strategy_id):
    """
    动态加载并返回策略类
    """
    if strategy_id not in strategy_configs:
        return None
    
    config = strategy_configs[strategy_id]
    module_name = config['module']
    class_name = config['class_name']
    
    try:
        # 动态导入模块
        module = __import__(module_name, fromlist=[class_name])
        # 获取类
        strategy_class = getattr(module, class_name)
        return strategy_class
    except (ImportError, AttributeError):
        print(f"无法加载策略类: {module_name}.{class_name}")
        return None

def create_strategy_instance(strategy_id, **kwargs):
    """
    创建策略实例
    """
    strategy_class = get_strategy_class(strategy_id)
    if strategy_class is None:
        return None
    
    # 获取策略默认参数
    default_params = {}
    if strategy_id in strategy_configs:
        for param in strategy_configs[strategy_id]['params']:
            default_params[param['name']] = param['default']
    
    # 使用传入的参数覆盖默认参数
    default_params.update(kwargs)
    
    # 创建并返回策略实例
    return strategy_class(**default_params)