# 阶段1：安装依赖
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装Alpine系统依赖
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    lapack-dev \
    freetype-dev \
    libpng-dev \
    linux-headers

# 复制项目文件和requirements.txt
COPY ../requirements.txt .

# 安装Python依赖到单独的目录（避免重复下载）
RUN pip install --prefix=/install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 阶段2：创建运行时镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 从builder阶段复制已安装的依赖
COPY --from=builder /install /usr/local

# 安装运行时依赖
RUN apk add --no-cache \
    libstdc++ \
    libgomp \
    freetype \
    libpng

# 复制项目文件
COPY . .
COPY ../framework /app/framework
COPY ../strategies /app/strategies

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python", "/app/web/app.py"]