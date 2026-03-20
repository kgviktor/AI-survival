#!/usr/bin/env python3
"""Quick test script - runs a single prompt through the model"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = REPO_ROOT / "bin"
MODELS_DIR = REPO_ROOT / "models"

LLAMA_CLI = BIN_DIR / "llama-cli.exe"

def test_model():
    # Find first available model
    models = list(MODELS_DIR.glob("*.gguf"))
    if not models:
        print("[X] No models found in models/ directory")
        return False
    
    model_path = models[0]
    print(f"[*] Testing model: {model_path.name}")
    print(f"[*] This may take 30-60 seconds on first run...")
    print()
    
    # Test prompt
    prompt = "Briefly explain how to purify water in a survival situation. Answer in 2-3 sentences."
    
    cmd = [
        str(LLAMA_CLI),
        "-m", str(model_path),
        "-p", f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "-n", "256",
        "-t", "8",
        "-c", "2048",
        "--temp", "0.7",
        "-ngl", "0",
        "--no-display-prompt",
    ]
    
    print(f"[>>] Prompt: {prompt}")
    print()
    print("[*] Generating response...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            print(response)
            print("-" * 50)
            print()
            print("[OK] Model works correctly!")
            return True
        else:
            print(f"[X] Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[X] Generation timed out (>3 min)")
        return False
    except Exception as e:
        print(f"[X] Error: {e}")
        return False


if __name__ == "__main__":
    success = test_model()
    print()
    if success:
        print("=" * 50)
        print("To start interactive chat (from repo root):")
        print()
        print(f'  cd /d "{REPO_ROOT}"')
        print("  run.bat qwen3.5-4b")
        print("=" * 50)
    sys.exit(0 if success else 1)
