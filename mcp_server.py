#!/usr/bin/env python3
"""
MCP Streamable-HTTP server for Inkwell.
Expose all five layers as MCP tools so any agent can:
  - search the library via hybrid recall
  - ingest new books
  - extract feature cards
  - generate story frameworks
  - inspect the association graph
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent   # inkwell/
sys.path.insert(0, str(BASE_DIR))

# ---------- lazy load heavy deps ----------
_MODEL = None

def _get_embedder():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        try:
            import torch
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        except Exception:
            device = "cpu"
        _MODEL = SentenceTransformer("BAAI/bge-m3", device=device)
    return _MODEL

# ---------- tool implementations ----------

def sf_search(query: str, top_k: int = 8) -> dict:
    """Hybrid (vector + metadata) search across the indexed library."""
    from network.multi_recall import hybrid_recall
    docs = hybrid_recall(query, top_k=top_k)
    return {"query": query, "results": docs}

def sf_ingest(file_path: str) -> dict:
    """Ingest a .txt/.md/.epub book into the SQLite catalog."""
    from library.ingest import ingest_book
    bid = ingest_book(file_path)
    return {"book_id": bid, "path": file_path}

def sf_extract(book_id: int = None) -> dict:
    """Extract a 12-dimension feature card for one or all un-analysed books."""
    from profiles.extractor import batch_extract_all, generate_structured_profile
    from library.catalog import get_book
    if book_id is not None:
        b = get_book(book_id)
        if not b:
            return {"error": f"book {book_id} not found"}
        p = Path(b.get("source_path", ""))
        if not p.exists():
            return {"error": f"source file missing: {p}"}
        text = p.read_text(encoding="utf-8")
        prof = generate_structured_profile(book_id, text, b.get("title", ""))
        return {"profile": prof}
    results = batch_extract_all()
    return {"processed": len(results), "profiles": results}

def sf_list_books() -> dict:
    """Return all books in the library."""
    from library.catalog import list_books
    return {"books": list_books()}

def sf_compose(query: str) -> dict:
    """Generate a full story framework (JSON). Requires DEEPSEEK_API_KEY."""
    from forge.composer import compose_framework
    raw = compose_framework(query)
    return {"framework": raw}

def sf_report() -> dict:
    """Association graph overview + evolution stats."""
    from network.associations import full_association_report
    from forge.learner import evolution_report
    assoc = full_association_report()
    evo = evolution_report()
    return {"association": assoc, "evolution": evo}

# ---------- MCP handler registration ----------

async def handle_list_tools(ctx, params):
    tools = [
        {
            "name": "sf_search",
            "description": "Search the Inkwell library using hybrid (vector + keyword) recall. Returns top-k ranked snippets with metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "default": 8},
                },
                "required": ["query"],
            },
        },
        {
            "name": "sf_ingest",
            "description": "Import a book file (.txt/.md/.epub) into Inkwell.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute or relative path to the file"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "sf_list_books",
            "description": "List all books currently in the Inkwell library.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "sf_extract",
            "description": "Extract 12-dim literary feature cards. Pass no args = batch all missing; pass book_id for one.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "book_id": {"type": "integer"},
                },
            },
        },
        {
            "name": "sf_compose",
            "description": "Generate a complete story framework (JSON) from a free-text query. Requires DEEPSEEK_API_KEY.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "e.g. 'a detective story set in Edo-period Japan'"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "sf_report",
            "description": "Get association graph summary + evolution stats.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]

    from mcp_types import ListToolsResult
    return ListToolsResult(tools=tools)


async def handle_call_tool(ctx, params):
    name = params.name
    args = params.arguments or {}

    try:
        if name == "sf_search":
            result = sf_search(args.get("query", ""), int(args.get("top_k", 8)))
        elif name == "sf_ingest":
            result = sf_ingest(args["file_path"])
        elif name == "sf_list_books":
            result = sf_list_books()
        elif name == "sf_extract":
            result = sf_extract(args.get("book_id"))
        elif name == "sf_compose":
            result = sf_compose(args["query"])
        elif name == "sf_report":
            result = sf_report()
        else:
            result = {"error": f"unknown tool: {name}"}

        from mcp_types import CallToolResult, TextContent
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        )
    except Exception as exc:
        from mcp_types import CallToolResult, TextContent
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps({"error": str(exc)}))]
        )

# ---------- Starlette / Streamable-HTTP ----------

import contextlib
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette as StarletteApp


def build_app():
    server = Server(
        "inkwell",
        description="Local AI writing library: ingest books, extract features, compose story frameworks.",
        version="1.0.0",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )

    session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=True,
        stateless=True,
    )

    @contextlib.asynccontextmanager
    async def lifespan(app):
        async with session_manager.run():
            yield

    starlette_app = StarletteApp(lifespan=lifespan)
    starlette_app.mount("/", app=session_manager.asgi_app)
    return starlette_app


app = build_app()

# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inkwell MCP Server")
    parser.add_argument("--port", type=int, default=9030)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    ns = parser.parse_args()

    import uvicorn
    print(f"  Inkwell MCP → http://{ns.host}:{ns.port}/mcp")
    uvicorn.run(app, host=ns.host, port=ns.port, log_level="info")