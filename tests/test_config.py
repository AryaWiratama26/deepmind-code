import os
import pytest
from deepmind_code.core.config import ConfigModel, get_api_key

def test_config_model_defaults():
    cfg = ConfigModel()
    
    assert cfg.default_model is not None
    assert cfg.openai_api_key is None
    assert cfg.gemini_api_key is None

def test_get_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    assert get_api_key("openai") == "test_openai_key"
    
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    assert get_api_key("gemini") == "test_gemini_key"
    
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    assert get_api_key("anthropic") == "test_anthropic_key"
    
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    assert get_api_key("groq") == "test_groq_key"
