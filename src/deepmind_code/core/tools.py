import os
import subprocess
import click
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from deepmind_code.core.context import ContextManager

def get_tools_spec() -> List[Dict[str, Any]]:
    """
    Define the JSON schema for tools available to the agent.
    
    Returns:
        List[Dict[str, Any]]: A list of tool definitions compatible with LiteLLM/OpenAI.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "List files and directories in a given path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The directory path to list. Defaults to current directory."}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the content of a specific file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "The relative path to the file. ALWAYS use paths relative to the current directory (don't include the project root folder name)."}
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write or overwrite content to a file. Requires user confirmation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "The relative path to the file. ALWAYS use paths relative to the current directory (don't include the project root folder name)."},
                        "content": {"type": "string", "description": "The full content to write to the file."}
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Execute a shell command in the project directory. Requires user confirmation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The shell command to execute."}
                    },
                    "required": ["command"]
                }
            }
        }
    ]

class ToolExecutor:
    """
    Handles the execution of tools called by the AI agent.
    """
    def __init__(self):
        self.ctx = ContextManager()
        self.console = Console()

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        """
        Execute a tool by name with the provided arguments.
        
        Args:
            name (str): The name of the function to execute.
            args (Dict[str, Any]): The arguments for the function.
            
        Returns:
            str: The result of the execution, formatted for the LLM.
        """
        if name == "list_dir":
            path = args.get("path", ".")
            # Temporarily change root for list_dir if path is provided
            temp_ctx = ContextManager(root_dir=path)
            return temp_ctx.get_file_tree()

        elif name == "read_file":
            file_path = args.get("file_path")
            content = self.ctx.read_file(file_path)
            return content if content is not None else f"Error: File {file_path} not found."

        elif name == "write_file":
            file_path = args.get("file_path")
            content = args.get("content")
            
            lexer = os.path.splitext(file_path)[1][1:] or "python"
            self.console.print(Panel(
                Syntax(content, lexer=lexer, theme="monokai", line_numbers=True), 
                title=f"Proposed write to {file_path}"
            ))
            
            if click.confirm(f"Allow agent to write to {file_path}?"):
                try:
                    # Create parent directories if they don't exist
                    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return f"Successfully wrote to {file_path}."
                except Exception as e:
                    return f"Error writing file: {str(e)}"
            return "User denied file write permission."

        elif name == "run_command":
            command = args.get("command")
            self.console.print(f"[bold yellow]Agent wants to run:[/bold yellow] {command}")
            if click.confirm("Allow execution?"):
                try:
                    result = subprocess.run(
                        command, shell=True, capture_output=True, text=True, timeout=30
                    )
                    output = result.stdout + result.stderr
                    return f"Exit Code: {result.returncode}\nOutput:\n{output}"
                except Exception as e:
                    return f"Error executing command: {str(e)}"
            return "User denied command execution permission."

        return f"Error: Unknown tool {name}"
