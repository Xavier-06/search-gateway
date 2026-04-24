# 详细配置指南

## 环境要求

### 必须
- Python 3.9+
- pip

### 推荐
- Docker（运行 SearXNG）
- 代理服务（国内必需）

## 安装步骤

### Step 1: 安装 Python 依赖

```bash
pip install ddgs scrapling yfinance requests
```

### Step 2: 安装 SearXNG

#### 方式 A: Docker（推荐）

```bash
# 启动 SearXNG
./scripts/start_searxng.sh

# 验证
curl http://127.0.0.1:8888/healthz
```

#### 方式 B: 直接安装

```bash
# Ubuntu/Debian
apt-get install searxng

# macOS
brew install searxng
```

### Step 3: 配置（国内用户）

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 国内代理地址（根据你的代理软件填写）
PROXY_URL=http://127.0.0.1:7897

# SearXNG 地址
SEARXNG_URL=http://127.0.0.1:8888
```

### Step 4: 验证

```bash
python scripts/search_gateway.py --verify
```

预期输出：
```json
{
  "ddg": true,
  "searxng": true,
  "searxng_url": "http://127.0.0.1:8888",
  "scrapling": true,
  "yfinance": true,
  "proxy": true,
  "proxy_url": "http://127.0.0.1:7897"
}
```

## 代理配置

### Clash（macOS）

```env
PROXY_URL=http://127.0.0.1:7897
```

### V2Ray

```env
PROXY_URL=socks5://127.0.0.1:1080
```

### Surge（macOS/iOS）

```env
PROXY_URL=http://127.0.0.1:6153
```

## SearXNG 配置

### 启用中文引擎

编辑 `~/.searxng/settings.yml`：

```yaml
engines:
  - name: baidu
    engine: baidu
    shortcut: bd

  - name: bing
    engine: bing
    shortcut: b

  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
```

重启 SearXNG：
```bash
docker restart searxng
```

## WorkBuddy 集成

### 安装 Skill

```bash
# 复制 skill 到 WorkBuddy
cp -r skills/search-gateway ~/.workbuddy/skills/

# 或创建 symlink
ln -s $(pwd)/skills/search-gateway ~/.workbuddy/skills/search-gateway
```

### 使用

在 WorkBuddy 对话中直接使用：
- "帮我搜索 XXX"
- "查一下 XXX 的新闻"
- "看看 XXX 的估值"

## 故障排查

### 问题：SearXNG 连接超时

```bash
# 检查 SearXNG 是否运行
docker ps | grep searxng

# 重启
docker restart searxng
```

### 问题：DDG 搜索失败

```bash
# 测试 DDG
python -c "from ddgs import DDGS; list(DDGS().text('test', max_results=1))"
```

### 问题：代理连接失败

```bash
# 检查代理是否运行
curl -x http://127.0.0.1:7897 https://www.google.com
```

## 性能优化

### 并发搜索

系统默认会并发调用多个引擎，如需调整：

```python
# 修改 search_many 并发数
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(search, q): q for q in queries}
```

### 缓存

搜索结果默认不缓存，可接入 Redis：

```python
# 可选：添加缓存层
import redis
r = redis.Redis()
```
