"""
StoryForge — SQLite 数据库初始化脚本

综合笔灵 (BiLing) 和大作家 (GreatWriter) 的 Schema 设计精华，
支持跨书籍图书馆、人物原型库、联想网络、自主学习回路。

表结构:
  1. book_profile      — 书籍全息档案
  2. character_archetype — 人物原型库
  3. chapter_structure — 章节结构解剖
  4. world_elements    — 世界观元素
  5. influence_graph   — 影响关系图谱
  6. bibles            — 创作圣经表
  7. frameworks_collected — 自主学习收藏
  8. framework_evolutions  — 进化记录
"""

import sqlite3
import sys
import os
from pathlib import Path

DIR = Path(__file__).parent
DB_PATH = os.environ.get("INKWELL_DB", str(DIR / "data" / "inkwell.db"))
DATA_DIR = Path(DB_PATH).parent
FRAMEWORKS_DB = str(DATA_DIR / "frameworks.db")


def create_database(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # 1 - book_profile — 书籍全息档案
    cur.execute("""
        CREATE TABLE IF NOT EXISTS book_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            author_era TEXT,
            genre TEXT,
            sub_genre TEXT,
            plot_structure TEXT,
            narrative_pov TEXT,
            writing_style TEXT,
            word_count INTEGER,
            premise TEXT,
            worldbuilding_desc TEXT,
            ending_plan TEXT,
            core_foreshadowing TEXT,
            main_character_arc TEXT,
            conflict_patterns TEXT,
            emotional_curve TEXT,
            pacing_profile TEXT,
            feature_card_json TEXT,
            quality_score REAL DEFAULT 0,
            source_path TEXT,
            source_format TEXT,
            indexed_at TEXT,
            updated_at TEXT
        )
    """)

    # 2 - character_archetype (借鉴笔灵 chars + 大作家 goal)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS character_archetype (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE,
            archetype_name TEXT NOT NULL,
            source_book TEXT,
            source_character TEXT,
            role_type TEXT,
            personality TEXT,
            motivation TEXT,
            goal TEXT,
            arc TEXT,
            abilities TEXT,
            relationships TEXT,
            notes TEXT,
            variation_tags TEXT,
            embedding_vector BLOB,
            created_at TEXT
        )
    """)

    # 3 - chapter_structure (借鉴笔灵 blueprints)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chapter_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE,
            chapter_number REAL NOT NULL,
            chapter_title TEXT,
            chapter_role TEXT,
            key_events TEXT,
            suspense_type TEXT,
            emotional_peak TEXT,
            pace_density INTEGER,
            ending_hook TEXT,
            key_conflict TEXT,
            characters_involved TEXT,
            word_count INTEGER
        )
    """)

    # 4 - world_elements (借鉴大作家 novel_settings)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS world_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE,
            element_type TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT,
            sort_order INTEGER DEFAULT 0 CHECK(sort_order >= 0)
        )
    """)

    # 5 - influence_graph (书籍间 influence/intertext/inheritance)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS influence_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE,
            target_book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE,
            relation_type TEXT CHECK(relation_type IN ('influence', 'intertext', 'inheritance')),
            evidence TEXT,
            confidence_score REAL DEFAULT 0.0,
            created_at TEXT
        )
    """)

    # 6 - bibles (借鉴大作家 novel_bibles)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bibles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES book_profile(id) ON DELETE CASCADE UNIQUE,
            story_mainline TEXT,
            ending_plan TEXT,
            character_arcs TEXT,
            core_foreshadowing TEXT,
            world_building TEXT,
            extra_notes TEXT,
            raw_payload TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # 7 - frameworks_collected — 自主学习收藏
    cur.execute("""
        CREATE TABLE IF NOT EXISTS frameworks_collected (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            framework_json TEXT NOT NULL,
            source_query TEXT,
            source_book_ids TEXT,
            quality_score REAL DEFAULT 0,
            tags TEXT,
            evolution_mark TEXT,
            created_at TEXT
        )
    """)

    # 8 - framework_evolutions — 进化记录
    cur.execute("""
        CREATE TABLE IF NOT EXISTS framework_evolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evolution_type TEXT,
            description TEXT,
            patterns_found TEXT,
            frameworks_added INTEGER DEFAULT 0,
            frameworks_removed INTEGER DEFAULT 0,
            timestamp TEXT
        )
    """)

    # indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_book_author ON book_profile(author)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_book_genre ON book_profile(genre)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_book_score ON book_profile(quality_score)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_char_archetype ON character_archetype(archetype_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_char_book ON character_archetype(book_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chapter_book ON chapter_structure(book_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_src ON influence_graph(source_book_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_trg ON influence_graph(target_book_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_world_book ON world_elements(book_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bible_book ON bibles(book_id)")

    conn.commit()
    conn.close()
    print(f"StoryForge DB created: {db_path}")
    return db_path


def create_frameworks_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS frameworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            framework_json TEXT NOT NULL,
            source_query TEXT,
            source_book_ids TEXT,
            quality_score REAL DEFAULT 0,
            tags TEXT,
            evolution_mark TEXT,
            created_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fw_score ON frameworks(quality_score)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fw_tags ON frameworks(tags)")
    conn.commit()
    conn.close()
    print(f"Frameworks DB created: {db_path}")
    return db_path


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    create_database(DB_PATH)
    create_frameworks_db(FRAMEWORKS_DB)
    print("StoryForge initialization complete.")