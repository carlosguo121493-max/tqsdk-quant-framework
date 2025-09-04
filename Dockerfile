# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 使用非root用户运行（增加安全性）
RUN useradd -m appuser
USER appuser

# 设置PATH环境变量，确保用户的pip安装可执行
ENV PATH="/home/appuser/.local/bin:$PATH"

# 安装系统依赖 - 采用更可靠的方式，添加--fix-missing参数
USER root
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 切换回非root用户
USER appuser

# 升级pip
RUN pip install --upgrade pip --user

# 复制requirements.txt文件
COPY --chown=appuser:appuser requirements.txt .

# 安装Python依赖
RUN pip install numpy pandas matplotlib tqsdk jupyter --user

# 创建配置文件目录
RUN mkdir -p /home/appuser/.jupyter

# 配置Jupyter Notebook密码（密码为'quant'，可根据需要修改）
RUN python -c "from notebook.auth import passwd; open('/home/appuser/.jupyter/jupyter_notebook_config.py', 'w').write(f'c.NotebookApp.password = u{repr(passwd("quant"))}\n')"

# 配置Jupyter允许远程访问
RUN echo "c.NotebookApp.allow_remote_access = True" >> /home/appuser/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '*'" >> /home/appuser/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /home/appuser/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> /home/appuser/.jupyter/jupyter_notebook_config.py

# 复制项目文件
COPY --chown=appuser:appuser . .

# 创建数据目录（用于存储临时数据）
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["jupyter", "notebook"]