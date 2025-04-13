"""
LLMPack Settings - Configuration management for LLMPack tool.

This module provides functionality to:
1. Manage API keys for different LLM providers
2. Store and retrieve user preferences (LLM selection, language)
3. Handle configuration file operations
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional

import logging
from rich.logging import RichHandler

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_path=False)]
)
logger = logging.getLogger("llmpack.settings")

# Configuration file path
CONFIG_DIR = Path.home() / ".config" / "llmpack"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default settings
DEFAULT_SETTINGS = {
    "llm_provider": "gemini",
    "llm_model": "gemini-1.5-pro",  # Default model for the default provider
    "language": "en",
    "api_keys": {
        "openai": "",
        "anthropic": "",
        "gemini": "",
        "ollama": ""
    },
    "instruction_prompt": "Create a step-by-step work procedure for the following task:"
}

def ensure_config_dir():
    """Ensure the configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict:
    """
    Load configuration from file or create a new one if it doesn't exist.
    
    Returns:
        Dictionary containing configuration settings
    """
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        save_config(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_config(config: Dict):
    """
    Save configuration to file.
    
    Args:
        config: Dictionary containing configuration settings to save
    """
    ensure_config_dir()
    
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a specific provider.
    
    Args:
        provider: Name of the LLM provider
        
    Returns:
        API key string or None if not set
        
    Note:
        Checks environment variables first, then falls back to config file.
        Environment variable names follow the pattern: {PROVIDER}_API_KEY
        (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)
    """
    # Check environment variables first (convert provider to uppercase)
    env_var_name = f"{provider.upper()}_API_KEY"
    env_api_key = os.environ.get(env_var_name)
    
    if env_api_key:
        logger.debug(f"Using API key from environment variable: {env_var_name}")
        return env_api_key
    
    # Fall back to config file
    config = load_config()
    return config.get("api_keys", {}).get(provider, "")

def set_api_key(provider: str, api_key: str):
    """
    Set API key for a specific provider.
    
    Args:
        provider: Name of the LLM provider
        api_key: API key string to set
    """
    config = load_config()
    config["api_keys"][provider] = api_key
    save_config(config)
    logger.info(f"API key for {provider} updated successfully")

def get_setting(key: str) -> Optional[str]:
    """
    Get a specific setting value.
    
    Args:
        key: Setting key to retrieve
        
    Returns:
        Setting value or None if not found
    """
    config = load_config()
    return config.get(key, DEFAULT_SETTINGS.get(key))

def set_setting(key: str, value: str):
    """
    Set a specific setting value.
    
    Args:
        key: Setting key to set
        value: Setting value to set
    """
    config = load_config()
    config[key] = value
    save_config(config)
    logger.info(f"Setting {key} updated to {value}")
