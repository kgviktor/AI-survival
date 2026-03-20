#!/usr/bin/env python3
"""
Vectorize the knowledge base: texts/*.txt -> chunks -> FAISS.

Processes all files in texts/, one chunk at a time in memory.
Chunk params and port: config.yaml (indexing, rag.embed_port).

Requires: llama-server with embedding, faiss-cpu.

    start_server.bat rag  (or embedding-only on :8081)
"""

import json
import struct
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

try:
    import faiss
except ImportError:
    print("[X] pip install faiss-cpu")
    exit(1)

from load_config import indexing_dirs, load_config, rag_urls


def iter_chunks(text: str, source: str, chunk_chars: int, overlap_chars: int):
    """Yield one chunk at a time without holding all chunks in memory."""
    text = text.strip()
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        if end < len(text):
            for sep in ("\n\n", "\n", ". ", "! ", "? "):
                pos = text.rfind(sep, start + chunk_chars // 2, end)
                if pos != -1:
                    end = pos + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            yield {"text": chunk, "source": source}
        if end >= len(text):
            break
        start = end - overlap_chars


def embed(text: str, embed_url: str) -> list[float]:
    body = json.dumps({"model": "embedding", "input": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        embed_url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())["data"][0]["embedding"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        print(f"\n[X] HTTP {e.code}: {err_body[:500]}")
        raise


def main():
    cfg = load_config()
    TEXTS_DIR, INDEX_DIR = indexing_dirs(cfg)
    _, EMBED_URL = rag_urls(cfg)
    idx_cfg = cfg["indexing"]
    chunk_chars = idx_cfg["chunk_chars"]
    overlap_chars = idx_cfg["overlap_chars"]

    VECS_FILE = INDEX_DIR / "_vectors.bin"
    CHUNKS_JSONL = INDEX_DIR / "_chunks.jsonl"
    CHUNKS_FILE = INDEX_DIR / "chunks.json"
    INDEX_FILE = INDEX_DIR / "faiss.index"

    print("\n[*] Vectorizing: texts/ -> chunks -> FAISS\n")

    files = sorted(TEXTS_DIR.glob("*.txt"))
    if not files:
        print(f"[X] No .txt files in {TEXTS_DIR}")
        return 1

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if VECS_FILE.exists():
        VECS_FILE.unlink()
    if CHUNKS_JSONL.exists():
        CHUNKS_JSONL.unlink()

    total = 0
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as jf:
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            chunk_num = 0
            for c in iter_chunks(text, f.name, chunk_chars, overlap_chars):
                vec = embed(c["text"], EMBED_URL)
                mode = "ab" if VECS_FILE.exists() else "wb"
                with open(VECS_FILE, mode) as vf:
                    vf.write(struct.pack(f"{len(vec)}f", *vec))
                jf.write(json.dumps(c, ensure_ascii=False) + "\n")
                chunk_num += 1
                total += 1
                print(f"   {f.name}: chunk {chunk_num}")
            del text

    # Build FAISS from binary vectors
    print("Building FAISS index...")
    raw = np.fromfile(str(VECS_FILE), dtype=np.float32)
    dim = len(raw) // total
    matrix = raw.reshape(total, dim)
    faiss.normalize_L2(matrix)
    index = faiss.IndexFlatIP(dim)
    index.add(matrix)
    faiss.write_index(index, str(INDEX_FILE))

    # chunks.json from jsonl
    print("Writing chunks.json...")
    chunks_dict = {}
    with open(CHUNKS_JSONL, encoding="utf-8") as f:
        for i, line in enumerate(f):
            chunks_dict[str(i)] = json.loads(line)
    CHUNKS_FILE.write_text(json.dumps(chunks_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    CHUNKS_JSONL.unlink(missing_ok=True)

    VECS_FILE.unlink(missing_ok=True)
    print(f"\n[OK] {INDEX_FILE}, {CHUNKS_FILE} ({total} chunks)\n")
    return 0


if __name__ == "__main__":
    exit(main())
