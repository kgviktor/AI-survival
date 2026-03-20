#!/usr/bin/env python3
"""
AI Survival Chat - Terminal interface for local LLM
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

console = Console()


def load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        console.print("[red]Error: config.yaml not found![/red]")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_available_models(config: dict) -> list:
    """Get list of available GGUF models in models directory"""
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
        console.print("  python scripts/download_models.py --model phi3-mini")
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
        console.print("[red]Invalid choice, try again[/red]")


def load_llm(model_path: Path, config: dict):
    """Load LLM model"""
    try:
        from llama_cpp import Llama
    except ImportError:
        console.print("[red]llama-cpp-python not installed![/red]")
        console.print("Run: pip install llama-cpp-python")
        sys.exit(1)
    
    model_config = config.get("model", {})
    
    console.print(f"\n[yellow]Loading model: {model_path.name}...[/yellow]")
    
    llm = Llama(
        model_path=str(model_path),
        n_ctx=model_config.get("context_length", 4096),
        n_threads=model_config.get("n_threads", 8),
        n_gpu_layers=model_config.get("n_gpu_layers", 0),
        verbose=False,
    )
    
    console.print("[green]Model loaded successfully![/green]\n")
    return llm


def chat_completion(llm, messages: list, config: dict) -> str:
    """Generate chat completion with streaming"""
    model_config = config.get("model", {})
    
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=model_config.get("max_tokens", 1024),
        temperature=model_config.get("temperature", 0.7),
        top_p=model_config.get("top_p", 0.9),
        stream=True,
    )
    
    full_response = ""
    console.print("[bold cyan]AI:[/bold cyan] ", end="")
    
    for chunk in response:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            content = delta["content"]
            full_response += content
            console.print(content, end="")
    
    console.print()  # New line after response
    return full_response


def main():
    """Main chat loop"""
    console.print(Panel.fit(
        "[bold green]AI Survival Assistant[/bold green]\n"
        "Автономный ИИ-помощник для выживания\n\n"
        "[dim]Команды: /help, /clear, /quit[/dim]",
        border_style="green"
    ))
    
    # Load config
    config = load_config()
    
    # Find and select model
    models = get_available_models(config)
    model_path = select_model(models)
    
    # Load model
    llm = load_llm(model_path, config)
    
    # Initialize chat history
    system_prompt = config.get("system_prompt", "You are a helpful assistant.")
    messages = [{"role": "system", "content": system_prompt}]
    
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
                    messages = [{"role": "system", "content": system_prompt}]
                    console.clear()
                    console.print("[green]Chat history cleared.[/green]\n")
                    continue
                
                elif cmd in ("/help", "/h"):
                    console.print(Panel(
                        "[bold]Commands:[/bold]\n"
                        "  /help, /h   - Show this help\n"
                        "  /clear, /c  - Clear chat history\n"
                        "  /quit, /q   - Exit the program",
                        title="Help",
                        border_style="blue"
                    ))
                    continue
                
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                    continue
            
            # Add user message to history
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = chat_completion(llm, messages, config)
            
            # Add assistant response to history
            messages.append({"role": "assistant", "content": response})
            
            console.print()  # Empty line for readability
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type /quit to exit.[/yellow]")
            continue


if __name__ == "__main__":
    main()
