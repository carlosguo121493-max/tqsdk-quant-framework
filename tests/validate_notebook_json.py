#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证Notebook文件的JSON格式是否正确
"""
import json
import os

def validate_notebook_json(notebook_path):
    """
    验证Notebook文件的JSON格式是否正确
    
    Args:
        notebook_path: Notebook文件路径
    
    Returns:
        bool: True表示格式正确，False表示格式错误
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(notebook_path):
            print(f"❌ 文件不存在: {notebook_path}")
            return False
        
        # 读取并解析JSON文件
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # 验证必要的字段是否存在
        required_fields = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        for field in required_fields:
            if field not in notebook:
                print(f"❌ 缺少必要字段: {field}")
                return False
        
        # 验证cells是否为列表
        if not isinstance(notebook['cells'], list):
            print("❌ cells字段不是列表类型")
            return False
        
        # 验证nbformat是否为4（当前主流版本）
        if notebook['nbformat'] != 4:
            print(f"⚠️ nbformat版本为{notebook['nbformat']}，当前主流版本为4")
        
        print(f"✅ {notebook_path} 文件格式正确！")
        return True
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    # 验证我们的Notebook文件
    notebook_path = "/Users/weiguo/quant/tqsdk/strategy_demo.ipynb"
    print(f"开始验证 {notebook_path} 文件的JSON格式...")
    is_valid = validate_notebook_json(notebook_path)
    
    if is_valid:
        print("\n🎉 所有验证通过！Notebook文件现在可以正常使用。")
        print("\n使用建议：")
        print("1. 您可以直接在Jupyter环境中打开这个Notebook")
        print("2. 或者使用JupyterLab来查看和运行示例代码")
        print("3. 记得在实际使用时填写您的天勤量化账户信息")
    else:
        print("\n❌ Notebook文件存在格式问题，请检查并修复。")