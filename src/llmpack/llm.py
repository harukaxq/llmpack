"""
LLMPack LLM - LLM query execution for LLMPack tool.

This module provides functionality to:
1. Initialize and configure LLM providers using direct API requests
2. Execute queries with user prompts and predefined instruction templates
3. Handle responses from different LLM providers
"""
import os
import json
import requests
from typing import Optional, Dict, Any, List
import logging
from rich.logging import RichHandler

from llmpack.settings import get_api_key, get_setting
from llmpack.model_manager import get_default_model_for_provider

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_path=False)]
)
logger = logging.getLogger("llmpack.llm")

class LLMProvider:
    """Base class for LLM providers"""
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generate a response from the LLM"""
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None

class AnthropicProvider(LLMProvider):
    """Anthropic API provider implementation"""
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return None

class GeminiProvider(LLMProvider):
    """Google Gemini API provider implementation"""
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        # Combine system prompt and user prompt for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        return self._generate_non_stream(combined_prompt)
    
    def _generate_non_stream(self, prompt: str) -> str:
        """Use the non-streaming API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.0
            }
        }
        
        response = requests.post(url, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    

class OllamaProvider(LLMProvider):
    """Ollama API provider implementation"""
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        url = "http://localhost:11434/api/chat"
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None

def initialize_llm(provider: Optional[str] = None) -> Optional[LLMProvider]:
    """
    Initialize the LLM based on the provider and model specified in settings or passed as argument.
    
    Args:
        provider: Optional provider name to override the setting
        
    Returns:
        Initialized LLM provider instance or None if initialization fails
    """
    if provider is None:
        provider = get_setting("llm_provider")

    if provider is None:
        logger.error("No LLM provider specified. Please set the provider using 'llmpack init'.")
        return None
    
    # Get the model from settings or use default
    model = get_setting("llm_model")
    if not model:
        model = get_default_model_for_provider(provider)
        if not model:
            logger.error(f"No model found for provider {provider}.")
            return None
    
    api_key = get_api_key(provider)
    if not api_key and provider != "ollama":
        logger.error(f"No API key found for {provider}. Please set the API key using 'llmpack init' or set the {provider.upper()}_API_KEY environment variable.")
        return None
    
    # Log if using API key from environment variable
    if os.environ.get(f"{provider.upper()}_API_KEY") and provider != "ollama":
        logger.info(f"Using API key from environment variable: {provider.upper()}_API_KEY")
    
    logger.info(f"Initializing {provider} with model {model}")
    
    try:
        if provider == "openai":
            return OpenAIProvider(model=model, api_key=api_key)
        elif provider == "anthropic":
            return AnthropicProvider(model=model, api_key=api_key)
        elif provider == "gemini":
            return GeminiProvider(model=model, api_key=api_key)
        elif provider == "ollama":
            return OllamaProvider(model=model)
        else:
            logger.error(f"Unsupported LLM provider: {provider}")
            return None
    except Exception as e:
        logger.error(f"Error initializing {provider}: {e}")
        return None

def query_llm(task: str, provider: Optional[str] = None) -> Optional[str]:
    """
    Query the LLM with a predefined instruction prompt, user task, and combined code files.
    
    Args:
        task: The task or question to ask the LLM
        provider: Optional provider name to override the setting
        
    Returns:
        Response from the LLM as a string, or None if query fails
    """
    llm = initialize_llm(provider)
    if llm is None:
        return None
    
    # First, combine all code files
    from pathlib import Path
    import tempfile
    from llmpack.cli import load_gitignore_patterns, combine_files
    
    # Create a temporary file for the combined content
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    combined_content = ""
    try:
        # Load .gitignore patterns
        gitignore_data = load_gitignore_patterns()
        
        # Combine files into the temporary file
        combine_files(gitignore_data, temp_path)
        
        # Read the combined content
        combined_content = temp_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error combining files: {e}")
    finally:
        # Delete the temporary file
        if temp_path.exists():
            temp_path.unlink()
    
    instruction_prompt = get_setting("instruction_prompt")
    language = get_setting("language")
    
    # Prepare the prompts
    system_prompt = f"You are a helpful AI assistant. Respond in {language}."
    user_prompt = f"{instruction_prompt}\n\n{task}\n\nHere is the combined code from the project:\n\n{combined_content}"
    
    try:
        # Execute query
        logger.info(f"Querying {provider or get_setting('llm_provider')}...")
        response = llm.generate(system_prompt, user_prompt)
        return response
    except Exception as e:
        logger.error(f"Error querying LLM: {e}")
        return None

if __name__ == "__main__":
    query_llm("こんにちは〜", "gemini")