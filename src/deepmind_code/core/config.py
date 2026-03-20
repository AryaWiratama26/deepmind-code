import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

CONFIG_DIR = Path.home() / ".dmc"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

class ConfigModel(BaseModel):
    """
    Data model for the application configuration.
    
    Attributes:
        default_model (str): The default LLM model to use for completions.
        openai_api_key (Optional[str]): API key for OpenAI services.
        gemini_api_key (Optional[str]): API key for Google Gemini services.
        anthropic_api_key (Optional[str]): API key for Anthropic services.
        groq_api_key (Optional[str]): API key for Groq services.
        ollama_base_url (str): Base URL for local Ollama instance.
    """
    default_model: str = Field(default="gemini/gemini-pro")
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

def load_config() -> ConfigModel:
    """
    Load the configuration from the YAML file.
    
    Returns:
        ConfigModel: The loaded configuration or a default one if the file doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return ConfigModel()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            return ConfigModel(**data)
    except Exception:
        return ConfigModel()

def save_config(config: ConfigModel):
    """
    Save the given configuration to the YAML file.
    
    Args:
        config (ConfigModel): The configuration object to save.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config.model_dump(exclude_none=True), f)

def get_api_key(provider: str) -> Optional[str]:
    """
    Retrieve the API key for a specific provider from environment variables or configuration.
    
    Args:
        provider (str): The name of the AI provider (e.g., 'openai', 'gemini').
        
    Returns:
        Optional[str]: The API key if found, otherwise None.
    """
    config = load_config()
    
    if provider == "openai":
        return os.getenv("OPENAI_API_KEY") or config.openai_api_key
    elif provider in ["gemini", "google"]:
        return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or config.gemini_api_key
    elif provider == "anthropic":
        return os.getenv("ANTHROPIC_API_KEY") or config.anthropic_api_key
    elif provider == "groq":
        return os.getenv("GROQ_API_KEY") or config.groq_api_key
    
    return None
