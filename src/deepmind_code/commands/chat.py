import click
import sys
import json
import os
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from deepmind_code.providers.llm import LLMProvider
from deepmind_code.core.context import ContextManager

HISTORY_DIR = Path(".dmc")
HISTORY_FILE = HISTORY_DIR / "history.json"

console = Console()

@click.command()
@click.argument("prompt", required=False)
@click.option("--model", help="Model to use for this chat session")
@click.option("--clear", is_flag=True, help="Clear chat history for this project")
def chat(prompt: str, model: str, clear: bool):
    """
    Open an interactive chat session with project context and history.
    """
    if clear:
        if HISTORY_FILE.exists():
            os.remove(HISTORY_FILE)
            console.print("[green]Chat history cleared.[/green]")
        else:
            console.print("[yellow]No chat history found to clear.[/yellow]")
        if not prompt:
            return

    llm = LLMProvider(model=model)
    ctx = ContextManager()
    
    if not sys.stdin.isatty():
        try:
            sys.stdin = open('/dev/tty')    
        except Exception:
            pass

    # Load existing history
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            if history:
                console.print(f"[dim]Loaded {len(history)} messages from history.[/dim]")
        except Exception:
            history = []

    project_context = ctx.get_project_context()
    system_prompt = (
        "You are DeepMind-Code, a professional AI coding assistant. "
        "You have access to the project file tree and content to provide relevant answers. "
        "Keep your responses concise, focused on code quality, and follow best practices."
    )
    
    # Construct message list with history
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n{project_context}"}
    ]
    messages.extend(history)
    
    if not prompt:
        prompt = click.prompt("Enter your question")
    
    messages.append({"role": "user", "content": prompt})
    
    console.print(f"[bold blue]DeepMind-Code ([italic]{llm.model}[/italic]):[/bold blue]")
    
    full_response = ""
    with Live(vertical_overflow="visible", console=console) as live:
        for chunk in llm.stream_completion(messages):
            full_response += chunk
            live.update(Markdown(full_response))
            
    # Save to history
    history.append({"role": "user", "content": prompt})
    history.append({"role": "assistant", "content": full_response})
    
    # Keep history manageable (last 20 messages)
    if len(history) > 20:
        history = history[-20:]
        
    try:
        HISTORY_DIR.mkdir(exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        console.print(f"[red]Warning: Could not save chat history: {str(e)}[/red]")
