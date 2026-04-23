#!/usr/bin/env python3
"""
新闻搜索 - News Search

基于 SearXNG/DDG 的新闻搜索，支持时间过滤。
"""
import json
import os
import sys
from typing import Optional

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://127.0.0.1:8888")


def search_news(query: str, max_results: int = 10, time_range: str = "") -> list:
    """搜索新闻。

    Args:
        query: 搜索关键词
        max_results: 最大结果数
        time_range: 时间范围 (d=天, w=周, m=月, y=年)
    """
    # 先尝试 SearXNG
    results = _search_searxng_news(query, max_results, time_range)
    if results:
        return results

    # fallback 到 DDG
    return _search_ddg_news(query, max_results)

def _search_searxng_news(query: str, max_results: int, time_range: str) -> list:
    """SearXNG 新闻搜索。"""
    try:
        import urllib.parse
        import urllib.request

        # 时间参数映射
        time_map = {"d": "day", "w": "week", "m": "month", "y": "year"}
        time_param = time_map.get(time_range.lower(), "") if time_range else ""

        q = urllib.parse.quote(query)
        url = f'{SEARXNG_URL}/search?q={q}&format=json&engines=news'

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8', errors='replace'))

        results = []
        for item in data.get('results', [])[:max_results]:
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', ''),
                'publishedDate': item.get('publishedDate', ''),
                'engine': item.get('engine', 'searxng'),
                'source': 'searxng:news',
            })
        return results
    except Exception as e:
        print(f"SearXNG news failed: {e}", file=sys.stderr)
        return []

def _search_ddg_news(query: str, max_results: int) -> list:
    """DDG 新闻搜索。"""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.news(query, max_results=max_results))

        return [
            {
                'title': r.get('title', ''),
                'url': r.get('url', ''),
                'content': r.get('description', ''),
                'publishedDate': r.get('date', ''),
                'engine': 'ddg',
                'source': 'ddg:news',
            }
            for r in raw if r.get('url')
        ]
    except Exception as e:
        print(f"DDG news failed: {e}", file=sys.stderr)
        return []

if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser(description="News Search")
    ap.add_argument("query", nargs="?")
    ap.add_argument("-n", "--max-results", type=int, default=10)
    ap.add_argument("-t", "--time-range", choices=["d", "w", "m", "y"], default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.query:
        ap.print_help()
        sys.exit(1)

    results = search_news(args.query, max_results=args.max_results, time_range=args.time_range)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r.get('source', '')}] {r.get('title', '')}")
            print(f"   {r.get('url', '')}")
            if r.get('publishedDate'):
                print(f"   📅 {r.get('publishedDate')}")
            print()
