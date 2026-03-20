# AI Survival — Local offline survival assistant

## What this project is

**AI Survival** is a **fully local** setup: you run open-weight models on your own PC (via **llama.cpp** / `llama-server`) and use them **without the internet** once binaries and model files are installed. **Nothing is sent to external APIs** — prompts and (with RAG) your knowledge texts stay on your machine.

There are **three separate ways to use the repo** (pick one for a session; they do not all run at once):

1. **Simple terminal chat** — `run.bat` starts **one** `llama-server` with the chat model you choose. Plain Q&A in the console; **no** knowledge base, **no** Python. Good for quick survival-oriented talk (preparedness, outdoors, first aid, gear, etc.).

2. **Terminal chat + RAG** — You run **two** `llama-server` processes: a **small embedding model** (port 8081) builds/searches vectors, and your **chat model** (8080) answers. `build_embeddings.py` + `ask.py` (Python) chunk the texts under `knowledge_base/texts/`, build a **FAISS** index, retrieve relevant passages, and **inject them into the prompt** so replies can lean on **your handbook**, not only the model weights. Edit `.txt` → rebuild the index → the “bookshelf” updates.

3. **VS Code (Continue)** — You point the **Continue** extension at a **single** `llama-server` with a model you pick (often a **code** model). That is **IDE assistance**, not the RAG `ask.py` pipeline. Setup: `vs_extension/SETUP.md`.

**RAG is not “smarter one brain”** — it is **chat model + retrieval**: the embed server only turns text into vectors; the chat model still does all the wording.

**Quick commands:** → `CHEATSHEET.txt`.

---

## Important

AI answers **do not replace** a doctor, instructor, or emergency services. In danger, get professional help.

---

## Three modes (summary)

| # | Mode | What to run | Python |
|---|------|-------------|--------|
| 1 | Simple chat | `run.bat qwen3.5-4b` (one server) | No |
| 2 | Chat + RAG | `start_server.bat rag` → `build_embeddings.py` → `ask.py` (two servers) | Yes |
| 3 | VS Code | `start_server.bat …` + Continue per `vs_extension/SETUP.md` (one server for IDE) | — |

**RAG step-by-step:** see `CHEATSHEET.txt` (servers, index, questions, updating the base).

Run commands from the **repository root** (folder with `run.bat` and `start_server.bat`).

Example:
```bat
start_server.bat rag
.venv\Scripts\python.exe scripts\build_embeddings.py
.venv\Scripts\python.exe scripts\ask.py
```

---

## Layout

```
AI_survival/
├── bin/                 # llama-server, llama-cli
├── models/              # GGUF
├── knowledge_base/texts # .txt sources for RAG (bundled survival handbook, etc.)
├── knowledge_base/index # FAISS (local, not in git — see .gitignore)
├── scripts/             # build_embeddings.py, ask.py, download_models.py
├── config.yaml          # RAG ports, chunks, system prompt
├── CHEATSHEET.txt       # command cheat sheet
├── run.bat              # simple chat
└── start_server.bat     # servers for RAG / VS Code
```

---

## Models (overview)

| Name for run.bat | Role |
|------------------|------|
| qwen3.5-4b, qwen3.5-9b, qwen3-8b, … | Simple chat |
| start_server.bat rag [qwen35-9b] | RAG: chat + embedding |

Full list: `run.bat` with no args, or `scripts/download_models.py --list`.

Default embed model: `Qwen3-Embedding-0.6B` (1024 dims).

**Thinking (Qwen3):** append `/no_think` to a prompt to disable.

---

## Requirements

- ~16 GB RAM for RAG (chat + embed + OS)
- Python 3.12 + `.venv` + `requirements.txt`

## Git and paths

The repo has **no hardcoded paths to your disk**: scripts resolve from the **project root** (`Path(__file__).parent.parent` in Python; for `.bat`, run from the folder that contains `run.bat`).

After `git clone` on another PC: add `bin/`, `models/*.gguf`, create a venv (`python -m venv .venv`, `pip install -r requirements.txt`), build the index with `build_embeddings.py`. `.venv` is not in git — absolute paths inside it stay **local**, which is expected.

## License

MIT
