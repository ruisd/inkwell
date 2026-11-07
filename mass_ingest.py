#!/usr/bin/env python3
"""Batch ingest standalone EPUB novels from Downloads into StoryForge."""
import sys, os, time, json, subprocess
from pathlib import Path

# Use DSH bundled Python — already has lxml (+ bs4, ebooklib installed above)
DSH_PY = "/Users/ruisongde/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3"
VENV_PY = "/Users/ruisongde/.rag-mcp/venv/bin/python3"
# Install site-packages path for ebooklib/bs4
EBOOK_DIR = "/tmp/ebook-py"

# --- EPUB list (skip collections & non-fiction) ---
TARGETS = [
    # 两京十五日 already ingested (id 2,3,4) — skip
    Path.home() / "Downloads/孤城闭(畅销十载,赞誉有加,口碑经典。米兰Lady古典爱情文艺巨作,从写史的角度描摹爱,以文艺的笔法追溯史。) (米兰Lady [米兰Lady]) (z-library.sk, 1lib.sk, z-lib.sk).epub",
]

# --- Extract metadata using standalone script ---
def extract_meta(epub_path: Path):
    """Returns (title, author) using ebooklib."""
    code = f'''
import sys; sys.path.insert(0, "{EBOOK_DIR}")
import ebooklib, json
from ebooklib import epub
book = epub.read_epub(r"{epub_path}")
title = book.get_metadata("DC", "title")
creator = book.get_metadata("DC", "creator")
t = str(title[0][0]) if title else "Unknown"
c = str(creator[0][0]) if creator else "Unknown"
print(json.dumps({{"title": t, "author": c}}))
'''
    r = subprocess.run([DSH_PY, "-c", code], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  [WARN] meta extraction failed: {r.stderr[:120]}")
        return "Unknown", "Unknown"
    try:
        d = json.loads(r.stdout.strip())
        return d["title"], d["author"]
    except:
        return "Unknown", "Unknown"

# --- Main ---
print(f"\n{'='*60}")
print(f"STORYFORGE MASS INGEST — {len(TARGETS)} standalone novels")
print(f"{'='*60}\n")

results = []
for i, ep in enumerate(TARGETS, 1):
    if not ep.exists():
        print(f"[{i}/{len(TARGETS)}] MISSING: {ep.name}")
        continue
    print(f"\n[{i}/{len(TARGETS)}] Parsing: {ep.name}")
    # Extract metadata
    title, author = extract_meta(ep)
    print(f"  Title: {title}")
    print(f"  Author: {author}")

    # Extract plain text
    t0 = time.time()
    code = f'''
import sys; sys.path.insert(0, "{EBOOK_DIR}")
import ebooklib, re, json
from ebooklib import epub
from bs4 import BeautifulSoup
book = epub.read_epub(r"{ep}")
chapters = []
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    soup = BeautifulSoup(item.get_body_content(), "html.parser")
    txt = soup.get_text(separator="\\n").strip()
    txt = re.sub(r"\\n{3,}", "\\n\\n", txt)
    if len(txt) > 200:
        chapters.append(txt)
full = "\\n\\n".join(chapters)
print(json.dumps({{"char_count": len(full)}}))
with open("/tmp/_sf_temp.txt", "w", encoding="utf-8") as f:
    f.write(full)
'''
    r = subprocess.run([DSH_PY, "-c", code], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  [ERROR] extraction failed: {r.stderr[:200]}")
        continue
    info = json.loads(r.stdout.strip())
    elapsed = time.time() - t0
    print(f"  Extracted: {info['char_count']} chars in {elapsed:.1f}s")

    # Ingest via inkwell ingest module
    t0 = time.time()
    # Create a temporary .txt reference so ingest picks it up
    tmp_path = Path("/tmp/_sf_temp.txt")
    r2 = subprocess.run(
        [VENV_PY, "-c",
         f'''
import sys; sys.path.insert(0, ".")
from inkwell.library import ingest

result = ingest.ingest_book(
    r"{tmp_path}",
    title="{title}",
    author="{author}",
    source_format="epub",
    original_path=r"{ep}",
)
print("OK:" + str(result))
'''],
        cwd="/Users/ruisongde/Documents/deepseek-harness/default-workspace",
        capture_output=True, text=True, timeout=600
    )
    elapsed = time.time() - t0
    if r2.returncode != 0:
        print(f"  [ERROR] ingest failed ({elapsed:.1f}s): {r2.stderr[:200]}")
        results.append({"title": title, "author": author, "status": "FAILED", "error": r2.stderr[:200]})
        continue
    print(f"  Ingested: {r2.stdout.strip()} in {elapsed:.1f}s")
    results.append({"title": title, "author": author, "status": "OK", "output": r2.stdout.strip()})

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}\n")
ok = [r for r in results if r["status"] == "OK"]
fail = [r for r in results if r["status"] != "OK"]
print(f"  ✓ Success: {len(ok)}")
print(f"  ✗ Failed:  {len(fail)}")
if fail:
    for f_ in fail:
        print(f"    - {f_['title']}: {f_.get('error', '?')}")