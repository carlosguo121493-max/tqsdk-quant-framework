# 量化交易策略交互平台

基于Flask的量化交易策略交互网页，提供策略选择、参数配置、回测运行和结果可视化功能。

## 通过Docker部署

### 前提条件
- 已安装Docker和Docker Compose
- 克隆了量化交易策略项目代码

### 部署步骤

1. 进入项目根目录
```bash
cd /path/to/quant/tqsdk
```

2. 使用Docker Compose启动所有服务
```bash
docker-compose up -d --build
```

此命令将构建并启动以下服务：
- **quant-jupyter**: Jupyter Notebook服务 (端口8888)
- **quant-web**: 量化交易策略交互网页服务 (端口5000)
- **quant-tests**: 测试服务 (可选)

3. 访问服务
   - Jupyter Notebook: [http://localhost:8888](http://localhost:8888) (密码: quant)
   - 策略交互网页: [http://localhost:5000](http://localhost:5000)

### 服务说明

#### quant-web服务
- 基于Flask框架构建的Web应用
- 提供策略选择、参数配置、回测运行和结果可视化功能
- 支持简单均线交叉、多均线和玻璃位三种策略
- 使用Chart.js进行数据可视化

#### 可用API接口
- `/api/strategies`: 获取可用策略列表
- `/api/strategy_params/<strategy_id>`: 获取特定策略的参数配置
- `/api/run_backtest`: 运行回测并返回结果

### 环境变量配置
当前配置中不需要额外的环境变量，所有设置已在代码中定义。

### 数据持久化
通过Docker Compose的卷映射，以下目录会在容器重启后保留数据：
- `./web`: 网页应用代码
- `./framework`: 量化交易框架代码
- `./strategies`: 策略实现代码
- `./data`: 数据存储目录

### 停止服务
```bash
docker-compose down
```

### 查看服务日志
```bash
docker-compose logs -f quant-web
```

## 开发模式

### 本地开发环境设置

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行Flask应用
```bash
cd web
python app.py
```

应用将在 [http://localhost:5000](http://localhost:5000) 启动。

## 注意事项
- 本平台仅用于策略测试，不构成投资建议
- 模拟数据仅供演示使用，实际回测结果可能有所不同
- 在生产环境中，应使用WSGI服务器（如Gunicorn）运行Flask应用