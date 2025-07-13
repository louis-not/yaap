"""
Configuration management for YAAP
Handles loading and validation of LLM settings
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    base_url: str
    model: str
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API calls"""
        config = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }
        
        if self.max_tokens is not None:
            config["max_tokens"] = self.max_tokens
            
        return config
    
    @property
    def client_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for OpenAI client initialization"""
        return {
            "base_url": self.base_url,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }


def load_llm_config() -> LLMConfig:
    """
    Load LLM configuration from environment variables
    
    Returns:
        LLMConfig object with loaded settings
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    
    # Load .env file if it exists
    if env_file.exists():
        _load_env_file(env_file)
    
    # Required environment variables
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")
    
    if not base_url:
        raise ValueError("LLM_BASE_URL environment variable is required")
    if not model:
        raise ValueError("LLM_MODEL environment variable is required")
    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is required")
    
    # Optional environment variables with defaults
    timeout = int(os.getenv("LLM_TIMEOUT", "30"))
    max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_tokens = os.getenv("LLM_MAX_TOKENS")
    top_p = float(os.getenv("LLM_TOP_P", "1.0"))
    frequency_penalty = float(os.getenv("LLM_FREQUENCY_PENALTY", "0.0"))
    presence_penalty = float(os.getenv("LLM_PRESENCE_PENALTY", "0.0"))
    
    return LLMConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
        max_tokens=int(max_tokens) if max_tokens else None,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )


def _load_env_file(env_file: Path) -> None:
    """Load environment variables from .env file"""
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Only set if not already set in environment
                    if key not in os.environ:
                        os.environ[key] = value
    except Exception as e:
        # Silently ignore .env file errors
        pass