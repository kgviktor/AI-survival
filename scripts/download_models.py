#!/usr/bin/env python3
"""
Model downloader for AI Survival project
Downloads GGUF models from HuggingFace
"""

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

# Predefined models (Q4_K_M quantization - good balance of size/quality)
AVAILABLE_MODELS = {
    # === Qwen3 Text Models ===
    "qwen3-0.6b": {
        "repo": "Qwen/Qwen3-0.6B-GGUF",
        "file": "Qwen3-0.6B-Q8_0.gguf",
        "size": "0.7 GB",
        "description": "Qwen3 ultra-light (0.6B params)",
    },
    "qwen3-1.7b": {
        "repo": "Qwen/Qwen3-1.7B-GGUF",
        "file": "Qwen3-1.7B-Q8_0.gguf",
        "size": "1.9 GB",
        "description": "Qwen3 light (1.7B params)",
    },
    "qwen3-4b": {
        "repo": "Qwen/Qwen3-4B-GGUF",
        "file": "Qwen3-4B-Q4_K_M.gguf",
        "size": "2.6 GB",
        "description": "Qwen3 fast (4B params)",
    },
    "qwen3-8b": {
        "repo": "Qwen/Qwen3-8B-GGUF",
        "file": "Qwen3-8B-Q4_K_M.gguf",
        "size": "5.0 GB",
        "description": "Qwen3 smart (8B params)",
    },
    "qwen3-14b": {
        "repo": "Qwen/Qwen3-14B-GGUF",
        "file": "Qwen3-14B-Q4_K_M.gguf",
        "size": "8.5 GB",
        "description": "Qwen3 large (14B params)",
    },
    
    # === Qwen3.5 Models ===
    "qwen3.5-0.8b": {
        "repo": "unsloth/Qwen3.5-0.8B-GGUF",
        "file": "Qwen3.5-0.8B-Q8_0.gguf",
        "size": "0.8 GB",
        "description": "Qwen3.5 ultra-light (0.8B params)",
    },
    "qwen3.5-2b": {
        "repo": "unsloth/Qwen3.5-2B-GGUF",
        "file": "Qwen3.5-2B-Q4_K_M.gguf",
        "size": "1.2 GB",
        "description": "Qwen3.5 light (2B params)",
    },
    "qwen3.5-4b": {
        "repo": "unsloth/Qwen3.5-4B-GGUF",
        "file": "Qwen3.5-4B-Q4_K_M.gguf",
        "size": "2.6 GB",
        "description": "Qwen3.5 fast (4B params)",
    },
    "qwen3.5-9b": {
        "repo": "unsloth/Qwen3.5-9B-GGUF",
        "file": "Qwen3.5-9B-Q4_K_M.gguf",
        "size": "5.3 GB",
        "description": "Qwen3.5 smart (9B params)",
    },
    
    # === Qwen3 Embedding Models ===
    "qwen3-embedding-0.6b": {
        "repo": "Qwen/Qwen3-Embedding-0.6B-GGUF",
        "file": "Qwen3-Embedding-0.6B-Q8_0.gguf",
        "size": "0.6 GB",
        "description": "Embedding ultra-light (0.6B, 1024 dims)",
    },
    "qwen3-embedding-4b": {
        "repo": "Qwen/Qwen3-Embedding-4B-GGUF",
        "file": "Qwen3-Embedding-4B-Q4_K_M.gguf",
        "size": "2.3 GB",
        "description": "Embedding balanced (4B, 2560 dims)",
    },
    "qwen3-embedding-8b": {
        "repo": "Qwen/Qwen3-Embedding-8B-GGUF",
        "file": "Qwen3-Embedding-8B-Q4_K_M.gguf",
        "size": "4.4 GB",
        "description": "Embedding best quality (8B, 4096 dims)",
    },

    # === Qwen2.5 Coder ===
    "qwen2.5-coder-7b": {
        "repo": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
        "file": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "size": "4.4 GB",
        "description": "Code & technical (7B params)",
    },
    "qwen2.5-coder-14b": {
        "repo": "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF",
        "file": "qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        "size": "8.9 GB",
        "description": "Code & technical large (14B params)",
    },
}


def list_models():
    """Display available models"""
    print("\n[*] Available models for download:\n")
    print(f"{'Name':<22} {'Size':<10} {'Description'}")
    print("-" * 70)
    
    for name, info in AVAILABLE_MODELS.items():
        print(f"{name:<22} {info['size']:<10} {info['description']}")
    
    print("\n" + "-" * 70)
    print("\nUsage: python download_models.py --model <name>")
    print("Example: python download_models.py --model qwen3-4b")
    print("\nTo download multiple: python download_models.py --model qwen3-4b qwen3-8b")


def download_model(model_name: str) -> bool:
    """Download a specific model from HuggingFace"""
    if model_name not in AVAILABLE_MODELS:
        print(f"[X] Unknown model: {model_name}")
        print("Use --list to see available models")
        return False
    
    model_info = AVAILABLE_MODELS[model_name]
    dest_path = MODELS_DIR / model_info["file"]
    
    if dest_path.exists():
        print(f"[OK] Model already exists: {model_info['file']}")
        return True
    
    print(f"\n[>>] Downloading {model_name}...")
    print(f"   Repository: {model_info['repo']}")
    print(f"   File: {model_info['file']}")
    print(f"   Size: {model_info['size']}")
    print()
    
    try:
        from huggingface_hub import hf_hub_download
        
        # Ensure models directory exists
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Download the model
        downloaded_path = hf_hub_download(
            repo_id=model_info["repo"],
            filename=model_info["file"],
            local_dir=MODELS_DIR,
            local_dir_use_symlinks=False,
        )
        
        print(f"\n[OK] Downloaded successfully: {model_info['file']}")
        return True
        
    except ImportError:
        print("[X] huggingface-hub not installed!")
        print("Run: pip install huggingface-hub")
        return False
    except Exception as e:
        print(f"[X] Download failed: {e}")
        return False


def list_downloaded():
    """List already downloaded models"""
    if not MODELS_DIR.exists():
        print("\n[i] No models directory found.")
        return
    
    models = list(MODELS_DIR.glob("*.gguf"))
    
    if not models:
        print("\n[i] No models downloaded yet.")
        return
    
    print("\n[i] Downloaded models:\n")
    for model in models:
        size_gb = model.stat().st_size / (1024**3)
        print(f"  • {model.name} ({size_gb:.1f} GB)")


def main():
    parser = argparse.ArgumentParser(
        description="Download GGUF models for AI Survival",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_models.py --list              # Show available models
  python download_models.py --model phi3-mini   # Download specific model
  python download_models.py --downloaded        # Show downloaded models
        """
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available models"
    )
    
    parser.add_argument(
        "--model", "-m",
        nargs="+",
        help="Model(s) to download"
    )
    
    parser.add_argument(
        "--downloaded", "-d",
        action="store_true", 
        help="List downloaded models"
    )
    
    args = parser.parse_args()
    
    if args.downloaded:
        list_downloaded()
        return
    
    if args.list or not args.model:
        list_models()
        list_downloaded()
        return
    
    # Download requested models
    success = True
    for model_name in args.model:
        if not download_model(model_name):
            success = False
    
    if success:
        print("\n[OK] All done! Run 'python src/chat.py' to start chatting.")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
