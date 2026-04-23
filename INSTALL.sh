#!/bin/bash
# Search Gateway 安装脚本

set -e

echo "🔍 Search Gateway 安装程序"
echo "============================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 pip
if ! command -v pip &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip 未安装"
    exit 1
fi

PIP="pip"
if ! command -v pip &> /dev/null; then
    PIP="python3 -m pip"
fi

echo "📦 安装 Python 依赖..."
$PIP install duckduckgo-search scrapling yfinance requests --quiet

echo "🐳 检查 Docker..."
if command -v docker &> /dev/null; then
    echo "🐳 启动 SearXNG..."
    ./scripts/start_searxng.sh || echo "⚠️ SearXNG 启动失败，可稍后手动启动"
else
    echo "⚠️ Docker 未安装，跳过 SearXNG（DDG 仍可正常工作）"
fi

echo "🔗 建立 scripts symlink..."
mkdir -p skills/search-gateway
if [ ! -e skills/search-gateway/scripts ]; then
    ln -s ../../scripts skills/search-gateway/scripts
    echo "✅ 已创建 symlink: skills/search-gateway/scripts -> ../../scripts"
fi

echo "🔧 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑填写代理地址"
fi

echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "  1. 编辑 .env 填写代理地址（国内用户必需）"
echo "  2. 运行: python scripts/search_gateway.py --verify"
echo "  3. 参考 SETUP_GUIDE.md 了解更多"
