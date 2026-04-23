#!/usr/bin/env python3
"""
搜索路由 - 根据查询类型自动选择最佳引擎

路由规则：
  1. 含中文 + 不含英文 → DDG CLI（中文搜索最可靠）
  2. 含中文 + 股票代码 → DDG CLI
  3. 纯英文 → SearXNG（18080）
  4. 混合查询 → DDG CLI
"""
import os
import re
import subprocess
import sys
import json
from typing import Optional

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://127.0.0.1:8888")


def is_chinese_query(query: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in query)

def is_stock_query(query: str) -> bool:
    # 精确匹配股票代码：5位数字.HK（如 0291.HK）、4位数字.HK（如 9880.HK）、HKEX
    return bool(re.search(r'\d{4,5}\.HK|HKEX', query))

def search(query: str, max_results: int = 10, **kwargs) -> list:
    """自动路由搜索引擎。"""
    has_chinese = is_chinese_query(query)
    has_stock = is_stock_query(query)

    if has_chinese or has_stock:
        return _search_ddg(query, max_results)
    else:
        return _search_searxng(query, max_results)

def _search_ddg(query: str, max_results: int = 10) -> list:
    """DDG CLI 搜索（中文最优）。"""
    try:
        r = subprocess.run(
            ['ddgs', 'text', '-q', query, '-m', str(max_results)],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, 'LC_ALL': 'en_US.UTF-8'}
        )
        if r.returncode != 0 or not r.stdout.strip():
            return []

        results = []
        lines = r.stdout.strip().split('\n')
        current = {}

        for line in lines:
            line = line.strip()
            if line.startswith('title'):
                if current.get('title'):
                    results.append(current)
                current = {'title': line[6:].strip()[:120], 'url': '', 'content': ''}
            elif line.startswith('href'):
                current['url'] = line[5:].strip()
            elif line.startswith('body'):
                current['content'] = line[5:].strip()[:500]
            elif line.startswith('======'):
                if current.get('title'):
                    results.append(current)
                    current = {}

        if current.get('title'):
            results.append(current)

        return [
            {
                'title': r.get('title', ''),
                'url': r.get('url', ''),
                'content': r.get('content', ''),
                'engine': 'ddg',
                'source': 'ddg-cli',
            }
            for r in results[:max_results]
        ]
    except Exception as e:
        print(f"DDG failed: {e}", file=sys.stderr)
        return []

def _search_searxng(query: str, max_results: int = 10) -> list:
    """SearXNG 搜索。"""
    try:
        import urllib.parse
        import urllib.request
        q = urllib.parse.quote(query)
        url = f'{SEARXNG_URL}/search?q={q}&format=json&language=all&results={max_results}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8', errors='replace'))
        items = data.get('results', [])
        return [
            {
                'title': i.get('title', ''),
                'url': i.get('url', ''),
                'content': i.get('content', ''),
                'engine': i.get('engine', 'searxng'),
                'source': 'searxng',
            }
            for i in items[:max_results]
        ]
    except Exception as e:
        print(f"SearXNG failed: {e}", file=sys.stderr)
        return _search_ddg(query, max_results)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        queries = [
            '东江集团控股 02283 注塑模具',
            '注塑行业市场规模 2025',
            'Python tutorial',
        ]
    else:
        queries = [sys.argv[1]]

    for q in queries:
        print(f'\n🔍 "{q}"')
        results = search(q, max_results=5)
        print(f'   Found {len(results)} results')
        for r in results[:3]:
            print(f'   ✅ [{r["engine"]}] {r["title"][:80]}')
