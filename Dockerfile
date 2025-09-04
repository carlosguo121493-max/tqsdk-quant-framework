# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \n    gcc \n    g++ \n    libc-dev \n    libgomp1 \n    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install numpy pandas matplotlib tqsdk jupyter

# 创建配置文件目录
RUN mkdir -p /root/.jupyter

# 配置Jupyter Notebook密码（密码为'quant'，可根据需要修改）
RUN python -c "from notebook.auth import passwd; print(f'c.NotebookApp.password = u"{passwd(\"quant\")}"' >> /root/.jupyter/jupyter_notebook_config.py)"

# 配置Jupyter允许远程访问
RUN echo "c.NotebookApp.allow_remote_access = True" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '*'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> /root/.jupyter/jupyter_notebook_config.py

# 复制项目文件
COPY . .

# 创建数据目录（用于存储临时数据）
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["jupyter", "notebook", "--allow-root"]