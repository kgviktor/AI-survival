#!/usr/bin/env python3
"""
Download and setup llama.cpp binary for Windows
"""

import os
import sys
import zipfile
import tempfile
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BIN_DIR = PROJECT_ROOT / "bin"

# GitHub API to get latest release
GITHUB_API_URL = "https://api.github.com/repos/ggerganov/llama.cpp/releases/latest"


def check_avx2():
    """Check if CPU supports AVX2"""
    # Most modern Intel/AMD CPUs support AVX2
    # i5-13420H definitely supports AVX2
    return True


def get_latest_release_url(use_avx2=True):
    """Get download URL for latest llama.cpp release"""
    import httpx
    
    print("[*] Finding latest llama.cpp release...")
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(GITHUB_API_URL)
            response.raise_for_status()
            release = response.json()
            
            assets = release.get("assets", [])
            
            # Priority 1: exact match for avx2/noavx CPU-only build
            for asset in assets:
                name = asset.get("name", "")
                # Looking for: llama-bXXXX-bin-win-avx2-x64.zip (not cuda, not vulkan)
                if use_avx2:
                    if "win-avx2-x64.zip" in name and "cuda" not in name.lower() and "vulkan" not in name.lower():
                        print(f"   Found: {name}")
                        return asset.get("browser_download_url")
                else:
                    if "win-noavx-x64.zip" in name and "cuda" not in name.lower():
                        print(f"   Found: {name}")
                        return asset.get("browser_download_url")
            
            # Priority 2: any avx/noavx without cuda
            for asset in assets:
                name = asset.get("name", "")
                if "win" in name and "x64.zip" in name:
                    if "cuda" not in name.lower() and "cudart" not in name.lower() and "vulkan" not in name.lower():
                        print(f"   Found (alt): {name}")
                        return asset.get("browser_download_url")
                    
    except Exception as e:
        print(f"   [X] Failed to get release info: {e}")
    
    return None


def download_llama_cpp():
    """Download llama.cpp binaries"""
    try:
        import httpx
    except ImportError:
        print("Installing required packages...")
        os.system("pip install httpx")
        import httpx
    
    print("[*] Checking CPU capabilities...")
    use_avx2 = check_avx2()
    
    url = get_latest_release_url(use_avx2)
    
    if not url:
        print("[X] Could not find download URL")
        print("\nManual download:")
        print("1. Go to: https://github.com/ggerganov/llama.cpp/releases")
        print("2. Download: llama-*-bin-win-avx2-x64.zip")
        print(f"3. Extract llama-cli.exe to: {BIN_DIR}")
        return False
    
    print(f"[>>] Downloading llama.cpp {'(AVX2)' if use_avx2 else '(no-AVX)'}...")
    print(f"   URL: {url}")
    
    # Create bin directory
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        with httpx.Client(follow_redirects=True, timeout=300) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
        
        print("[*] Extracting...")
        
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            # Extract only the needed files
            for member in zip_ref.namelist():
                if member.endswith(('.exe', '.dll')):
                    # Extract to bin folder
                    filename = os.path.basename(member)
                    with zip_ref.open(member) as source:
                        dest_path = BIN_DIR / filename
                        with open(dest_path, 'wb') as dest:
                            dest.write(source.read())
                        print(f"   Extracted: {filename}")
        
        # Clean up
        os.unlink(tmp_path)
        
        # Check if main binary exists
        llama_cli = BIN_DIR / "llama-cli.exe"
        if llama_cli.exists():
            print(f"\n[OK] Success! llama-cli.exe is ready at: {llama_cli}")
            return True
        else:
            # Try alternative names
            for alt_name in ["main.exe", "llama.exe"]:
                alt_path = BIN_DIR / alt_name
                if alt_path.exists():
                    # Rename to llama-cli.exe
                    alt_path.rename(llama_cli)
                    print(f"\n[OK] Success! Renamed {alt_name} to llama-cli.exe")
                    return True
            
            print("\n⚠️  Download completed but llama-cli.exe not found")
            print(f"   Check {BIN_DIR} and rename the main binary to llama-cli.exe")
            return False
            
    except Exception as e:
        print(f"\n[X] Download failed: {e}")
        print("\nManual download:")
        print("1. Go to: https://github.com/ggerganov/llama.cpp/releases")
        print("2. Download: llama-*-bin-win-avx2-x64.zip")
        print(f"3. Extract llama-cli.exe to: {BIN_DIR}")
        return False


def main():
    print("=" * 50)
    print("  llama.cpp Setup for AI Survival")
    print("=" * 50)
    print()
    
    llama_cli = BIN_DIR / "llama-cli.exe"
    
    if llama_cli.exists():
        print(f"[OK] llama-cli.exe already exists at: {llama_cli}")
        overwrite = input("\nOverwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Keeping existing binary.")
            return
    
    download_llama_cpp()
    
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Download a model: python scripts/download_models.py --model phi3-mini")
    print("2. Start chatting: python src/chat_standalone.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
