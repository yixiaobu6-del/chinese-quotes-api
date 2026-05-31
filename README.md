# 中文金句库 API

一个基于 FastAPI 构建的中文金句（名言警句）检索 API，提供随机金句、分类查询、关键词搜索等功能。

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn api:app --reload --port 8000
# 或
python api.py
```

服务启动后访问 http://localhost:8000/docs 查看 Swagger API 文档。

**网页版**：打开 `web/index.html` 可直接使用，无需启动后端（内置120+条金句）。

## API 文档

### 基础信息

- Base URL: `http://localhost:8000`
- 全部接口返回 JSON 格式，UTF-8 编码

### 接口列表

#### 1. 获取随机金句

```
GET /api/random
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| count | int | 否 | 返回数量，默认1，最大20 |

**示例：**
```bash
curl http://localhost:8000/api/random
curl http://localhost:8000/api/random?count=3
```

**返回示例：**
```json
{
  "count": 1,
  "quotes": [
    {
      "id": "q_001",
      "content": "路漫漫其修远兮，吾将上下而求索。",
      "author": "屈原",
      "source": "《离骚》",
      "theme": "励志",
      "emotion": ["坚定", "追求"]
    }
  ]
}
```

#### 2. 按主题分类查询

```
GET /api/theme/{theme}
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| theme | str | 是 | 主题名称（励志/哲学/爱情/学习/处世等） |

**示例：**
```bash
curl http://localhost:8000/api/theme/励志
```

**返回：**
```json
{
  "theme": "励志",
  "count": 25,
  "quotes": [...]
}
```

#### 3. 搜索金句

```
GET /api/search
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | str | 是 | 关键词 |
| author | str | 否 | 按作者过滤 |

**示例：**
```bash
curl "http://localhost:8000/api/search?q=天"
curl "http://localhost:8000/api/search?q=奋斗&author=鲁迅"
```

#### 4. 按情绪标签查询

```
GET /api/emotion/{emotion}
```

**示例：**
```bash
curl http://localhost:8000/api/emotion/温暖
```

#### 5. 获取统计信息

```
GET /api/stats
```

**返回：**
```json
{
  "total": 110,
  "themes": {"励志": 25, "哲学": 18, ...},
  "top_authors": [...]
}
```

#### 6. 按作者查询

```
GET /api/author/{author}
```

**示例：**
```bash
curl http://localhost:8000/api/author/苏轼
```

## 数据格式

每句金句的 JSON 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| content | string | 金句内容 |
| author | string | 作者 |
| source | string | 出处 |
| theme | string | 主题分类 |
| emotion | array[string] | 情绪标签 |
| tags | array[string] | 附加标签 |

## License

MIT License
