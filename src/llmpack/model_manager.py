"""
LLMPack Model Manager - Manages available models for different LLM providers.

This module provides functionality to:
1. Define model definitions directly in code
2. Get available models for a specific provider
3. Get default model for a provider
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import logging
from rich.logging import RichHandler

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_path=False)]
)
logger = logging.getLogger("llmpack.model_manager")

# Define models directly in code
MODELS = {
    "openai": [
        {
            "id": "gpt-4.5",
            "name": "GPT-4.5",
            "description": "Most capable model with vision and high token limit"
        },
        {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "description": "Powerful model with good balance of capabilities"
        },
        {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "description": "Fast and cost-effective model"
        }
    ],
    "anthropic": [
        {
            "id": "claude-3.7-sonnet",
            "name": "Claude 3.7 Sonnet",
            "description": "Most powerful Claude model with highest reasoning capabilities"
        },
        {
            "id": "claude-3.5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "description": "Balanced model with good performance and speed"
        },
        {
            "id": "claude-3.5-haiku",
            "name": "Claude 3.5 Haiku",
            "description": "Fast and efficient model for simpler tasks"
        }
    ],
    "gemini": [
        {
            "id": "gemini-2.5-pro-preview-03-25",
            "name": "Gemini 2.5 Pro",
            "description": "Most capable Gemini model with 1M token context"
        },
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "description": "Fast and efficient model with 1M token context"
        },
        {
            "id": "gemini-nano",
            "name": "Gemini Nano",
            "description": "Previous generation model"
        }
    ],
    "ollama": [
        {
            "id": "llama3",
            "name": "Llama 3",
            "description": "Latest Llama model from Meta"
        },
        {
            "id": "llama3:8b",
            "name": "Llama 3 (8B)",
            "description": "Smaller and faster Llama 3 model"
        },
        {
            "id": "mistral",
            "name": "Mistral",
            "description": "Efficient open-source model"
        },
        {
            "id": "mixtral",
            "name": "Mixtral",
            "description": "Mixture of experts model with strong capabilities"
        }
    ]
}

def load_models() -> Dict[str, List[Dict[str, str]]]:
    """
    Load model definitions from the MODELS dictionary.
    
    Returns:
        Dictionary mapping provider names to lists of model definitions
    """
    return MODELS

def get_models_for_provider(provider: str) -> List[Dict[str, str]]:
    """
    Get available models for a specific provider.
    
    Args:
        provider: Name of the LLM provider
        
    Returns:
        List of model definitions for the provider
    """
    models = load_models()
    return models.get(provider, [])

def get_default_model_for_provider(provider: str) -> Optional[str]:
    """
    Get the default model ID for a specific provider.
    
    Args:
        provider: Name of the LLM provider
        
    Returns:
        Default model ID or None if no models are available
    """
    models = get_models_for_provider(provider)
    if models:
        return models[0]["id"]
    return None

def get_model_info(provider: str, model_id: str) -> Optional[Dict[str, str]]:
    """
    Get information about a specific model.
    
    Args:
        provider: Name of the LLM provider
        model_id: ID of the model
        
    Returns:
        Model information dictionary or None if not found
    """
    models = get_models_for_provider(provider)
    for model in models:
        if model["id"] == model_id:
            return model
    return None
