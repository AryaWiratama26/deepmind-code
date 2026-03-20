import click
import sys
from rich.console import Console
from rich.panel import Panel
from deepmind_code.providers.llm import LLMProvider
from deepmind_code.core.context import ContextManager

console = Console()

@click.command()
@click.argument("error_output", required=False)
def fix(error_output: str):
    """
    Analyze terminal errors and suggest potential fixes.
    
    Args:
        error_output (str): The error message or traceback to analyze.
    """
    if not error_output and not sys.stdin.isatty():
        error_output = sys.stdin.read().strip()
        
        try:
            sys.stdin = open('/dev/tty')
        except Exception:
            pass

    if not error_output:
        error_output = click.prompt("Paste the error/output here")

    llm = LLMProvider()
    ctx = ContextManager()
    
    project_context = ctx.get_project_context()
    system_prompt = (
        "You are an expert software debugger. Analyze the provided error output in the context of the project. "
        "Identify the cause of the failure and provide a specific fix. "
        "If a specific file needs modification, identify it clearly."
    )
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n{project_context}"},
        {"role": "user", "content": f"I encountered the following error:\n{error_output}"}
    ]
    
    console.print("[bold red]Analyzing log output...[/bold red]")
    
    response = llm.completion(messages)
    analysis = response.choices[0].message.content if response.choices else "AI returned an empty analysis."
    console.print(Panel(analysis, title="Suggested Resolution", border_style="red"))

    # Attempt to extract file path and offer editing
    # We ask the LLM in a separate call to be sure we get the right file and content
    if click.confirm("Would you like me to try and apply this fix automatically?"):
        apply_prompt = (
            f"Based on your analysis:\n{analysis}\n\n"
            "If this fix applies to a file, identify the file path and return the COMPLETELY UPDATED content of that file. "
            "Format your response as:\nFile: [path]\nContent:\n[code]\n\n"
            "If no single file can be updated, return 'NO_FILE'."
        )
        
        messages.append({"role": "user", "content": apply_prompt})
        
        console.print("[bold blue]Generating fix...[/bold blue]")
        fix_response = llm.completion(messages)
        fix_text = fix_response.choices[0].message.content if fix_response.choices else ""
        
        if "File:" in fix_text and "Content:" in fix_text:
            try:
                # Basic parsing
                lines = fix_text.split("\n")
                file_path = ""
                for line in lines:
                    if line.startswith("File:"):
                        file_path = line.replace("File:", "").strip()
                        break
                
                content_start = fix_text.find("Content:\n") + len("Content:\n")
                new_content = fix_text[content_start:].strip()
                
                # Clean up markdown if AI ignored instructions
                if new_content.startswith("```"):
                    c_lines = new_content.split("\n")
                    if c_lines[0].startswith("```"):
                        c_lines = c_lines[1:]
                    if c_lines and c_lines[-1].startswith("```"):
                        c_lines = c_lines[:-1]
                    new_content = "\n".join(c_lines).strip()

                # Call edit-like preview and apply
                from rich.syntax import Syntax
                import os
                console.print(Panel(
                    Syntax(new_content, lexer=os.path.splitext(file_path)[1][1:] or "python", theme="monokai", line_numbers=True), 
                    title=f"Fix for {file_path}"
                ))
                
                if click.confirm(f"Apply this fix to {file_path}?"):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    console.print(f"[green]Successfully fixed {file_path}.[/green]")
            except Exception as e:
                console.print(f"[red]Error applying fix: {str(e)}[/red]")
        else:
            console.print("[yellow]Could not identify a specific file to update.[/yellow]")

@click.command()
@click.argument("path", default=".")
def review(path: str):
    """
    Review code within a specific directory for quality and best practices.
    
    Args:
        path (str): The directory path to review. Defaults to the current directory.
    """
    llm = LLMProvider()
    ctx = ContextManager(root_dir=path)
    
    project_context = ctx.get_project_context()
    
    system_prompt = (
        "You are a senior technical lead. Review the provided project structure and context. "
        "Provide actionable feedback on architecture, code quality, potential issues, and scalability."
    )
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n{project_context}"},
        {"role": "user", "content": "Please perform a review of this project folder."}
    ]
    
    console.print(f"[bold blue]Reviewing path: {path}...[/bold blue]")
    
    response = llm.completion(messages)
    console.print(Panel(
        response.choices[0].message.content if response.choices else "AI returned an empty review.", 
        title="Technical Review"
    ))
