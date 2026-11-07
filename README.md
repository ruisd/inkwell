storyforge/
├── library/                    # Layer 1: 图书馆管理层
│   ├── __init__.py
│   ├── catalog.py              # SQLite 目录（书籍档案）
│   ├── librarian.py            # 搜索+下载+入库管线
│   ├── post_process.py         # 后处理流水线（借鉴笔灵）
│   └── models.py               # 数据模型定义
│
├── profiles/                   # Layer 2: 书籍特征分析
│   ├── __init__.py
│   ├── extractor.py            # 特征卡片提取（借鉴笔灵 prompts）
│   ├── characters.py           # 人物原型聚类
│   ├── chapters.py             # 章节结构分析
│   ├── bibles.py               # 创作圣经提取（借鉴大作家）
│   └── world_elements.py       # 世界观元素管理
│
├── network/                    # Layer 3: 联想网络中英文
│   ├── __init__.py
│   ├── associations.py         # 三重联想引擎（向量+FTS+图谱）
│   └── multi_recall.py         # 多路并行召回（借鉴笔灵混合检索）
│
├── inspiration/                # Layer 4: 灵感引擎
│   ├── __init__.py
│   ├── patterns.py             # 管道A: 情节模式挖掘
│   ├── archetypes.py           # 管道B: 人物原型库查询
│   ├── structures.py           # 管道C: 叙事节奏参考
│   └── bridges.py              # 管道D: 桥段解构器
│
├── forge/                      # Layer 5: 故事框架生成器
│   ├── __init__.py
│   ├── composer.py             # Prompt组装 + LLM调用
│   ├── evaluator.py            # 评估器
│   └── learner.py              # 自主学习回路
│
├── prompts/                    # Prompt 模板目录
│   ├── extract_profile.md
│   ├── extract_characters.md
│   ├── extract_bible.md
│   ├── find_patterns.md
│   ├── bridge_inspiration.md
│   ├── pace_reference.md
│   ├── compose_framework.md
│   └── evaluate_framework.md
│
├── config.yaml                 # 全局配置
├── server.py                   # FastAPI 服务端点
├── setup_db.py                 # SQLite 初始化脚本
└── requirements.txt           # 依赖清单
