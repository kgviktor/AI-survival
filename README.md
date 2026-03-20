# AI Survival — Local offline survival assistant

## What this project is

**AI Survival** is a **fully local** setup: you run open-weight models on your own PC (via llama.cpp) and talk to them **without the internet** after models and binaries are in place. Nothing is sent to external APIs—your prompts and (if you use RAG) your knowledge files stay on your machine.

**What you get in practice:**

1. **Survival-oriented Q&A** — The stack is tuned for preparedness, outdoors, medical first-aid context, logistics, gear, and similar topics. You can chat in the terminal (`run.bat`) or wire the same server into **VS Code** with the Continue extension for coding help on the same models.

2. **Optional RAG over your knowledge base** — Under `knowledge_base/texts/` you keep plain `.txt` articles (the bundled corpus is a large survival handbook split into files). A script builds a **FAISS** index from embeddings; `ask.py` then retrieves relevant chunks and injects them into the prompt so answers can **cite your own material**, not just the model’s weights. Add or edit `.txt` files, rebuild the index, and the assistant’s “bookshelf” updates.

3. **One repo, two “brains”** — *Chat* uses the LLM alone. *RAG mode* runs a **second** small model for embeddings plus the chat model, so answers can combine general reasoning with passages from your indexed texts.

**Quick orientation:** detailed commands → `CHEATSHEET.txt`.

---

## Important

AI answers **do not replace** a doctor, instructor, or emergency services. In danger, get professional help.

---

## Three modes

| Mode | What to run | Python |
|------|-------------|--------|
| Simple chat | `run.bat qwen3.5-4b` | No |
| RAG (knowledge base) | `start_server.bat rag` → `build_embeddings.py` → `ask.py` | Yes |
| Code in VS Code | `vs_extension/SETUP.md` | — |

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
├── knowledge_base/texts # .txt sources for RAG (article bodies may be non-English)
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
