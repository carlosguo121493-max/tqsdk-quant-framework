# GitHub代码推送指南

由于自动化环境中的网络限制，您需要在自己的本地环境中完成代码的最后推送步骤。以下是详细的操作指南：

## 前提条件

1. 确保您的电脑已安装Git
2. 确保您有GitHub账号（用户名：carlosguo121493-max）
3. 确保您的项目代码已在本地（路径：/Users/weiguo/quant/tqsdk）

## 操作步骤

### 方法一：使用HTTPS协议（推荐）

1. 打开终端（Terminal）应用程序
2. 进入项目目录：
   ```bash
   cd /Users/weiguo/quant/tqsdk
   ```
3. 执行推送命令：
   ```bash
   git push -u origin main
   ```
4. 当系统提示输入GitHub凭据时，输入您的GitHub用户名和密码（或个人访问令牌）

   > **注意**：GitHub现在推荐使用个人访问令牌（Personal Access Token）代替密码。如果您还没有个人访问令牌，可以按照GitHub官方文档创建一个。

### 方法二：使用SSH协议（更安全、无需重复输入密码）

如果您想使用SSH协议，可以按照以下步骤配置：

1. 检查是否已有SSH密钥：
   ```bash
   ls -al ~/.ssh
   ```

2. 如果没有SSH密钥，生成一个新的：
   ```bash
   ssh-keygen -t ed25519 -C "guowei@shnow.cn"
   ```
   按照提示完成操作，通常可以使用默认值。

3. 启动SSH代理并添加密钥：
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add -K ~/.ssh/id_ed25519
   ```

4. 复制SSH公钥内容：
   ```bash
   pbcopy < ~/.ssh/id_ed25519.pub
   ```

5. 登录GitHub，进入"Settings" > "SSH and GPG keys" > "New SSH key"，粘贴公钥并保存

6. 将本地仓库的远程地址更改为SSH格式：
   ```bash
   git remote set-url origin git@github.com:carlosguo121493-max/tqsdk-quant-framework.git
   ```

7. 测试SSH连接：
   ```bash
   ssh -T git@github.com
   ```
   如果成功，会显示一条欢迎消息。

8. 执行推送：
   ```bash
   git push -u origin main
   ```

## 常见问题解决

1. **HTTP2连接错误**
   如果遇到"Error in the HTTP2 framing layer"错误，可以禁用HTTP2协议：
   ```bash
   git config --global http.version HTTP/1.1
   ```

2. **连接超时**
   如果遇到连接超时问题，检查您的网络连接或防火墙设置，确保允许GitHub的连接。

3. **权限问题**
   确保您的GitHub账号有足够的权限访问和修改`tqsdk-quant-framework`仓库。

## 完成推送后

成功推送后，您可以在浏览器中访问以下地址查看您的仓库：
https://github.com/carlosguo121493-max/tqsdk-quant-framework

如果您在操作过程中遇到任何问题，可以参考GitHub官方文档或搜索相关错误信息获取帮助。