import click
import os
import sys
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from deepmind_code.providers.llm import LLMProvider
from deepmind_code.core.context import ContextManager

console = Console()

@click.command()
@click.argument("file_input")
@click.argument("instructions", nargs=-1)
@click.option("--model", help="Model to use for editing")
def edit(file_input, instructions, model):
    """
    Modify a file based on natural language instructions.
    
    Args:
        file_input (str): The filename or path to the file to be edited.
        instructions (tuple): Natural language instructions for editing.
        model (str): Optional override for the LLM model.
    """
    instruction_str = " ".join(instructions)
    if not instruction_str:
        instruction_str = click.prompt("Enter changes to be made")

    llm = LLMProvider(model=model)
    ctx = ContextManager()
    
    if not sys.stdin.isatty():
        try:
            sys.stdin = open('/dev/tty')
        except Exception:
            pass

    # Resolve the file path
    file = ctx.find_file(file_input)
    if not file:
        console.print(f"[red]Error: Could not find '{file_input}' in the current project context.[/red]")
        return

    content = ctx.read_file(file)
    if content is None:
        console.print(f"[red]Error: File '{file}' does not exist or cannot be read.[/red]")
        return

    system_prompt = (
        "You are an expert software engineer. You will receive existing file content and editing instructions. "
        "Your goal is to return the entire updated content of the file. "
        "Do not include any explanations, comments outside the code, or markdown formatting like ```python. "
        "Provide only the raw updated source code."
    )
    
    user_prompt = f"File: {file}\n\nContent:\n{content}\n\nInstructions: {instruction_str}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    console.print(f"[bold blue]Processing {file}...[/bold blue]")
    
    response = llm.completion(messages)
    new_content = response.choices[0].message.content.strip() if response.choices else ""

    if not new_content:
        console.print("[red]Error: The AI returned an empty response.[/red]")
        return

    # Clean up markdown formatting if the AI ignored instructions
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        new_content = "\n".join(lines).strip()

    if new_content == content.strip():
        console.print("[yellow]No changes were suggested by the AI.[/yellow]")
        return

    # Display preview
    console.print(Panel(
        Syntax(new_content, lexer=os.path.splitext(file)[1][1:] or "python", theme="monokai", line_numbers=True), 
        title="Preview Changes"
    ))
    
    if click.confirm("Apply these changes?"):
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)
            console.print(f"[green]Successfully updated {file}.[/green]")
        except Exception as e:
            console.print(f"[red]Error writing to file: {str(e)}[/red]")
    else:
        console.print("[yellow]Operation cancelled. Changes were not applied.[/yellow]")
