# Search Gateway - WorkBuddy 搜索系统

多引擎融合搜索系统，专为投研/情报场景设计，支持中文/英文/新闻/金融多维搜索。

## 功能特性

- 🔍 **多引擎融合** - DuckDuckGo + SearXNG + Google 三路搜索自动补位
- 🌐 **中文优化** - 中文查询自动路由到最优引擎
- 📰 **新闻搜索** - 支持时间过滤的新闻检索
- 💰 **金融估值** - 股票/基金实时行情（yfinance）
- 📄 **深度抓取** - 自动抓取页面正文内容
- 🔄 **自动降级** - 某引擎失败时自动切换

## 快速开始

### 0. 关联脚本目录（重要！）

```bash
# skill 和 scripts 在同一仓库时，需要建立 symlink
ln -s scripts skills/search-gateway/scripts
```

### 1. 安装依赖

```bash
pip install ddgs scrapling yfinance requests
```

### 2. 启动 SearXNG

```bash
# macOS/Linux
./scripts/start_searxng.sh

# Windows (Docker Desktop)
docker run -d --name searxng -p 8888:8888 searxng/searxng:latest
```

### 3. 配置代理（国内用户必需）

```bash
cp .env.example .env
# 编辑 .env，填写你的代理地址
```

### 4. 验证安装

```bash
python scripts/search_gateway.py --verify
```

## 使用示例

### 命令行搜索

```bash
# 基础搜索
python scripts/search_gateway.py "特斯拉 2025 财报"

# 指定引擎
python scripts/search_gateway.py "AI startup funding 2025" --prefer ddg

# 深度搜索（抓取正文）
python scripts/search_gateway.py "OpenAI GPT-5" --deep

# JSON 输出
python scripts/search_gateway.py "比亚迪销量" --json
```

### Python 调用

```python
from scripts.search_gateway import search, search_deep, search_many

# 基础搜索
results = search("宁德时代 毛利率", max_results=10)

# 深度搜索
results = search_deep("OpenAI 最新动态", max_results=5, fetch_top_n=3)

# 批量搜索
results = search_many(["query1", "query2"], max_results=8)
```

### 新闻搜索

```bash
python scripts/search_news.py "AI 监管" -t w -n 20
```

## 引擎说明

| 引擎 | 状态 | 说明 |
|------|------|------|
| DuckDuckGo | ✅ 必需 | 中文/英文主力搜索 |
| SearXNG | ✅ 推荐 | 本地实例，支持多引擎聚合 |
| Google | ⚠️ 可选 | 需要代理 |
| scrapling | ⚠️ 可选 | 页面正文抓取 |
| yfinance | ⚠️ 可选 | 金融数据 |

## 目录结构

```
search-gateway/
├── scripts/
│   ├── search_gateway.py      # 核心搜索网关
│   ├── search_router.py       # 查询路由
│   ├── search_news.py         # 新闻搜索
│   ├── searxng_manager.py     # SearXNG 管理
│   └── start_searxng.sh       # 启动脚本
├── config/
│   └── searxng/
│       └── settings.yml       # SearXNG 配置
├── skills/
│   └── search-gateway/
│       └── SKILL.md           # WorkBuddy Skill
├── .env.example               # 环境变量示例
├── INSTALL.sh                 # 安装脚本
├── SETUP_GUIDE.md             # 详细配置指南
└── README.md
```

## WorkBuddy 集成

1. 复制到 WorkBuddy skills 目录：
   ```bash
   cp -r skills/search-gateway ~/.workbuddy/skills/
   ```

2. 在对话中即可使用搜索功能

## 常见问题

### Q: SearXNG 启动失败？
```bash
# 检查 Docker 是否运行
docker ps

# 查看日志
docker logs searxng
```

### Q: 中文搜索返回空结果？
```bash
# 验证 DDG 是否可用
python -c "from ddgs import DDGS; print('OK')"
```

### Q: 需要代理吗？
- 国内用户：需要代理（配置 PROXY_URL）
- 海外用户：可选

## License

MIT
