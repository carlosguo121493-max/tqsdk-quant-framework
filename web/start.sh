#!/bin/sh

# 打印环境变量，用于调试
# echo "DATABASE_URL: $DATABASE_URL"

# 运行数据库初始化脚本
python /app/web/init_db.py || echo "数据库初始化失败，继续尝试启动应用..."

# 启动Flask应用
python /app/web/app.py