#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文金句库 API - FastAPI 实现

提供随机金句、主题分类查询、搜索、情绪标签查询等接口。

启动方式:
    uvicorn api:app --reload --port 8000
    或
    python api.py

API文档: http://localhost:8000/docs
"""

import json
import os
import random
from typing import List, Optional
from collections import Counter

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ---------- 数据加载 ----------

def load_quotes():
    """加载金句数据"""
    path = os.path.join(os.path.dirname(__file__), 'data', 'quotes.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到数据文件 {path}")
        return []
    except json.JSONDecodeError:
        print(f"错误: 数据文件格式错误 {path}")
        return []


# 全局加载
quotes_data = load_quotes()


# ---------- 数据模型 ----------

class Quote(BaseModel):
    """金句模型"""
    id: str
    content: str
    author: str
    source: str
    theme: str
    emotion: List[str]
    tags: List[str]


class QuoteList(BaseModel):
    """金句列表"""
    count: int
    quotes: List[Quote]


class ThemeQuotes(BaseModel):
    """主题分类结果"""
    theme: str
    count: int
    quotes: List[Quote]


class Stats(BaseModel):
    """统计信息"""
    total: int
    themes: dict
    emotion_tags: dict
    top_authors: List[dict]


# ---------- 应用初始化 ----------

app = FastAPI(
    title="中文金句库 API",
    description="一个提供中文名言警句检索的 API，支持随机获取、主题分类、关键词搜索等功能。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 工具函数 ----------

def search_quotes(keyword: str, author: Optional[str] = None) -> List[dict]:
    """搜索金句"""
    results = []
    kw = keyword.lower()
    for q in quotes_data:
        if kw in q.get('content', '').lower() or kw in q.get('author', '').lower() or kw in q.get('source', '').lower():
            if author:
                if author.lower() not in q.get('author', '').lower():
                    continue
            results.append(q)
    return results


# ---------- API 路由 ----------

@app.get("/")
def root():
    """根路径"""
    return {
        "name": "中文金句库 API",
        "version": "1.0.0",
        "total_quotes": len(quotes_data),
        "docs": "/docs"
    }


@app.get("/api/random", response_model=QuoteList, tags=["金句接口"])
def get_random_quotes(count: int = Query(1, ge=1, le=20, description="返回数量，最大20")):
    """
    获取随机金句

    - `count`: 返回数量，默认1，最大20
    """
    if not quotes_data:
        raise HTTPException(status_code=500, detail="数据为空")

    selected = random.sample(quotes_data, min(count, len(quotes_data)))
    return QuoteList(count=len(selected), quotes=selected)


@app.get("/api/theme/{theme}", response_model=ThemeQuotes, tags=["金句接口"])
def get_quotes_by_theme(theme: str):
    """
    按主题分类查询金句

    - `theme`: 主题名称（如：励志、哲学、爱情、学习、处世等）
    """
    results = [q for q in quotes_data if q.get('theme', '').lower() == theme.lower()]

    if not results:
        # 尝试模糊匹配
        results = [q for q in quotes_data if theme.lower() in q.get('theme', '').lower()]

    if not results:
        # 列出可用主题
        themes = set(q.get('theme', '') for q in quotes_data)
        raise HTTPException(
            status_code=404,
            detail=f"未找到主题为 '{theme}' 的金句。可用主题: {', '.join(sorted(themes))}"
        )

    return ThemeQuotes(theme=theme, count=len(results), quotes=results)


@app.get("/api/search", response_model=QuoteList, tags=["搜索接口"])
def search_quotes_endpoint(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    author: Optional[str] = Query(None, description="按作者过滤（可选）")
):
    """
    搜索金句

    - `q`: 关键词，在内容、作者、出处中搜索
    - `author`: 按作者过滤（可选）
    """
    results = search_quotes(q, author)

    if not results:
        return QuoteList(count=0, quotes=[])

    return QuoteList(count=len(results), quotes=results)


@app.get("/api/emotion/{emotion}", response_model=QuoteList, tags=["金句接口"])
def get_quotes_by_emotion(emotion: str):
    """
    按情绪标签查询金句

    - `emotion`: 情绪标签（如：温暖、豪迈、深情、宁静等）
    """
    results = [
        q for q in quotes_data
        if any(emotion.lower() in e.lower() for e in q.get('emotion', []))
    ]

    if not results:
        all_emotions = set()
        for q in quotes_data:
            for e in q.get('emotion', []):
                all_emotions.add(e)
        raise HTTPException(
            status_code=404,
            detail=f"未找到情绪标签为 '{emotion}' 的金句。可用情绪标签: {', '.join(sorted(all_emotions))}"
        )

    return QuoteList(count=len(results), quotes=results)


@app.get("/api/author/{author}", response_model=QuoteList, tags=["搜索接口"])
def get_quotes_by_author(author: str):
    """
    按作者查询金句

    - `author`: 作者名称
    """
    results = [q for q in quotes_data if author.lower() in q.get('author', '').lower()]

    if not results:
        authors = set(q.get('author', '') for q in quotes_data)
        raise HTTPException(
            status_code=404,
            detail=f"未找到作者 '{author}' 的金句。可用作者: {', '.join(sorted(authors))}"
        )

    return QuoteList(count=len(results), quotes=results)


@app.get("/api/stats", response_model=Stats, tags=["统计接口"])
def get_stats():
    """
    获取金句库统计信息

    返回总数、主题分布、情绪标签分布、热门作者等。
    """
    theme_counter = Counter(q.get('theme', '未分类') for q in quotes_data)
    emotion_counter = Counter()
    for q in quotes_data:
        for e in q.get('emotion', []):
            emotion_counter[e] += 1
    author_counter = Counter(q.get('author', '佚名') for q in quotes_data)

    # 按主题统计
    themes = {theme: count for theme, count in sorted(theme_counter.items(), key=lambda x: -x[1])}

    # 按情绪标签统计
    emotions = {e: count for e, count in sorted(emotion_counter.items(), key=lambda x: -x[1])}

    # 热门作者
    top_authors = [
        {"author": author, "count": count}
        for author, count in author_counter.most_common(15)
    ]

    return Stats(
        total=len(quotes_data),
        themes=themes,
        emotion_tags=emotions,
        top_authors=top_authors
    )


# ---------- 启动入口 ----------

if __name__ == '__main__':
    import uvicorn
    print(f"中文金句库 API 启动中...")
    print(f"金句总数: {len(quotes_data)}")
    print(f"API文档: http://localhost:8000/docs")
    print(f"按 Ctrl+C 停止")
    uvicorn.run(app, host="0.0.0.0", port=8000)