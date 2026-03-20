#!/usr/bin/env python3
"""
RAG-powered chat with local knowledge base (FAISS).

Usage:
    .venv/Scripts/python.exe scripts/ask.py "your question"
    .venv/Scripts/python.exe scripts/ask.py          (interactive)
    .venv/Scripts/python.exe scripts/ask.py --clear  (clear history)

Requires:
    - llama-server chat (config.yaml → rag.chat_port)
    - llama-server embedding (rag.embed_port) when an index exists
    - Index: scripts/build_embeddings.py

    start_server.bat rag
"""

import json
import sys
from pathlib import Path

import faiss
import httpx
import numpy as np

from load_config import CONFIG_PATH, indexing_dirs, load_config, rag_urls, health_base

PROJECT_ROOT = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_ROOT / "history.json"


def _system_prompt(cfg: dict) -> str:
    p = cfg.get("system_prompt")
    if isinstance(p, str) and p.strip():
        return p.strip()
    return (
        "You are an autonomous AI assistant focused on survival. Answer briefly and to the point.\n"
        "If unsure, say so.\n"
        "Write your responses in the same language as the user."
    )


def load_index(index_dir: Path):
    index_file = index_dir / "faiss.index"
    chunks_file = index_dir / "chunks.json"
    if not index_file.exists() or not chunks_file.exists():
        return None, None
    index = faiss.read_index(str(index_file))
    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))
    return index, chunks


def load_history() -> list:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history: list, max_pairs: int):
    if len(history) > max_pairs * 2:
        history = history[-(max_pairs * 2) :]
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_embedding(text: str, client: httpx.Client, embed_url: str) -> np.ndarray:
    resp = client.post(embed_url, json={"model": "embedding", "input": text}, timeout=60.0)
    resp.raise_for_status()
    vec = resp.json()["data"][0]["embedding"]
    return np.array([vec], dtype=np.float32)


def search_chunks(
    query: str,
    index,
    chunks: dict,
    client: httpx.Client,
    embed_url: str,
    top_k: int,
    max_chunk_chars: int,
) -> list[str]:
    vec = get_embedding(query, client, embed_url)
    faiss.normalize_L2(vec)
    distances, ids = index.search(vec, top_k)
    results = []
    for idx in ids[0]:
        if idx == -1:
            continue
        chunk = chunks[str(idx)]
        text = chunk["text"][:max_chunk_chars]
        source = chunk["source"]
        results.append(f"[{source}]\n{text}")
    return results


def build_messages(
    question: str,
    rag_chunks: list[str],
    history: list,
    system_prompt: str,
):
    system_parts = [system_prompt]
    if rag_chunks:
        system_parts.append(
            "KNOWLEDGE BASE (use when answering):\n\n" + "\n\n---\n\n".join(rag_chunks)
        )
    messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    return messages


def chat(
    messages: list[dict],
    client: httpx.Client,
    chat_url: str,
    max_tokens: int,
    temperature: float,
) -> str:
    response = client.post(
        chat_url,
        json={
            "model": "local",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        },
        timeout=120.0,
    )
    response.raise_for_status()

    full_response = []
    print("\nAssistant: ", end="", flush=True)
    for line in response.iter_lines():
        if not line or line == "data: [DONE]":
            continue
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                delta = data["choices"][0]["delta"].get("content", "")
                if delta:
                    print(delta, end="", flush=True)
                    full_response.append(delta)
            except (json.JSONDecodeError, KeyError):
                continue
    print()
    return "".join(full_response)


def check_http_health(base: str) -> bool:
    try:
        return httpx.get(f"{base}/health", timeout=2.0).status_code == 200
    except Exception:
        return False


def main():
    cfg = load_config()
    rag = cfg["rag"]
    chat_api = cfg["chat_api"]
    chat_url, embed_url = rag_urls(cfg)
    chat_base = health_base(cfg, rag["chat_port"])
    embed_base = health_base(cfg, rag["embed_port"])
    _texts_dir, index_dir = indexing_dirs(cfg)

    top_k = rag["top_k"]
    max_pairs = rag["max_history_pairs"]
    max_chunk_chars = rag["max_chunk_chars"]
    system_prompt = _system_prompt(cfg)

    args = sys.argv[1:]

    if args and args[0] == "--clear":
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
            print("[OK] History cleared.")
        else:
            print("[i] Already empty.")
        return

    if not check_http_health(chat_base):
        print(f"[X] Chat server not running (port {rag['chat_port']})")
        print('    start_server.bat rag')
        sys.exit(1)

    index, chunks = load_index(index_dir)
    has_rag = index is not None

    if has_rag and not check_http_health(embed_base):
        print(
            f"[!] Embedding server unreachable (port {rag['embed_port']}) — RAG disabled, chat only.\n"
        )
        has_rag = False

    if not has_rag:
        if index is None:
            print(f"[i] No index — running without RAG. Build: .venv\\Scripts\\python.exe scripts\\build_embeddings.py")
            if not CONFIG_PATH.exists():
                print(f"[i] Missing {CONFIG_PATH.name} — using built-in defaults.")
        print()
    else:
        print(f"[+] RAG on (FAISS, {len(chunks)} chunks)\n")

    history = load_history()

    if args:
        question = " ".join(args)
        interactive = False
    else:
        print("=" * 50)
        print(" AI Survival — RAG Chat")
        print(" /exit — quit  |  /clear — clear history")
        print("=" * 50 + "\n")
        interactive = True

    with httpx.Client() as client:
        while True:
            if interactive:
                try:
                    question = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[bye]")
                    break
                if not question:
                    continue
                if question == "/exit":
                    print("[bye]")
                    break
                if question == "/clear":
                    history = []
                    if HISTORY_FILE.exists():
                        HISTORY_FILE.unlink()
                    print("[OK] History cleared.\n")
                    continue

            rag_chunks = []
            if has_rag:
                try:
                    rag_chunks = search_chunks(
                        question,
                        index,
                        chunks,
                        client,
                        embed_url,
                        top_k,
                        max_chunk_chars,
                    )
                except Exception as e:
                    print(f"[!] RAG error: {e}")

            messages = build_messages(question, rag_chunks, history, system_prompt)
            try:
                answer = chat(
                    messages,
                    client,
                    chat_url,
                    chat_api["max_tokens"],
                    chat_api["temperature"],
                )
            except Exception as e:
                print(f"\n[X] Chat error: {e}")
                if not interactive:
                    sys.exit(1)
                continue

            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
            save_history(history, max_pairs)

            if not interactive:
                break


if __name__ == "__main__":
    main()
