#!/bin/bash
# OpenClaw 阿里云一键部署脚本
# 使用方法：curl -fsSL https://xxx/install-openclaw.sh | bash

set -e

echo "============================================================"
echo "  OpenClaw 阿里云服务器部署脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 用户运行此脚本 (sudo -i)"
    exit 1
fi

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    log_info "检测到操作系统：$OS $VERSION"
}

# 安装 Node.js
install_nodejs() {
    log_info "正在安装 Node.js 20.x..."
    
    case $OS in
        ubuntu|debian)
            curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
            apt-get update
            apt-get install -y nodejs
            ;;
        centos|rhel|rocky|almalinux)
            curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
            yum install -y nodejs
            ;;
        *)
            log_error "不支持的操作系统：$OS"
            exit 1
            ;;
    esac
    
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    log_info "Node.js 已安装：$NODE_VERSION"
    log_info "npm 已安装：$NPM_VERSION"
}

# 安装 OpenClaw
install_openclaw() {
    log_info "正在安装 OpenClaw..."
    npm install -g openclaw
    
    OPENCLAW_VERSION=$(openclaw --version 2>/dev/null || echo "未知")
    log_info "OpenClaw 已安装：$OPENCLAW_VERSION"
}

# 创建配置目录
setup_config() {
    log_info "正在创建配置目录..."
    mkdir -p ~/.openclaw
    mkdir -p ~/.openclaw/workspace
    mkdir -p ~/.openclaw/logs
    
    # 创建基础配置文件
    if [ ! -f ~/.openclaw/config.json ]; then
        cat > ~/.openclaw/config.json << 'EOF'
{
  "gateway": {
    "port": 8080,
    "host": "0.0.0.0"
  },
  "feishu": {
    "appId": "YOUR_APP_ID",
    "appSecret": "YOUR_APP_SECRET"
  }
}
EOF
        log_info "已创建配置文件：~/.openclaw/config.json"
        log_warn "请编辑配置文件，填入你的飞书 App ID 和 Secret"
    fi
}

# 配置 systemd 服务
setup_systemd() {
    log_info "正在配置 systemd 服务..."
    
    cat > /etc/systemd/system/openclaw.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw
ExecStart=/usr/bin/openclaw gateway start
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production
Environment=PATH=/usr/bin:/usr/local/bin

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable openclaw
    log_info "systemd 服务已配置"
}

# 配置防火墙
setup_firewall() {
    log_info "正在配置防火墙规则..."
    
    # 检查 firewalld
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=8080/tcp
        firewall-cmd --reload
        log_info "firewalld: 已开放 8080 端口"
    fi
    
    # 检查 ufw
    if command -v ufw &> /dev/null; then
        ufw allow 8080/tcp
        log_info "ufw: 已开放 8080 端口"
    fi
    
    log_warn "请同时在阿里云控制台配置安全组，开放 8080 端口"
}

# 启动服务
start_service() {
    log_info "正在启动 OpenClaw Gateway..."
    systemctl start openclaw
    
    sleep 3
    
    if systemctl is-active --quiet openclaw; then
        log_info "OpenClaw Gateway 已启动"
    else
        log_error "OpenClaw Gateway 启动失败，查看日志：journalctl -u openclaw -f"
    fi
}

# 显示部署信息
show_info() {
    echo ""
    echo "============================================================"
    echo "  部署完成!"
    echo "============================================================"
    echo ""
    echo "📁 配置目录：~/.openclaw/"
    echo "📝 配置文件：~/.openclaw/config.json"
    echo "📊 日志目录：~/.openclaw/logs/"
    echo ""
    echo "🔧 管理命令:"
    echo "  openclaw gateway status   - 查看状态"
    echo "  openclaw gateway logs     - 查看日志"
    echo "  openclaw gateway restart  - 重启服务"
    echo "  systemctl status openclaw - 系统服务状态"
    echo ""
    echo "⚠️  下一步:"
    echo "  1. 编辑 ~/.openclaw/config.json 配置飞书应用"
    echo "  2. 在阿里云安全组开放 8080 端口"
    echo "  3. 在飞书开放平台配置事件订阅 URL"
    echo ""
    echo "📖 详细文档：DEPLOY_ALIYUN.md"
    echo ""
}

# 主流程
main() {
    detect_os
    install_nodejs
    install_openclaw
    setup_config
    setup_systemd
    setup_firewall
    start_service
    show_info
}

# 运行
main
