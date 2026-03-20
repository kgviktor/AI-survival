# Continue + Local LLM — VS Code setup

Use local models from the `models/` folder inside VS Code, fully offline.

---

## Requirements

- VS Code
- **Continue** extension (`Continue.continue` in the marketplace)
- `start_server.bat` running (from the project root)

---

## One-time setup

### 1. Install Continue

In VS Code: Extensions → search `Continue.continue` → Install

### 2. Copy config

Copy `vs_extension/continue_config.yaml` to:

`C:\Users\<your user>\.continue\config.yaml`

Or edit your existing config — add the `models:` block from `continue_config.yaml`.

---

## Run

### 1. Start the server with the model you want

Open a terminal at the project root (`AI_survival/`) and run:

```
start_server.bat coder-7b
```

Available models:

| Command        | Model                | Size    | Speed       |
|----------------|----------------------|---------|-------------|
| `coder-7b`     | Qwen2.5-Coder 7B     | 4.4 GB  | ~6 tok/s    |
| `coder-14b`    | Qwen2.5-Coder 14B    | 8.9 GB  | ~2.5 tok/s  |
| `qwen3-4b`     | Qwen3 4B             | 2.3 GB  | ~10 tok/s   |
| `qwen3-8b`     | Qwen3 8B             | 4.7 GB  | ~6 tok/s    |
| `qwen35-4b`    | Qwen3.5 4B           | 2.6 GB  | ~10 tok/s   |
| `qwen35-9b`    | Qwen3.5 9B           | 5.3 GB  | ~5 tok/s    |

Wait until the terminal shows something like:
```
main: server is listening on http://127.0.0.1:8080
```

### 2. Open the project in VS Code

**File → Open Folder** → select the project folder

### 3. Open Continue

`Ctrl+L` — chat with the model

---

## Usage

### Chat (`Ctrl+L`)

- Ask questions about your code
- Select code before asking — it will be included in context
- `@file` — add a specific file to context
- `@codebase` — search across the project

### Inline edit (`Ctrl+I`)

- Select code → press `Ctrl+I` → describe the change
- The model edits the file in place and shows a diff

### Autocomplete

On CPU it can feel slow (3–5 s lag). Prefer disabling or increasing debounce:
Continue → gear → Autocomplete → set a large Debounce (3000 ms) or turn off.

---

## Switching models

1. `Ctrl+C` in the server terminal
2. Start again with another name:

```
start_server.bat coder-14b
```

The label in Continue’s dropdown does not matter — the model loaded in the server is what answers.

---

## Stop

`Ctrl+C` in the server terminal.
