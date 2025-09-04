# 使用Python官方镜像作为基础镜像
# 使用更新、更可靠的Debian基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 配置apt源以提高可靠性
RUN echo 'deb http://deb.debian.org/debian bullseye main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian bullseye-updates main contrib non-free' >> /etc/apt/sources.list

# 安装系统依赖 - 采用分步骤安装，增加重试机制
RUN apt-get clean && \
    apt-get -y update && \
    apt-get -y install --no-install-recommends gcc g++ libc-dev libgomp1 && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip

# 安装Python依赖（单独安装numpy以避免编译问题）
RUN pip install numpy==1.23.5 pandas==1.5.3 matplotlib==3.7.1
RUN pip install tqsdk jupyter notebook

# 配置Jupyter Notebook允许远程访问
RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.ip = '*'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py

# 设置Jupyter密码为'quant'
RUN python -c "from notebook.auth import passwd; open('/root/.jupyter/jupyter_notebook_config.py', 'a').write(f'c.NotebookApp.password = u{repr(passwd("quant"))}\n')"

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["jupyter", "notebook"]