import click
from rich.console import Console
from rich.panel import Panel
from deepmind_code.core.config import load_config, save_config, ConfigModel
from deepmind_code.commands.chat import chat
from deepmind_code.commands.edit import edit
from deepmind_code.commands.shell import fix, review
from deepmind_code.commands.agent import agent

console = Console()

@click.group()
@click.version_option()
def cli():
    """deepmind-code: AI-powered coding assistant for the terminal."""
    pass

@cli.command()
@click.option("--model", help="Default LLM model identifier")
@click.option("--openai-key", help="OpenAI API Key")
@click.option("--gemini-key", help="Gemini/Google API Key")
@click.option("--anthropic-key", help="Anthropic API Key")
@click.option("--groq-key", help="Groq API Key")
def config(model, openai_key, gemini_key, anthropic_key, groq_key):
    """View or update application configuration."""
    cfg = load_config()
    
    if model: cfg.default_model = model
    if openai_key: cfg.openai_api_key = openai_key
    if gemini_key: cfg.gemini_api_key = gemini_key
    if anthropic_key: cfg.anthropic_api_key = anthropic_key
    if groq_key: cfg.groq_api_key = groq_key
    
    if any([model, openai_key, gemini_key, anthropic_key, groq_key]):
        save_config(cfg)
        console.print("[green]Configuration updated successfully.[/green]")
    else:
        console.print(Panel(
            f"[bold blue]Current Settings:[/bold blue]\n\n"
            f"Default Model: {cfg.default_model}\n"
            f"OpenAI Key: {'[green]SET[/green]' if cfg.openai_api_key else '[red]NOT SET[/red]'}\n"
            f"Gemini Key: {'[green]SET[/green]' if cfg.gemini_api_key else '[red]NOT SET[/red]'}\n"
            f"Anthropic Key: {'[green]SET[/green]' if cfg.anthropic_api_key else '[red]NOT SET[/red]'}\n"
            f"Groq Key: {'[green]SET[/green]' if cfg.groq_api_key else '[red]NOT SET[/red]'}",
            title="deepmind-code configuration"
        ))

# Register subcommands
cli.add_command(chat)
cli.add_command(edit)
cli.add_command(fix)
cli.add_command(review)
cli.add_command(agent)

if __name__ == "__main__":
    cli()
