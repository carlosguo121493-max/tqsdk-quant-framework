#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库模块，负责连接数据库和数据操作
"""

import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化数据库实例
db = SQLAlchemy()

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


def initialize_data(app=None):
    """初始化期货品种和合约数据
    
    Args:
        app: Flask应用实例，可选参数
    """
    # 模拟的期货品种数据（按交易所分类）
    products_data = [
        # 中金所
        {'product_id': 'if', 'name': '沪深300指数期货', 'exchange': 'CFFEX'},
        {'product_id': 'ic', 'name': '中证500指数期货', 'exchange': 'CFFEX'},
        {'product_id': 'ih', 'name': '上证50指数期货', 'exchange': 'CFFEX'},
        # 上期所
        {'product_id': 'cu', 'name': '沪铜期货', 'exchange': 'SHFE'},
        {'product_id': 'al', 'name': '沪铝期货', 'exchange': 'SHFE'},
        {'product_id': 'zn', 'name': '沪锌期货', 'exchange': 'SHFE'},
        {'product_id': 'au', 'name': '黄金期货', 'exchange': 'SHFE'},
        {'product_id': 'ag', 'name': '白银期货', 'exchange': 'SHFE'},
        {'product_id': 'rb', 'name': '螺纹钢期货', 'exchange': 'SHFE'},
        {'product_id': 'hc', 'name': '热轧卷板期货', 'exchange': 'SHFE'},
        {'product_id': 'i', 'name': '铁矿石期货', 'exchange': 'SHFE'},
        {'product_id': 'j', 'name': '焦炭期货', 'exchange': 'SHFE'},
        {'product_id': 'jm', 'name': '焦煤期货', 'exchange': 'SHFE'},
        {'product_id': 'fu', 'name': '燃油期货', 'exchange': 'SHFE'},
        {'product_id': 'sc', 'name': '原油期货', 'exchange': 'SHFE'},
        # 郑商所
        {'product_id': 'ta', 'name': 'PTA期货', 'exchange': 'CZCE'},
        {'product_id': 'ma', 'name': '甲醇期货', 'exchange': 'CZCE'},
        {'product_id': 'pp', 'name': '聚丙烯期货', 'exchange': 'CZCE'},
        {'product_id': 'l', 'name': '聚乙烯期货', 'exchange': 'CZCE'},
        {'product_id': 'v', 'name': '聚氯乙烯期货', 'exchange': 'CZCE'},
        {'product_id': 'm', 'name': '豆粕期货', 'exchange': 'CZCE'},
        {'product_id': 'y', 'name': '豆油期货', 'exchange': 'CZCE'},
        {'product_id': 'a', 'name': '豆一期货', 'exchange': 'CZCE'},
        {'product_id': 'p', 'name': '棕榈油期货', 'exchange': 'CZCE'},
        {'product_id': 'c', 'name': '玉米期货', 'exchange': 'CZCE'},
        {'product_id': 'cs', 'name': '玉米淀粉期货', 'exchange': 'CZCE'},
        {'product_id': 'cf', 'name': '棉花期货', 'exchange': 'CZCE'},
        {'product_id': 'sr', 'name': '白糖期货', 'exchange': 'CZCE'},
        {'product_id': 'oi', 'name': '菜油期货', 'exchange': 'CZCE'},
        {'product_id': 'rm', 'name': '菜籽粕期货', 'exchange': 'CZCE'},
        {'product_id': 'fg', 'name': '玻璃期货', 'exchange': 'CZCE'},
        {'product_id': 'zc', 'name': '动力煤期货', 'exchange': 'CZCE'},
        # 广期所
        {'product_id': 'si', 'name': '工业硅期货', 'exchange': 'GGFEX'},
        # 大盘指数
        {'product_id': 'sh', 'name': '上证指数', 'exchange': 'INDEX'},
        {'product_id': 'sz', 'name': '深圳成指', 'exchange': 'INDEX'},
        {'product_id': 'cyb', 'name': '创业板指', 'exchange': 'INDEX'},
        {'product_id': 'zz500', 'name': '中证500', 'exchange': 'INDEX'},
        {'product_id': 'hs300', 'name': '沪深300', 'exchange': 'INDEX'},
        {'product_id': 'sp', 'name': '不锈钢期货', 'exchange': 'GGFEX'},
        {'product_id': 'nr', 'name': '20号胶期货', 'exchange': 'GGFEX'},
        {'product_id': 'lu', 'name': '低硫燃料油期货', 'exchange': 'GGFEX'},
        {'product_id': 'ss', 'name': '不锈钢期货', 'exchange': 'GGFEX'}
    ]
    
    # 添加期货品种到数据库
    for product_data in products_data:
        product = FuturesProduct(**product_data)
        db.session.add(product)
    
    db.session.commit()
    
    # 获取当前年份后两位
    current_year = datetime.now().year % 100
    
    # 为每个品种添加合约
    products = FuturesProduct.query.all()
    for product in products:
        # 大盘指数特殊处理
        if product.exchange == 'INDEX':
            # 只添加指数连续合约
            db.session.add(FuturesContract(
                code=f'{product.exchange}.{product.product_id.upper()}999',
                name=f'{product.product_id.upper()}999（指数连续）',
                is_continuous=True,
                product_id=product.product_id
            ))
        else:
            # 期货品种正常处理
            # 添加连续合约
            db.session.add(FuturesContract(
                code=f'{product.exchange}.{product.product_id.upper()}888',
                name=f'{product.product_id.upper()}888（主力连续）',
                is_continuous=True,
                product_id=product.product_id
            ))
            
            db.session.add(FuturesContract(
                code=f'{product.exchange}.{product.product_id.upper()}999',
                name=f'{product.product_id.upper()}999（指数连续）',
                is_continuous=True,
                product_id=product.product_id
            ))
            
            # 添加普通合约
            if product.product_id in ['if', 'ic', 'ih']:
                # 金融期货（季月合约）
                for month in [3, 6, 9, 12]:
                    for year_offset in range(0, 3):
                        year = current_year + year_offset
                        contract_code = f'{product.product_id.upper()}{year}{month:02d}'
                        db.session.add(FuturesContract(
                            code=f'{product.exchange}.{contract_code}',
                            name=contract_code,
                            product_id=product.product_id
                        ))
            else:
                # 商品期货（全年合约）
                for month in range(1, 13):
                    for year_offset in range(0, 2):
                        year = current_year + year_offset
                        contract_code = f'{product.product_id.upper()}{year}{month:02d}'
                        db.session.add(FuturesContract(
                            code=f'{product.exchange}.{contract_code}',
                            name=contract_code,
                            product_id=product.product_id
                        ))
    
    db.session.commit()