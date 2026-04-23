#!/usr/bin/env python3
"""
SearXNG 管理脚本 - 启动/停止/检查 SearXNG 实例
"""
import os
import sys
import subprocess
import requests

SEARXNG_PORT = os.getenv("SEARXNG_PORT", "8888")
SEARXNG_URL = f"http://127.0.0.1:{SEARXNG_PORT}"


def check_health() -> bool:
    """检查 SearXNG 是否运行。"""
    try:
        r = requests.get(f"{SEARXNG_URL}/healthz", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def start_docker() -> bool:
    """用 Docker 启动 SearXNG。"""
    print("🚀 启动 SearXNG (Docker)...")

    # 检查 Docker 是否安装
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
    except Exception:
        print("❌ Docker 未安装，请先安装 Docker: https://docs.docker.com/get-docker/")
        return False

    # 检查是否已存在容器
    try:
        subprocess.run(["docker", "inspect", "searxng"], capture_output=True, check=True)
        print("📦 容器已存在，启动中...")
        subprocess.run(["docker", "start", "searxng"], check=True)
    except Exception:
        # 创建新容器
        cmd = [
            "docker", "run", "-d",
            "--name", "searxng",
            "-p", f"{SEARXNG_PORT}:8888",
            "-v", f"{os.path.expanduser('~')}/.searxng:/etc/searxng",
            "-e", "SEARXNG_BASE_URL=http://localhost:{}/".format(SEARXNG_PORT),
            "--restart", "unless-stopped",
            "searxng/searxng:latest"
        ]
        subprocess.run(cmd, check=True)
        print("✅ SearXNG 容器已创建并启动")

    # 等待启动
    print("⏳ 等待 SearXNG 启动...")
    for i in range(30):
        if check_health():
            print(f"✅ SearXNG 已就绪: {SEARXNG_URL}")
            return True
        import time
        time.sleep(1)

    print("❌ SearXNG 启动超时")
    return False


def stop_docker() -> bool:
    """停止 SearXNG Docker 容器。"""
    try:
        subprocess.run(["docker", "stop", "searxng"], check=True)
        print("✅ SearXNG 已停止")
        return True
    except Exception:
        print("❌ 停止 SearXNG 失败")
        return False


def status() -> str:
    """查看 SearXNG 状态。"""
    if check_health():
        return f"✅ 运行中: {SEARXNG_URL}"
    else:
        return f"❌ 未运行 (期望: {SEARXNG_URL})"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(status())
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "start":
        start_docker()
    elif cmd == "stop":
        stop_docker()
    elif cmd == "restart":
        stop_docker()
        start_docker()
    elif cmd == "status":
        print(status())
    elif cmd == "logs":
        subprocess.run(["docker", "logs", "-f", "searxng"])
    else:
        print(f"未知命令: {cmd}")
        print("用法: searxng_manager.py [start|stop|restart|status|logs]")
