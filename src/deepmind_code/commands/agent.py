import click
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from deepmind_code.providers.llm import LLMProvider
from deepmind_code.core.context import ContextManager
from deepmind_code.core.tools import get_tools_spec, ToolExecutor

console = Console()

@click.command()
@click.argument("prompt", required=False)
@click.option("--model", help="Model to use for the agent")
@click.option("--max-steps", default=10, help="Maximum number of steps the agent can take")
def agent(prompt: str, model: str, max_steps: int):
    """
    Run an autonomous agent that can use tools to complete project tasks.
    
    Args:
        prompt (str): The initial goal for the agent.
        model (str): Optional model identifier override.
        max_steps (int): Maximum iterative steps to allow.
    """
    llm = LLMProvider(model=model)
    executor = ToolExecutor()
    ctx = ContextManager()
    
    if not sys.stdin.isatty():
        # Re-open TTY for interactive prompts if piped
        try:
            sys.stdin = open('/dev/tty')
        except Exception:
            pass

    if not prompt:
        prompt = click.prompt("What task should I complete?")

    tools = get_tools_spec()
    project_context = ctx.get_project_context()
    
    system_prompt = (
        "You are DeepMind-Code, a professional AI coding assistant. "
        f"You have access to tools to complete tasks in the project:\n\n{project_context}"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    console.print(Panel(f"Running Agent Mode with model: [bold]{llm.model}[/bold]", title="Agent Initialized"))
    
    for step in range(max_steps):
        console.print(f"\n[bold blue]Step {step + 1}/{max_steps}[/bold blue]")
        
        # We use litellm.completion directly to handle tool calls
        import litellm
        from deepmind_code.core.config import get_api_key
        
        provider = llm.model.split("/")[0] if "/" in llm.model else "openai"
        api_key = get_api_key(provider)
        
        kwargs = {
            "model": llm.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto"
        }
        if api_key:
            kwargs["api_key"] = api_key
            
        try:
            response = litellm.completion(**kwargs)
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {str(e)}")
            break
            
        message = response.choices[0].message
        # Convert to dict for consistent history management
        msg_dict = message.model_dump()
        messages.append(msg_dict)
        
        # Initial AI response (reasoning)
        if message.content:
            console.print(f"[italic]{message.content}[/italic]")
            
        # Check for tool calls
        if not message.tool_calls:
            console.print("[green]Task completed or no further actions needed.[/green]")
            break
            
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool
            observation = executor.execute(name, args)
            
            # Feed back to history
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": str(observation)
            })
            
            # Short observation summary in terminal
            if len(str(observation)) > 100:
                obs_summary = str(observation)[:100] + "..."
            else:
                obs_summary = str(observation)
            console.print(f"[bold dim]Tool Output ({name}):[/bold dim] {obs_summary}")

    console.print("\n[bold green]Agent finished.[/bold green]")
