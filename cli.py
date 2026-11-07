#!/usr/bin/env python3
"""
StoryForge CLI — Interactive mode.
Usage: inkwell              (interactive shell)
       inkwell ingest PATH  (batch ingest one book)
       inkwell query PROMPT (generate a framework)
       inkwell report       (association network report)
"""

import cmd
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def _print_box(title: str, lines: list[str]):
    w = 60
    print(f"\n{'─'*w}")
    print(f"  {title}")
    print(f"{'─'*w}")
    for ln in lines:
        print(f"  {ln}")
    print(f"{'─'*w}\n")


# ═══════════════════════════════════════════════════════
# Interactive shell
# ═══════════════════════════════════════════════════════

class StoryForgeShell(cmd.Cmd):
    intro = (
        "\n╔══════════════════════════════════════════════════╗\n"
        "║          StoryForge  ──  故事锻造台             ║\n"
        "║  本地图书馆 · 联想网络 · 灵感引擎 · 框架生成   ║\n"
        "╚══════════════════════════════════════════════════╝\n"
        "'library' | 'ingest' | 'extract' | 'search' | 'query' | 'report' | 'quit'"
    )
    prompt = "\n📖 inkwell> "

    def do_library(self, arg):
        "library [genre|author] — browse indexed books"
        from inkwell.library import catalog
        genre = arg.strip() if arg.strip() else ""
        books = catalog.list_books(genre=genre)
        if not books:
            print("[library] No books indexed. Use 'ingest' first.")
            return
        _print_box(f"Library — {len(books)} books", [
            f"#{b['id']:>3}  {b['title'][:30]:<30}  {b['author'][:14]:<14}  {b['genre'][:12]}" for b in books
        ])

    def do_ingest(self, arg):
        "ingest PATH — import a book file into library"
        path = Path(arg.strip())
        if not path.exists():
            print(f"[ingest] File not found: {path}")
            return
        from inkwell.library import librarian
        try:
            book_id = librarian.ingest_book(str(path))
            print(f"[ingest] ✓ Book #{book_id} indexed.")
        except Exception as e:
            print(f"[ingest] ✗ {e}")

    def do_extract(self, arg):
        "extract ALL — run feature extraction on all un-analysed books"
        if arg.strip().upper() != "ALL":
            print("Use: extract ALL")
            return
        from inkwell.profiles import extractor
        results = extractor.batch_extract_all()
        print(f"[extract] ✓ {len(results)} books analysed.")

    def do_search(self, arg):
        "search TERM — hybrid search across chunks"
        q = arg.strip()
        if not q:
            print("[search] Usage: search <query>")
            return
        from inkwell.network import multi_recall
        hits = multi_recall.hybrid_recall(q)
        if not hits:
            print("[search] No results.")
            return
        _print_box(f"Search: \"{q}\" — {len(hits)} hits", [
            f"{h.get('title','?')[:40]:<40} [{h.get('recall_type','?')}] score={h.get('score',0)}" for h in hits
        ])

    def do_query(self, arg):
        "query PROMPT — generate a complete story framework"
        q = arg.strip()
        if not q:
            print("[query] Usage: query <story prompt>")
            return
        from inkwell.forge import composer
        from inkwell.forge import learner
        result = composer.compose_framework(q)
        print(f"\n{'═'*60}")
        print(result)
        print(f"{'═'*60}\n")
        score = learner.quality_score(result)
        if learner.should_collect(result):
            learner.collect_framework(result, q)
            print(f"[learner] ✓ Framework auto-collected (score={score:.2f})")
        else:
            print(f"[learner] Quality score {score:.2f} < threshold — not collected.")

    def do_report(self, arg):
        "report — association network overview"
        from inkwell.network import associations
        rep = associations.full_association_report()
        _print_box("Association Report", [
            f"Books: {rep['book_count']}",
            f"Semantic pairs (>0.75): {len(rep['semantic_pairs_above_075'])}",
            f"Cross-index keys: {rep['cross_index_keys'][:10]}{'...' if len(rep['cross_index_keys'])>10 else ''}",
        ])
        from inkwell.forge import learner
        ev = learner.evolution_report()
        _print_box("Evolution", [
            f"Frameworks: {ev['count']}  Avg score: {ev['avg_score']}  Trend: {ev['trend']}",
        ])

    def do_quit(self, arg):
        return True

    do_q = do_quit
    do_exit = do_quit


# ═══════════════════════════════════════════════════════
# CLI dispatcher
# ═══════════════════════════════════════════════════════

def main():
    if len(sys.argv) == 1:
        StoryForgeShell().cmdloop()
        return

    cmd = sys.argv[1]
    if cmd == "ingest":
        path = Path(sys.argv[2])
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)
        from inkwell.library import librarian
        try:
            bid = librarian.ingest_book(str(path))
            print(json.dumps({"status": "ok", "book_id": bid}))
        except Exception as e:
            print(json.dumps({"status": "error", "detail": str(e)}))
            sys.exit(1)

    elif cmd == "query":
        q = " ".join(sys.argv[2:])
        from inkwell.forge import composer
        from inkwell.forge import learner
        result = composer.compose_framework(q)
        print(result)
        if learner.should_collect(result):
            learner.collect_framework(result, q)

    else:
        StoryForgeShell().cmdloop()


if __name__ == "__main__":
    main()