"""Load config.yaml merged with built-in defaults."""
from copy import deepcopy
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

_DEFAULTS = {
    "rag": {
        "host": "localhost",
        "chat_port": 8080,
        "embed_port": 8081,
        "top_k": 5,
        "max_history_pairs": 20,
        # history.json: user/assistant only; RAG is not stored, re-injected each question.
        "max_chunk_chars": 15000,
    },
    "indexing": {
        "chunk_chars": 1500,
        "overlap_chars": 300,
    },
    "chat_api": {
        "max_tokens": 1024,
        "temperature": 0.7,
    },
}


def _deep_merge_dict(a: dict, b: dict) -> dict:
    r = deepcopy(a)
    for k, v in (b or {}).items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = _deep_merge_dict(r[k], v)
        else:
            r[k] = v
    return r


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
    else:
        user = {}
    return _deep_merge_dict(_DEFAULTS, user)


def rag_urls(cfg: dict) -> tuple[str, str]:
    h = cfg["rag"]["host"]
    cp = cfg["rag"]["chat_port"]
    ep = cfg["rag"]["embed_port"]
    return f"http://{h}:{cp}/v1/chat/completions", f"http://{h}:{ep}/v1/embeddings"


def health_base(cfg: dict, port: int) -> str:
    h = cfg["rag"]["host"]
    return f"http://{h}:{port}"


def indexing_dirs(cfg: dict) -> tuple[Path, Path]:
    kb = cfg.get("paths", {}).get("knowledge_base", "knowledge_base")
    if kb.startswith("./"):
        kb = kb[2:]
    base = PROJECT_ROOT / kb
    return base / "texts", base / "index"
