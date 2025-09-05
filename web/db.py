#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库模块，负责连接数据库和数据操作
"""

import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from tqsdk import TqApi, TqAuth

# 初始化数据库实例
db = SQLAlchemy()

# 配置选项 - 控制是否使用TqSdk真实数据以及认证信息
USE_TQSDK_REAL_DATA = os.environ.get('USE_TQSDK_REAL_DATA', 'False').lower() == 'true'
TQSDK_USERNAME = os.environ.get('TQSDK_USERNAME', '')
TQSDK_PASSWORD = os.environ.get('TQSDK_PASSWORD', '')

class FuturesProduct(db.Model):
    """期货品种模型"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 定义关系
    contracts = db.relationship('FuturesContract', backref='product', lazy=True)

class FuturesContract(db.Model):
    """期货合约模型"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_continuous = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.String(20), db.ForeignKey('futures_product.product_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


def init_db(app):
    """初始化数据库"""
    # 配置数据库连接，使用更简单的相对路径
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///futures.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化应用与数据库的关联
    db.init_app(app)
    
    # 创建数据表
    with app.app_context():
        db.create_all()
        
        # 初始化数据（如果表为空）
        if not FuturesProduct.query.first():
            initialize_data()


def get_futures_data_from_api():
    """从TqSdk获取真实期货品种和合约数据，如果失败则使用修正后的模拟数据
    
    Returns:
        dict: 包含期货品种和合约数据的字典
    """
    result = {
        'products': [],
        'contracts': []
    }
    
    try:
        # 尝试从TqSdk获取真实数据
        print("正在尝试从TqSdk获取真实期货数据...")
        
        # 创建TqApi实例（不使用认证信息，因为很多功能无需登录即可使用）
        # 但有些功能可能需要认证，所以根据配置选项提供认证信息
        if USE_TQSDK_REAL_DATA and TQSDK_USERNAME and TQSDK_PASSWORD:
            print("使用认证信息连接TqSdk...")
            api = TqApi(auth=TqAuth(TQSDK_USERNAME, TQSDK_PASSWORD))
        else:
            print("使用匿名方式连接TqSdk（部分功能可能受限）...")
            api = TqApi()
        
        # 获取所有合约信息
        all_contracts = api.query_quotes(ins_class='FUTURE', expired=False)
        
        # 存储产品信息的字典，用于去重
        products_dict = {}
        
        # 遍历所有合约，提取产品和合约信息
        for contract in all_contracts:
            # 获取合约代码、交易所代码、产品代码等信息
            contract_code = contract['instrument_id']
            exchange = contract_code.split('.')[0]
            product_id = contract_code.split('.')[1][0:2] if len(contract_code.split('.')) > 1 else ''
            product_name = contract.get('name', '')
            
            # 提取产品ID（前2个字符，如'cu'表示铜）
            # 针对不同交易所的特殊处理
            if exchange == 'CFFEX':
                # 中金所产品ID较长，如'if2309'
                product_id = contract_code.split('.')[1][0:2]
            else:
                # 其他交易所产品ID通常是前2个字符
                product_id = contract_code.split('.')[1][0:2] if len(contract_code.split('.')[1]) >= 2 else ''
            
            # 添加产品信息（去重）
            product_key = f"{exchange}.{product_id}"
            if product_key not in products_dict:
                products_dict[product_key] = {
                    'product_id': product_id,
                    'name': product_name.split(' ')[0] if product_name else f'{product_id}期货',
                    'exchange': exchange
                }
                result['products'].append(products_dict[product_key])
            
            # 添加合约信息
            result['contracts'].append({
                'code': contract_code,
                'name': contract_code.split('.')[1],
                'is_continuous': '888' in contract_code or '999' in contract_code,
                'product_id': product_id
            })
        
        # 关闭API连接
        api.close()
        
        print(f"成功从TqSdk获取真实数据：{len(result['products'])} 个期货品种和 {len(result['contracts'])} 个合约数据")
        
    except Exception as e:
        print(f"从TqSdk获取真实数据失败: {e}")
        print("将使用修正后的模拟数据...")
        
        # 使用修正后的模拟数据作为备用
        # 模拟的期货品种数据（按交易所分类）- 修正版
        result['products'] = [
            # 中金所
            {'product_id': 'if', 'name': '沪深300指数期货', 'exchange': 'CFFEX'},
            {'product_id': 'ic', 'name': '中证500指数期货', 'exchange': 'CFFEX'},
            {'product_id': 'ih', 'name': '上证50指数期货', 'exchange': 'CFFEX'},
            {'product_id': 'tf', 'name': '10年期国债期货', 'exchange': 'CFFEX'},
            {'product_id': 't', 'name': '5年期国债期货', 'exchange': 'CFFEX'},
            {'product_id': 'ts', 'name': '2年期国债期货', 'exchange': 'CFFEX'},
            
            # 上期所
            {'product_id': 'cu', 'name': '沪铜期货', 'exchange': 'SHFE'},
            {'product_id': 'al', 'name': '沪铝期货', 'exchange': 'SHFE'},
            {'product_id': 'zn', 'name': '沪锌期货', 'exchange': 'SHFE'},
            {'product_id': 'pb', 'name': '沪铅期货', 'exchange': 'SHFE'},
            {'product_id': 'ni', 'name': '沪镍期货', 'exchange': 'SHFE'},
            {'product_id': 'sn', 'name': '沪锡期货', 'exchange': 'SHFE'},
            {'product_id': 'au', 'name': '黄金期货', 'exchange': 'SHFE'},
            {'product_id': 'ag', 'name': '白银期货', 'exchange': 'SHFE'},
            {'product_id': 'rb', 'name': '螺纹钢期货', 'exchange': 'SHFE'},
            {'product_id': 'hc', 'name': '热轧卷板期货', 'exchange': 'SHFE'},
            {'product_id': 'ss', 'name': '不锈钢期货', 'exchange': 'SHFE'},
            {'product_id': 'fu', 'name': '燃料油期货', 'exchange': 'SHFE'},
            {'product_id': 'bu', 'name': '石油沥青期货', 'exchange': 'SHFE'},
            {'product_id': 'sc', 'name': '原油期货', 'exchange': 'SHFE'},
            {'product_id': 'ru', 'name': '天然橡胶期货', 'exchange': 'SHFE'},
            {'product_id': 'nr', 'name': '20号胶期货', 'exchange': 'SHFE'},
            {'product_id': 'sp', 'name': '漂针浆期货', 'exchange': 'SHFE'},
            
            # 郑商所 - 修正纯碱交易所
            {'product_id': 'ta', 'name': 'PTA期货', 'exchange': 'CZCE'},
            {'product_id': 'ma', 'name': '甲醇期货', 'exchange': 'CZCE'},
            {'product_id': 'cs', 'name': '玉米淀粉期货', 'exchange': 'CZCE'},
            {'product_id': 'sr', 'name': '白糖期货', 'exchange': 'CZCE'},
            {'product_id': 'cf', 'name': '棉花期货', 'exchange': 'CZCE'},
            {'product_id': 'zc', 'name': '动力煤期货', 'exchange': 'CZCE'},
            {'product_id': 'fg', 'name': '玻璃期货', 'exchange': 'CZCE'},
            {'product_id': 'rm', 'name': '菜籽粕期货', 'exchange': 'CZCE'},
            {'product_id': 'oi', 'name': '菜籽油期货', 'exchange': 'CZCE'},
            {'product_id': 'pk', 'name': '花生期货', 'exchange': 'CZCE'},
            {'product_id': 'jr', 'name': '粳稻期货', 'exchange': 'CZCE'},
            {'product_id': 'rs', 'name': '菜籽期货', 'exchange': 'CZCE'},
            {'product_id': 'lr', 'name': '晚籼稻期货', 'exchange': 'CZCE'},
            {'product_id': 'sf', 'name': '硅铁期货', 'exchange': 'CZCE'},
            {'product_id': 'sm', 'name': '锰硅期货', 'exchange': 'CZCE'},
            {'product_id': 'sa', 'name': '纯碱期货', 'exchange': 'CZCE'},
            
            # 大商所
            {'product_id': 'a', 'name': '豆一期货', 'exchange': 'DCE'},
            {'product_id': 'b', 'name': '豆二期货', 'exchange': 'DCE'},
            {'product_id': 'c', 'name': '玉米期货', 'exchange': 'DCE'},
            {'product_id': 'm', 'name': '豆粕期货', 'exchange': 'DCE'},
            {'product_id': 'y', 'name': '豆油期货', 'exchange': 'DCE'},
            {'product_id': 'p', 'name': '棕榈油期货', 'exchange': 'DCE'},
            {'product_id': 'l', 'name': '聚乙烯期货', 'exchange': 'DCE'},
            {'product_id': 'v', 'name': '聚氯乙烯期货', 'exchange': 'DCE'},
            {'product_id': 'pp', 'name': '聚丙烯期货', 'exchange': 'DCE'},
            {'product_id': 'j', 'name': '焦炭期货', 'exchange': 'DCE'},
            {'product_id': 'jm', 'name': '焦煤期货', 'exchange': 'DCE'},
            {'product_id': 'i', 'name': '铁矿石期货', 'exchange': 'DCE'},
            {'product_id': 'eg', 'name': '乙二醇期货', 'exchange': 'DCE'},
            {'product_id': 'eb', 'name': '苯乙烯期货', 'exchange': 'DCE'},
            {'product_id': 'fb', 'name': '纤维板期货', 'exchange': 'DCE'},
            {'product_id': 'bb', 'name': '胶合板期货', 'exchange': 'DCE'},
            {'product_id': 'jd', 'name': '鸡蛋期货', 'exchange': 'DCE'},
            {'product_id': 'rr', 'name': '粳米期货', 'exchange': 'DCE'},
            
            # 广期所 - 添加多晶硅期货
            {'product_id': 'si', 'name': '工业硅期货', 'exchange': 'GFEX'},
            {'product_id': 'bn', 'name': '苯乙烯期货', 'exchange': 'GFEX'},
            {'product_id': 'ec', 'name': '碳酸锂期货', 'exchange': 'GFEX'},
            {'product_id': 'pb2', 'name': '国际铜期货', 'exchange': 'GFEX'},
            {'product_id': 'pvs', 'name': '多晶硅期货', 'exchange': 'GFEX'}
        ]
        
        # 获取当前年份后两位
        current_year = datetime.now().year % 100
        
        # 为每个品种添加合约
        for product in result['products']:
            # 添加连续合约
            result['contracts'].append({
                'code': f'{product["exchange"]}.{product["product_id"].upper()}888',
                'name': f'{product["product_id"].upper()}888（主力连续）',
                'is_continuous': True,
                'product_id': product['product_id']
            })
            
            result['contracts'].append({
                'code': f'{product["exchange"]}.{product["product_id"].upper()}999',
                'name': f'{product["product_id"].upper()}999（指数连续）',
                'is_continuous': True,
                'product_id': product['product_id']
            })
            
            # 添加普通合约
            if product['product_id'] in ['if', 'ic', 'ih', 'tf', 't', 'ts']:
                # 金融期货（季月合约）
                for month in [3, 6, 9, 12]:
                    for year_offset in range(0, 3):
                        year = current_year + year_offset
                        contract_code = f'{product["product_id"].upper()}{year}{month:02d}'
                        result['contracts'].append({
                            'code': f'{product["exchange"]}.{contract_code}',
                            'name': contract_code,
                            'is_continuous': False,
                            'product_id': product['product_id']
                        })
            else:
                # 商品期货（全年合约）
                for month in range(1, 13):
                    for year_offset in range(0, 2):
                        year = current_year + year_offset
                        contract_code = f'{product["product_id"].upper()}{year}{month:02d}'
                        result['contracts'].append({
                            'code': f'{product["exchange"]}.{contract_code}',
                            'name': contract_code,
                            'is_continuous': False,
                            'product_id': product['product_id']
                        })
        
        print(f"使用修正后的模拟数据：成功加载 {len(result['products'])} 个期货品种和 {len(result['contracts'])} 个合约数据")
    
    return result

def refresh_futures_data(app=None):
    # Refresh futures products and contracts data
    # Parameters:
    #   app: Flask app instance (optional)
    # Returns:
    #   dict: Dictionary containing refresh results
    try:
        # Use app context if provided
        if app:
            with app.app_context():
                # Clear existing data
                FuturesContract.query.delete()
                FuturesProduct.query.delete()
                db.session.commit()
                
                # 从API获取最新数据
                data = get_futures_data_from_api()
                
                # 添加期货品种到数据库
                for product_data in data['products']:
                    product = FuturesProduct(**product_data)
                    db.session.add(product)
                
                db.session.commit()
                
                # 添加合约到数据库
                for contract_data in data['contracts']:
                    contract = FuturesContract(**contract_data)
                    db.session.add(contract)
                
                db.session.commit()
                
                result = {
                    'success': True,
                    'message': f'成功刷新 {len(data["products"])} 个期货品种和 {len(data["contracts"])} 个合约数据'
                }
                print(result['message'])
        else:
            # 没有提供app参数，直接操作数据库
            # 清空现有数据
            FuturesContract.query.delete()
            FuturesProduct.query.delete()
            db.session.commit()
            
            # 从API获取最新数据
            data = get_futures_data_from_api()
            
            # 添加期货品种到数据库
            for product_data in data['products']:
                product = FuturesProduct(**product_data)
                db.session.add(product)
            
            db.session.commit()
            
            # 添加合约到数据库
            for contract_data in data['contracts']:
                contract = FuturesContract(**contract_data)
                db.session.add(contract)
            
            db.session.commit()
            
            result = {
                'success': True,
                'message': f'成功刷新 {len(data["products"])} 个期货品种和 {len(data["contracts"])} 个合约数据'
            }
            print(result['message'])
    except Exception as e:
        result = {
            'success': False,
            'message': f'刷新期货数据失败: {str(e)}'
        }
        print(result['message'])
    
    return result

# Ensure index products are included when initializing data
def ensure_index_products(app=None):
    # Ensure the database contains major index products
    index_products = [
        {'product_id': 'sh', 'name': 'SSE Index', 'exchange': 'INDEX'},
        {'product_id': 'sz', 'name': 'SZSE Index', 'exchange': 'INDEX'},
        {'product_id': 'hs300', 'name': 'CSI 300', 'exchange': 'INDEX'}
    ]
    
    try:
        if app:
            with app.app_context():
                for product_data in index_products:
                    existing_product = FuturesProduct.query.filter_by(product_id=product_data['product_id']).first()
                    if not existing_product:
                        product = FuturesProduct(**product_data)
                        db.session.add(product)
                        
                        # 添加对应的合约
                        contract = FuturesContract(
                            code=product_data['product_id'],
                            name=product_data['name'],
                            is_continuous=True,
                            product_id=product_data['product_id']
                        )
                        db.session.add(contract)
                
                db.session.commit()
        else:
            for product_data in index_products:
                existing_product = FuturesProduct.query.filter_by(product_id=product_data['product_id']).first()
                if not existing_product:
                    product = FuturesProduct(**product_data)
                    db.session.add(product)
                    
                    # 添加对应的合约
                    contract = FuturesContract(
                        code=product_data['product_id'],
                        name=product_data['name'],
                        is_continuous=True,
                        product_id=product_data['product_id']
                    )
                    db.session.add(contract)
                
            db.session.commit()
    except Exception as e:
        print(f"Error ensuring index products: {e}")

def initialize_data(app=None):
    # 确保添加大盘指数产品
    ensure_index_products(app)
    
    # 如果数据库中已经有数据，不重复初始化
    if app:
        with app.app_context():
            if FuturesProduct.query.first():
                print("数据库中已存在期货品种数据，跳过初始化")
                return
    else:
        if FuturesProduct.query.first():
            print("数据库中已存在期货品种数据，跳过初始化")
            return
    
    # 数据库没有数据，从API获取并初始化
    print("数据库中没有期货品种数据，从API获取并初始化...")
    
    if app:
        with app.app_context():
            data = get_futures_data_from_api()
            
            # 添加期货品种到数据库
            for product_data in data['products']:
                product = FuturesProduct(**product_data)
                db.session.add(product)
            
            db.session.commit()
            
            # 添加合约到数据库
            for contract_data in data['contracts']:
                contract = FuturesContract(**contract_data)
                db.session.add(contract)
            
            db.session.commit()
            print(f"成功初始化 {len(data['products'])} 个期货品种和 {len(data['contracts'])} 个合约数据")
    else:
        data = get_futures_data_from_api()
        
        # 添加期货品种到数据库
        for product_data in data['products']:
            product = FuturesProduct(**product_data)
            db.session.add(product)
        
        db.session.commit()
        
        # 添加合约到数据库
        for contract_data in data['contracts']:
            contract = FuturesContract(**contract_data)
            db.session.add(contract)
        
        db.session.commit()
        print(f"成功初始化 {len(data['products'])} 个期货品种和 {len(data['contracts'])} 个合约数据")