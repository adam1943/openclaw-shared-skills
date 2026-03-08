# OpenClaw 阿里云服务器部署指南

## 📋 前置要求

### 服务器配置
- **系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 1 核 +
- **内存**: 2GB+ (推荐 4GB)
- **磁盘**: 10GB+ 可用空间
- **网络**: 可访问外网 (下载依赖)

### 开放端口
| 端口 | 用途 | 是否必须 |
|------|------|----------|
| 22 | SSH | ✅ |
| 8080 | OpenClaw Gateway Web UI | 可选 |
| 443 | HTTPS (如配置反向代理) | 可选 |

---

## 🚀 快速部署

### 步骤 1: 连接服务器

```bash
ssh root@你的服务器 IP
```

### 步骤 2: 一键部署脚本

复制以下命令在服务器上执行：

```bash
# 下载部署脚本
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/install.sh -o install.sh

# 执行安装
chmod +x install.sh && ./install.sh
```

### 步骤 3: 配置 OpenClaw

```bash
# 编辑配置文件
nano ~/.openclaw/config.json
```

---

## 📝 手动部署（推荐）

### 1. 安装 Node.js

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
yum install -y nodejs

# 验证安装
node --version
npm --version
```

### 2. 安装 OpenClaw

```bash
npm install -g openclaw
```

### 3. 初始化配置

```bash
# 创建配置目录
mkdir -p ~/.openclaw

# 生成配置文件
openclaw init
```

### 4. 配置 Feishu (飞书)

编辑 `~/.openclaw/config.json`:

```json
{
  "feishu": {
    "appId": "cli_a0xxx...",
    "appSecret": "xxx...",
    "botName": "OpenClaw Bot"
  },
  "gateway": {
    "port": 8080,
    "host": "0.0.0.0"
  }
}
```

### 5. 启动 Gateway

```bash
# 启动服务
openclaw gateway start

# 查看状态
openclaw gateway status

# 查看日志
openclaw gateway logs
```

---

## 🔧 配置系统服务（开机自启）

### 创建 systemd 服务

```bash
cat > /etc/systemd/system/openclaw.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/openclaw gateway start
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable openclaw
systemctl start openclaw

# 查看状态
systemctl status openclaw
```

---

## 🔐 配置阿里云安全组

登录 [阿里云控制台](https://ecs.console.aliyun.com/)

1. 进入 **网络与安全** → **安全组**
2. 找到你的实例对应的安全组
3. 添加入站规则：

| 端口范围 | 授权对象 | 描述 |
|----------|----------|------|
| 22/22 | 你的 IP | SSH 管理 |
| 8080/8080 | 0.0.0.0/0 | OpenClaw Gateway |

---

## 🧪 验证部署

```bash
# 检查 Gateway 状态
openclaw gateway status

# 测试连接
curl http://localhost:8080/health

# 查看日志
openclaw gateway logs --tail 50
```

---

## 📱 飞书机器人配置

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret

### 2. 配置应用权限

需要以下权限：
- 消息读写
- 机器人管理
- 用户信息读取

### 3. 配置事件订阅

- 订阅类型：事件订阅
- 加密策略：不加密 (或配置密钥)
- 订阅事件：
  - `im.message.receive_v1`
  - `im.message.reply`

### 4. 配置请求地址

```
https://你的服务器IP:8080/feishu/webhook
```

---

## 🔍 故障排查

### Gateway 无法启动

```bash
# 查看详细日志
openclaw gateway logs --level debug

# 检查端口占用
netstat -tlnp | grep 8080

# 检查 Node.js 版本
node --version  # 需要 18+
```

### 飞书消息不响应

1. 检查飞书应用配置
2. 验证事件订阅 URL 可访问
3. 检查服务器防火墙
4. 验证 App ID/Secret 配置

### 内存不足

```bash
# 查看内存使用
free -h

# 添加 swap (如果内存<2GB)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

---

## 📊 监控与维护

### 查看资源使用

```bash
# CPU/内存
htop

# 磁盘使用
df -h

# 日志大小
du -sh ~/.openclaw/logs/
```

### 日志轮转

```bash
cat > /etc/logrotate.d/openclaw << 'EOF'
~/.openclaw/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 更新 OpenClaw

```bash
npm update -g openclaw
openclaw gateway restart
```

---

## 📞 获取帮助

- 文档：https://docs.openclaw.ai
- 社区：https://discord.com/invite/clawd
- GitHub: https://github.com/openclaw/openclaw

---

## ✅ 部署检查清单

- [ ] Node.js 已安装 (v18+)
- [ ] OpenClaw 已全局安装
- [ ] 配置文件已创建
- [ ] 飞书应用已配置
- [ ] 安全组端口已开放
- [ ] Gateway 服务已启动
- [ ] systemd 服务已配置 (可选)
- [ ] 测试消息已发送成功
