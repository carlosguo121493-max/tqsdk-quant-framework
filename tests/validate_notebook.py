import json
import os

# 要验证的文件列表
files_to_validate = [
    'chip_distribution_comparison.ipynb',
    'chip_distribution_example.ipynb'
]

def validate_json_file(file_path):
    """验证JSON文件格式是否正确"""
    try:
        print(f'验证文件: {file_path}')
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        print(f'文件大小: {file_size} 字节')
        
        # 读取并解析JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查Notebook基本结构
        required_keys = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        for key in required_keys:
            if key not in data:
                print(f'错误: 文件缺少必需的键 {key}')
                return False
        
        # 检查cells数组
        if not isinstance(data['cells'], list):
            print('错误: cells不是一个数组')
            return False
        
        print(f'文件包含 {len(data["cells"])} 个单元格')
        print('JSON格式验证通过!')
        return True
        
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
        print(f'错误位置: 行 {e.lineno}, 列 {e.colno}')
        # 尝试定位错误位置的内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if e.lineno <= len(lines):
                    print(f'出错行内容: {lines[e.lineno-1].strip()}')
                    # 打印上下文行
                    start = max(0, e.lineno-3)
                    end = min(len(lines), e.lineno+2)
                    print('上下文:')
                    for i in range(start, end):
                        line_num = i + 1
                        prefix = '->' if line_num == e.lineno else '  '
                        print(f'{prefix} {line_num}: {lines[i].strip()}')
        except:
            pass
        return False
    except Exception as e:
        print(f'验证过程中出错: {e}')
        return False

# 主函数
if __name__ == '__main__':
    print('===== 开始验证Notebook文件格式 =====')
    all_valid = True
    
    for file_name in files_to_validate:
        file_path = os.path.join('.', file_name)
        if not os.path.exists(file_path):
            print(f'错误: 文件 {file_path} 不存在')
            all_valid = False
            continue
        
        is_valid = validate_json_file(file_path)
        if not is_valid:
            all_valid = False
        print('-' * 50)
    
    if all_valid:
        print('所有文件JSON格式验证通过!')
    else:
        print('有文件JSON格式验证失败，请查看上述错误信息。')