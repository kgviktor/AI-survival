#!/usr/bin/env python3
"""
AI Survival Chat - Standalone version using llama.cpp binary directly
No llama-cpp-python required - uses subprocess to call llama-cli
"""

import os
import sys
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Path to llama.cpp binary (will be set up)
LLAMA_CLI = PROJECT_ROOT / "bin" / "llama-cli.exe"


def load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        console.print("[red]Error: config.yaml not found![/red]")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_llama_cli():
    """Check if llama-cli binary exists"""
    if not LLAMA_CLI.exists():
        console.print("[red]llama-cli.exe not found![/red]")
        console.print(f"\nExpected location: {LLAMA_CLI}")
        console.print("\nDownload from: https://github.com/ggerganov/llama.cpp/releases")
        console.print("Extract and place llama-cli.exe in the 'bin' folder")
        console.print("\nOr run: python scripts/setup_llama_cpp.py")
        sys.exit(1)


def get_available_models(config: dict) -> list:
    """Get list of available GGUF models"""
    models_dir = PROJECT_ROOT / config["paths"]["models_dir"]
    if not models_dir.exists():
        return []
    return list(models_dir.glob("*.gguf"))


def select_model(models: list) -> Path:
    """Interactive model selection"""
    if not models:
        console.print("[red]No models found in models/ directory![/red]")
        console.print("\nDownload a model first:")
        console.print("  python scripts/download_models.py --list")
        sys.exit(1)
    
    if len(models) == 1:
        console.print(f"[green]Using model:[/green] {models[0].name}")
        return models[0]
    
    console.print("\n[bold]Available models:[/bold]")
    for i, model in enumerate(models, 1):
        size_mb = model.stat().st_size / (1024 * 1024)
        console.print(f"  {i}. {model.name} ({size_mb:.0f} MB)")
    
    while True:
        choice = Prompt.ask("\nSelect model number", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]
        except ValueError:
            pass
        console.print("[red]Invalid choice[/red]")


def generate_response(model_path: Path, prompt: str, config: dict) -> str:
    """Generate response using llama-cli"""
    model_config = config.get("model", {})
    
    cmd = [
        str(LLAMA_CLI),
        "-m", str(model_path),
        "-p", prompt,
        "-n", str(model_config.get("max_tokens", 512)),
        "-t", str(model_config.get("n_threads", 8)),
        "-c", str(model_config.get("context_length", 4096)),
        "--temp", str(model_config.get("temperature", 0.7)),
        "--top-p", str(model_config.get("top_p", 0.9)),
        "--no-display-prompt",
        "-e",  # Escape newlines
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error: {result.stderr}[/red]")
            return ""
        
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        console.print("[red]Generation timed out[/red]")
        return ""
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return ""


def build_prompt(messages: list, system_prompt: str) -> str:
    """Build prompt string for llama-cli (ChatML format)"""
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
    
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    
    prompt += "<|im_start|>assistant\n"
    return prompt


def main():
    """Main chat loop"""
    console.print(Panel.fit(
        "[bold green]AI Survival Assistant[/bold green]\n"
        "[dim](Standalone mode - using llama.cpp binary)[/dim]\n\n"
        "[dim]Commands: /help, /clear, /quit[/dim]",
        border_style="green"
    ))
    
    # Check for llama-cli
    check_llama_cli()
    
    # Load config
    config = load_config()
    
    # Find and select model
    models = get_available_models(config)
    model_path = select_model(models)
    
    console.print(f"\n[green]Model loaded: {model_path.name}[/green]")
    
    # Initialize chat
    system_prompt = config.get("system_prompt", "You are a helpful assistant.")
    messages = []
    
    console.print("[dim]Type your message and press Enter. Type /quit to exit.[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()
                
                if cmd in ("/quit", "/exit", "/q"):
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                elif cmd in ("/clear", "/c"):
                    messages = []
                    console.clear()
                    console.print("[green]Chat history cleared.[/green]\n")
                    continue
                
                elif cmd in ("/help", "/h"):
                    console.print(Panel(
                        "[bold]Commands:[/bold]\n"
                        "  /help, /h   - Show this help\n"
                        "  /clear, /c  - Clear chat history\n"
                        "  /quit, /q   - Exit",
                        title="Help",
                        border_style="blue"
                    ))
                    continue
                
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                    continue
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Build full prompt
            prompt = build_prompt(messages, system_prompt)
            
            # Generate response
            console.print("[bold cyan]AI:[/bold cyan] ", end="")
            with console.status("[dim]Thinking...[/dim]", spinner="dots"):
                response = generate_response(model_path, prompt, config)
            
            if response:
                # Clean up response (remove end token if present)
                response = response.split("<|im_end|>")[0].strip()
                console.print(response)
                messages.append({"role": "assistant", "content": response})
            
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type /quit to exit.[/yellow]")
            continue


if __name__ == "__main__":
    main()
