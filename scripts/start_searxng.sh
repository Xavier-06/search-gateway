#!/bin/bash
# SearXNG 启动脚本

set -e

SEARXNG_PORT="${SEARXNG_PORT:-8888}"
SEARXNG_URL="http://127.0.0.1:${SEARXNG_PORT}"

echo "🔍 检查 SearXNG 状态..."

# 检查是否已运行
if curl -s --max-time 3 "${SEARXNG_URL}/healthz" > /dev/null 2>&1; then
    echo "✅ SearXNG 已在运行: ${SEARXNG_URL}"
    exit 0
fi

echo "🚀 启动 SearXNG..."

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "请安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 启动容器
docker run -d \
    --name searxng \
    -p "${SEARXNG_PORT}:8888" \
    -v ~/.searxng:/etc/searxng \
    -e "SEARXNG_BASE_URL=http://localhost:${SEARXNG_PORT}/" \
    --restart unless-stopped \
    searxng/searxng:latest

# 等待启动
echo "⏳ 等待 SearXNG 启动..."
for i in {1..30}; do
    if curl -s --max-time 3 "${SEARXNG_URL}/healthz" > /dev/null 2>&1; then
        echo "✅ SearXNG 已就绪: ${SEARXNG_URL}"
        exit 0
    fi
    sleep 1
done

echo "❌ SearXNG 启动超时，请检查: docker logs searxng"
