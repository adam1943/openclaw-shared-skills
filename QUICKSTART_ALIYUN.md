# OpenClaw 阿里云部署 - 快速参考卡

## 🚀 3 步部署

### 1️⃣ 连接服务器
```bash
ssh root@你的服务器IP
```

### 2️⃣ 执行部署脚本
```bash
# 上传脚本
scp install-openclaw.sh root@你的服务器 IP:/root/

# 执行
ssh root@你的服务器 IP
chmod +x install-openclaw.sh
./install-openclaw.sh
```

### 3️⃣ 配置飞书
```bash
nano ~/.openclaw/config.json
# 修改后重启
openclaw gateway restart
```

---

## 📋 必要配置

### 阿里云安全组
| 端口 | 授权对象 | 说明 |
|------|----------|------|
| 22 | 你的 IP | SSH |
| 8080 | 0.0.0.0/0 | Gateway |

### 飞书开放平台
- **App ID**: `cli_xxx`
- **App Secret**: `xxx`
- **事件订阅 URL**: `http://你的服务器IP:8080/feishu/webhook`

---

## 🔧 常用命令

```bash
# 查看状态
openclaw gateway status
systemctl status openclaw

# 查看日志
openclaw gateway logs
journalctl -u openclaw -f

# 重启服务
openclaw gateway restart
systemctl restart openclaw

# 停止服务
openclaw gateway stop
systemctl stop openclaw

# 更新
npm update -g openclaw
openclaw gateway restart
```

---

## 🐛 故障排查

```bash
# 检查端口
netstat -tlnp | grep 8080

# 检查进程
ps aux | grep openclaw

# 查看日志
tail -f ~/.openclaw/logs/*.log

# 测试连接
curl http://localhost:8080/health
```

---

## 📞 需要帮助？

1. 查看完整文档：`DEPLOY_ALIYUN.md`
2. 官方文档：https://docs.openclaw.ai
3. 社区：https://discord.com/invite/clawd
