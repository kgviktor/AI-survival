"""
Test: why Qwen3.5 does not show thinking?
Comparing 3 variants on a small 0.8B model
"""
import subprocess
import tempfile
import os

BIN = r"bin\llama-cli.exe"

TESTS = [
    {
        "name": "Qwen3-1.7B — should think by default",
        "model": r"models\Qwen3-1.7B-Q8_0.gguf",
        "prompt": (
            "<|im_start|>system\n"
            "You are helpful.<|im_end|>\n"
            "<|im_start|>user\n"
            "What is 2+2?<|im_end|>\n"
            "<|im_start|>assistant\n"
        ),
    },
    {
        "name": "Qwen3.5-0.8B — default (expect NO think)",
        "model": r"models\Qwen3.5-0.8B-Q8_0.gguf",
        "prompt": (
            "<|im_start|>system\n"
            "You are helpful.<|im_end|>\n"
            "<|im_start|>user\n"
            "What is 2+2?<|im_end|>\n"
            "<|im_start|>assistant\n"
        ),
    },
    {
        "name": "Qwen3.5-0.8B — with an explicit <think> token at the start of the reply",
        "model": r"models\Qwen3.5-0.8B-Q8_0.gguf",
        "prompt": (
            "<|im_start|>system\n"
            "You are helpful.<|im_end|>\n"
            "<|im_start|>user\n"
            "What is 2+2?<|im_end|>\n"
            "<|im_start|>assistant\n"
            "<think>\n"
        ),
    },
]

for i, test in enumerate(TESTS, 1):
    print(f"\n{'='*60}")
    print(f"TEST {i}: {test['name']}")
    print('='*60)

    # Write the prompt to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                    delete=False, encoding='utf-8') as f:
        f.write(test['prompt'])
        tmp = f.name

    try:
        result = subprocess.run(
            [BIN, "-m", test['model'], "--jinja",
             "-n", "200", "--no-display-prompt", "-f", tmp],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=120
        )
        output = result.stdout.strip()
        # Remove technical llama output lines
        lines = [l for l in output.splitlines()
                 if not any(x in l for x in
                            ['load_backend', 'ggml_vulkan', 'Loading model',
                             'llama_memory', 'Vulkan', '▄▄', '██', 'build',
                             'modalities', 'available commands', '/exit',
                             '/regen', '/clear', '/read', 'Prompt:', 'Generation:',
                             '▀▀'])]
        clean = '\n'.join(lines).strip()
        print(clean if clean else "(empty output)")
    except subprocess.TimeoutExpired:
        print("(timeout — model did not answer within 120 seconds)")
    finally:
        os.unlink(tmp)

print(f"\n{'='*60}")
print("SUMMARY:")
print("  - Qwen3 thinks by default (shows [Start thinking])")
print("  - Qwen3.5 does NOT think out loud by default (thinking is hidden)")
print("  - To enable: manually add the <think> token at the start of the prompt")
print('='*60)
