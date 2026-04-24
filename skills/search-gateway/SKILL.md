---
name: search-gateway
description: 统一搜索网关，支持 DuckDuckGo/SearXNG/Google/新闻/深度抓取。当用户说"搜索"、"帮我查一下"、"找相关信息"、"看这个新闻"、"搜一下这个"、"research"、"search web"时使用。覆盖投研/新闻/情报检索场景。
---

# Search Gateway - 统一搜索网关

## 概述

多引擎融合搜索系统，支持 DuckDuckGo、SearXNG、Google 新闻搜索，以及页面深度抓取和金融估值查询。

## 核心能力

### 1. 统一搜索接口

```python
import sys
sys.path.insert(0, "<仓库根目录>")

from scripts.search_gateway import search, search_deep, search_many, verify_engines

# 基础搜索（DDG + SearXNG 自动补位）
results = search("搜索关键词", max_results=10)

# 指定引擎
results = search("关键词", prefer="ddg")      # 只用 DDG
results = search("关键词", prefer="searxng")  # 只用 SearXNG
results = search("关键词", prefer="multi")    # 三路合并

# 深度搜索（自动抓取 top 结果正文）
results = search_deep("关键词", max_results=5, fetch_top_n=3)

# 批量搜索
results = search_many(["query1", "query2", "query3"], max_results=8)
```

### 2. 新闻搜索

```python
import sys
sys.path.insert(0, "<仓库根目录>")

from scripts.search_news import search_news

results = search_news("关键词", max_results=10, time_range="w")  # 最近一周
```

### 3. 金融估值

```python
import sys
sys.path.insert(0, "<仓库根目录>")

from scripts.search_gateway import yfinance_summary

info = yfinance_summary("AAPL")  # 美股
info = yfinance_summary("9988.HK")  # 港股
info = yfinance_summary("000001.SZ")  # A股
```

### 4. 引擎健康检查

```bash
python scripts/search_gateway.py --verify
```

## 搜索栈架构

| Layer | 引擎 | 用途 |
|-------|------|------|
| 1 | DuckDuckGo | 中英文主力搜索 |
| 2 | SearXNG | Baidu/Bing 补充 |
| 3 | Google | 需要代理 |
| 4 | scrapling | 页面正文深度抓取 |
| 5 | yfinance | 金融估值数据 |

## 路由规则

- **中文查询** → DuckDuckGo（中文搜索最可靠）
- **股票代码** → DuckDuckGo
- **纯英文** → SearXNG
- **混合查询** → DuckDuckGo

## 依赖

- `ddgs`（新版 duckduckgo-search，安装命令：`pip install ddgs`）
- `scrapling`（可选，用于深度抓取）
- `yfinance`（可选，用于金融数据）
- SearXNG Docker 实例

## 安装

```bash
# 1. 安装依赖（注意：包名是 ddgs，不是 duckduckgo-search）
pip install ddgs scrapling yfinance requests

# 2. 关联脚本目录（skill 和 scripts 在同一仓库时）
# 在仓库根目录执行：
ln -s scripts skills/search-gateway/scripts

# 3. 启动 SearXNG
./scripts/start_searxng.sh

# 4. 配置代理（如需要）
cp .env.example .env
# 编辑 .env 填写 PROXY_URL

# 5. 验证
python scripts/search_gateway.py --verify
```

## 适用场景

- 投研情报搜集
- 新闻追踪
- 市场调研
- 竞品分析
- 金融数据查询
