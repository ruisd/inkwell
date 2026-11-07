# StoryForge — 快速启动

本地 AI 写作学习系统：图书馆 → 联想网络 → 灵感引擎 → 故事框架生成 → 自主学习进化。

## 启动方式

```bash
cd inkwell
PYTHONPATH="..:." python3 cli.py           # 交互式
PYTHONPATH="..:." python3 cli.py ingest <book-path>   # 入库
PYTHONPATH="..:." python3 cli.py query "<prompt>"     # 生成故事框架
```

环境变量: `DEEPSEEK_API_KEY` (Layer 4 框架生成需要)

## 交互命令一览

| 命令 | 作用 |
|------|------|
| `library` | 浏览已入库书籍 |
| `ingest <PATH>` | 导入 txt/md/epub 书籍 |
| `extract ALL` | 批量提取 12 维特征卡片 |
| `search <TERM>` | 三路混合检索 (向量+FTS+结构化) |
| `query <PROMPT>` | 生成完整故事框架 JSON |
| `report` | 联想网络 + 进化统计 |

## 架构

```
Layer 1: library/     → 图书馆 (下载·解析·入库·分章)
Layer 2: profiles/ + network/ → 特征卡片 + 联想网络 (向量相似·交叉索引·知识图谱)
Layer 3: inspiration/ → 灵感引擎 (情节模式·人物原型·叙事节奏·桥段解构)
Layer 4: forge/composer.py → 故事框架生成 (RAG检索 → DeepSeek → JSON框架)
Layer 5: forge/learner.py  → 自主学习 (评分·收录·进化)
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `cli.py` | 交互式命令行入口 |
| `config.yaml` | 全局配置 (模型/嵌入/路径) |
| `setup_db.py` | SQLite 建表 (8张表) |
| `library/catalog.py` | 所有 CRUD 操作 |
| `library/librarian.py` | 完整入库管道 |
| `profiles/extractor.py` | 12维特征提取 |
| `network/multi_recall.py` | 三路召回 |
| `forge/composer.py` | 框架生成 |
| `forge/learner.py` | 自主学习 |

## 依赖

- Python 3.12+ (DSH 捆绑可用)
- pip 包: pyyaml, lancedb, sentence-transformers, torch, openai, pydantic
- 已缓存模型: BAAI/bge-m3 (~/.cache/huggingface/)