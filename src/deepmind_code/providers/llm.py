import litellm
import click
from typing import List, Dict, Generator, Any
from deepmind_code.core.config import get_api_key, load_config

# Configure litellm to be quiet
litellm.set_verbose = False

class LLMProvider:
    """
    Abstractions for interacting with various LLM providers using LiteLLM.
    """
    def __init__(self, model: str = None):
        """
        Initialize the LLMProvider.
        
        Args:
            model (str, optional): The model identifier to use. Defaults to the configured default.
        """
        config = load_config()
        self.model = model or config.default_model

    def completion(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        """
        Generate a completion using the selected model.
        
        Args:
            messages (List[Dict[str, str]]): List of message objects for the chat history.
            stream (bool): Whether to stream the response.
            
        Returns:
            Any: The response from LiteLLM.
            
        Raises:
            click.Abort: If an error occurs during the completion process.
        """
        provider = self.model.split("/")[0] if "/" in self.model else "openai"
        api_key = get_api_key(provider)
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        if api_key:
            kwargs["api_key"] = api_key
            
        try:
            return litellm.completion(**kwargs)
        except Exception as e:
            from rich.console import Console
            Console().print(f"[bold red]AI Error:[/bold red] {str(e)}")
            if "API key" in str(e) or "key not valid" in str(e).lower():
                Console().print(f"[yellow]Tip: Use 'dmc config --{provider}-key <YOUR_KEY>' to set your API key.[/yellow]")
            raise click.Abort()

    def stream_completion(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Generate a streaming completion.
        
        Args:
            messages (List[Dict[str, str]]): List of message objects.
            
        Yields:
            str: Chunks of the generated content.
        """
        response = self.completion(messages, stream=True)
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
