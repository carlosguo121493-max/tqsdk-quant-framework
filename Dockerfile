# 使用Python Alpine版本作为基础镜像，更小更轻量
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 安装Alpine系统依赖
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    lapack-dev \
    freetype-dev \
    libpng-dev

# 升级pip
RUN pip install --upgrade pip

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖（使用清华PyPI镜像源）
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录（用于存储临时数据）
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露web服务端口
EXPOSE 5001

# 启动web服务
CMD ["python", "/app/web/app.py"]