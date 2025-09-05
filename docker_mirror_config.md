# Docker 国内镜像源配置指南

由于网络原因，从Docker Hub拉取镜像可能会遇到问题。配置国内镜像源可以显著提升镜像拉取速度和成功率。

## macOS Docker Desktop 配置方法

### 方法一：通过Docker Desktop UI配置（推荐）

1. 打开Docker Desktop应用
2. 点击顶部菜单栏中的Docker图标，选择"Preferences..."（偏好设置）
3. 在左侧导航栏选择"Docker Engine"（Docker引擎）
4. 在配置编辑器中添加或修改`registry-mirrors`配置
5. 点击"Apply & Restart"（应用并重启）按钮保存设置

配置示例：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com",
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

### 方法二：通过命令行配置

1. 打开终端
2. 创建或编辑Docker配置文件：
```bash
mkdir -p ~/.docker
nano ~/.docker/daemon.json
```
3. 添加以下内容（使用您选择的编辑器）：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com",
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```
4. 保存文件并重启Docker服务：
```bash
# 在macOS上，您可以通过Docker Desktop应用重启，或者使用以下命令
killall Docker && open -a Docker
```

## 验证配置是否生效

配置完成后，可以使用以下命令验证镜像源是否生效：
```bash
docker info
```

在输出信息中，查看"Registry Mirrors"部分，确认您配置的镜像源是否已列出。

## 国内常用Docker镜像源

1. **中国科学技术大学镜像源**：https://docker.mirrors.ustc.edu.cn
2. **Docker中国官方镜像**：https://registry.docker-cn.com
3. **腾讯云镜像源**：https://mirror.ccs.tencentyun.com
4. **网易云镜像源**：https://hub-mirror.c.163.com
5. **百度云镜像源**：https://mirror.baidubce.com

## 配置完成后重启服务

配置完成并验证后，您可以再次尝试启动我们的量化交易平台服务：
```bash
docker-compose up -d --build
```

## 注意事项

- 不同地区可能对不同镜像源的访问速度有所差异，可以根据实际情况选择或调整镜像源顺序
- 如果配置后仍然遇到问题，可以尝试重启Docker Desktop应用或重启计算机
- 部分企业网络可能需要配置代理才能访问外部资源，如果上述方法无效，请咨询网络管理员