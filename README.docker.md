# Docker化量化交易框架

本目录包含了将量化交易框架及其Jupyter Notebook示例Docker化所需的所有文件。通过Docker，您可以在任何支持Docker的环境中快速部署和使用本框架，无需担心环境配置问题。

## 文件结构

- `Dockerfile` - 定义Docker镜像的构建过程
- `docker-compose.yml` - 定义Docker Compose服务配置
- `.github/workflows/docker-build.yml` - 定义GitHub Actions自动构建工作流

## 本地使用方法

### 前提条件
- 已安装 [Docker](https://docs.docker.com/get-docker/)
- 已安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 使用Docker Compose启动Jupyter Notebook

1. 在项目根目录执行以下命令：
   ```bash
   docker compose up -d quant-jupyter
   ```

2. 查看Jupyter Notebook的访问信息：
   ```bash
   docker logs quant-jupyter
   ```

3. 在输出中找到类似以下的访问链接：
   ```
   http://127.0.0.1:8888/?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. 在浏览器中打开该链接，使用密码 `quant` 登录（或使用URL中的token自动登录）

5. 登录后，您可以在Notebook界面中访问和运行 `examples` 目录下的所有示例

### 停止服务

```bash
docker compose down
```

### 运行测试

```bash
docker compose up quant-tests
```

## 数据持久化

- `examples`、`framework`、`strategies` 和 `analysis_tools` 目录已挂载为卷，您对这些目录的修改会自动反映到容器中
- `data` 目录用于存储临时数据，容器内生成的数据会保存在这里

## GitHub Actions自动构建

本项目已配置GitHub Actions工作流，当您推送到`main`分支或创建Pull Request时，将自动执行以下操作：

1. 构建Docker镜像
2. 运行测试
3. （可选）推送到Docker仓库

### 手动触发交互式Notebook

您还可以通过GitHub Actions的"workflow_dispatch"事件手动触发交互式Notebook的构建和运行。不过需要注意的是，GitHub Actions环境中的Jupyter Notebook无法直接从外部访问。

## 远端操作交互

要在远端操作交互，建议采用以下方案之一：

### 方案1：使用GitHub Codespaces

1. 在GitHub仓库页面点击"Code"按钮
2. 选择"Codespaces"标签
3. 点击"Create codespace on main"
4. Codespaces会自动配置包含Docker的开发环境
5. 在Codespaces终端中执行 `docker compose up -d quant-jupyter` 启动Notebook

### 方案2：部署到云服务器

1. 在云服务器上安装Docker和Docker Compose
2. 克隆GitHub仓库
3. 执行 `docker compose up -d quant-jupyter` 启动Notebook
4. 通过云服务器的IP地址和8888端口访问Notebook

### 方案3：配置远程访问（高级）

可以在`docker-compose.yml`中添加远程访问配置，例如结合Ngrok或类似工具提供公网访问。

## 自定义配置

### 修改Jupyter密码

1. 生成新的密码哈希值：
   ```bash
   python -c "from notebook.auth import passwd; print(passwd())"
   ```

2. 在`Dockerfile`中更新密码配置

### 添加更多依赖

如果您的策略需要额外的Python库，可以在`requirements.txt`文件中添加，然后重新构建镜像：

```bash
docker compose build
```

## 常见问题

### Q: 如何查看容器日志？
A: 使用 `docker logs quant-jupyter` 命令查看Jupyter容器的日志。

### Q: 如何进入正在运行的容器？
A: 使用 `docker exec -it quant-jupyter /bin/bash` 命令进入容器的Shell。

### Q: 运行示例时遇到依赖错误怎么办？
A: 检查`requirements.txt`文件，确保所有必要的依赖都已列出，然后重新构建镜像。