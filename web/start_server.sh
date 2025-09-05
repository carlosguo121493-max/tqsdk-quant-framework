#!/bin/bash

# 启动量化交易策略交互平台服务

# 设置中文环境
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 获取脚本所在目录
dir=$(cd $(dirname $0); pwd)

# 检查是否安装了依赖
if ! pip show Flask > /dev/null 2>&1; then
    echo "正在安装依赖..."
    pip install -r $dir/../requirements.txt
fi

# 启动Flask服务
echo "正在启动量化交易策略交互平台服务..."
echo "服务地址: http://localhost:5000"
echo "按Ctrl+C停止服务"

# 运行Flask应用
cd $dir
python app.py