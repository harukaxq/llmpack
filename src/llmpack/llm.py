"""
LLMPack LLM - LLM query execution for LLMPack tool.

This module provides functionality to:
1. Initialize and configure LLM providers using LangChain
2. Execute queries with user prompts and predefined instruction templates
3. Handle responses from different LLM providers
"""
import os
from typing import Optional, Dict, Any
import logging
from rich.logging import RichHandler

from langchain_core.language_models import LLM, BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llmpack.settings import get_api_key, get_setting
from llmpack.model_manager import get_default_model_for_provider

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(show_path=False)]
)
logger = logging.getLogger("llmpack.llm")

def initialize_llm(provider: Optional[str] = None) -> Optional[BaseChatModel]:
    """
    Initialize the LLM based on the provider and model specified in settings or passed as argument.
    
    Args:
        provider: Optional provider name to override the setting
        
    Returns:
        Initialized LLM instance or None if initialization fails
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
            return ChatOpenAI(
                model=model,
                api_key=api_key, # type: ignore
                temperature=0.0
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model_name=model,
                api_key=api_key, # type: ignore
                temperature=0.0
            )
        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model,
                api_key=api_key, # type: ignore
                temperature=0.0
            )
        elif provider == "ollama":
            return ChatOllama(
                model=model,
                temperature=0.0
            )
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
    
    # Prepare the prompt template with combined content
    system_message = SystemMessage(content=f"You are a helpful AI assistant. Respond in {language}.")
    human_message = HumanMessage(content=f"{instruction_prompt}\n\n{task}\n\nHere is the combined code from the project:\n\n{combined_content}")
    
    try:
        # Create prompt and chain
        prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        chain = prompt | llm | StrOutputParser()
        
        # Execute query
        logger.info(f"Querying {provider or get_setting('llm_provider')}...")
        response = chain.invoke({})
        return response
    except Exception as e:
        logger.error(f"Error querying LLM: {e}")
        return None
