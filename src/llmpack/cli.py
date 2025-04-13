#!/usr/bin/env python3
"""
LLMPack - Tool for combining code files into a single document.

This module provides functionality to:
1. Generate a directory tree structure
2. Combine code files into a single markdown document
3. Copy the result to clipboard (macOS only)
"""
import os
import subprocess
import argparse
from pathlib import Path
import io
import logging
import sys
from typing import List, Tuple, Optional

import pathspec
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize rich console
console = Console()

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_path=False)]
)
logger = logging.getLogger("llmpack")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level based on verbosity."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def load_gitignore_patterns() -> List[Tuple[Path, str]]:
    """
    Load all .gitignore files in the project and return directory-specific patterns.
    
    Returns:
        List of tuples containing (directory_path, gitignore_content)
    """
    gitignore_data = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Loading .gitignore patterns..."),
        transient=True,
    ) as progress:
        task = progress.add_task("Scanning", total=None)
        
        for root, _, files in os.walk("."):
            if ".gitignore" in files:
                root_path = Path(root).resolve()
                gitignore_path = root_path / ".gitignore"
                
                try:
                    with gitignore_path.open("r", encoding="utf-8") as f:
                        content = f.read()
                        gitignore_data.append((root_path, content))
                        logger.debug(f"Loaded .gitignore: {gitignore_path}")
                except Exception as e:
                    logger.error(f"Error reading .gitignore {gitignore_path}: {e}")
        
        progress.update(task, completed=True)
    
    logger.debug(f"Loaded {len(gitignore_data)} .gitignore files")
    return gitignore_data


def should_ignore_file(file_path: Path, gitignore_data: List[Tuple[Path, str]]) -> bool:
    """
    Check if a file should be ignored based on .gitignore patterns.
    
    Args:
        file_path: Path to the file to check
        gitignore_data: List of (directory_path, gitignore_content) tuples
        
    Returns:
        True if the file should be ignored, False otherwise
    """
    abs_file_path = file_path.resolve()
    
    for gitignore_dir, gitignore_content in gitignore_data:
        try:
            # Calculate relative path (will raise ValueError if file is not under this directory)
            rel_path = abs_file_path.relative_to(gitignore_dir)
            
            # Parse .gitignore patterns
            patterns = [line.strip() for line in gitignore_content.splitlines() 
                       if line.strip() and not line.strip().startswith('#')]
            
            # Match patterns
            spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            if spec.match_file(str(rel_path)):
                logger.debug(f"Ignoring: {file_path} (matched by {gitignore_dir}/.gitignore)")
                return True
        except ValueError:
            # File is not under this directory, continue to next gitignore
            continue
    
    return False


def generate_tree(gitignore_data: List[Tuple[Path, str]]) -> str:
    """
    Generate a directory tree structure, respecting .gitignore patterns.
    
    Args:
        gitignore_data: List of (directory_path, gitignore_content) tuples
        
    Returns:
        String containing the tree structure in markdown format
    """
    logger.info("Generating directory tree...")
    
    # Directories to exclude
    exclude_dirs = {"node_modules", ".venv", "build", "dist", "Pods", ".git"}
    
    # Buffer for tree output
    tree_buffer = io.StringIO()
    tree_buffer.write("# Directory Structure\n<content>\n")
    
    # Start from root directory
    root_path = Path(".")
    
    def print_tree(directory: Path, prefix: str = "", is_last: bool = True, level: int = 0) -> None:
        """Recursively print directory tree."""
        # Get directory name
        dir_name = directory.name if level > 0 else "."
        
        # Skip excluded directories
        if dir_name in exclude_dirs or (level > 0 and should_ignore_file(directory, gitignore_data)):
            return
        
        # Print directory name
        connector = "└── " if is_last else "├── "
        tree_buffer.write(f"{prefix}{connector}{dir_name}/\n")
        
        # Get subdirectories and files
        items = []
        try:
            # Get directories and files separately
            dirs = [d for d in directory.iterdir() if d.is_dir() and d.name not in exclude_dirs]
            files = [f for f in directory.iterdir() if f.is_file()]
            
            # Sort by name
            dirs.sort()
            files.sort()
            
            # Directories first, then files
            items = dirs + files
        except PermissionError:
            tree_buffer.write(f"{prefix}    └── (Permission denied)\n")
            return
        
        # Process each item
        for i, item in enumerate(items):
            # Check if this is the last item
            is_last_item = i == len(items) - 1
            
            # Calculate next prefix
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            # Process directories recursively
            if item.is_dir():
                print_tree(item, next_prefix, is_last_item, level + 1)
            else:
                # Skip files that match .gitignore patterns
                if should_ignore_file(item, gitignore_data):
                    continue
                
                # Print file name
                connector = "└── " if is_last_item else "├── "
                tree_buffer.write(f"{prefix}{connector}{item.name}\n")
    
    # Generate tree
    print_tree(root_path)
    
    tree_buffer.write("</content>\n")
    return tree_buffer.getvalue()


def combine_files(gitignore_data: List[Tuple[Path, str]], output_path: Path, prefix: Optional[str] = None) -> int:
    """
    Combine code files into a single markdown document.
    
    Args:
        gitignore_data: List of (directory_path, gitignore_content) tuples
        output_path: Path to output file
        prefix: Optional text to add at the beginning of each file
        
    Returns:
        Total character count of the generated file
    """
    logger.info("Combining code files...")
    
    # Create or overwrite output file
    with output_path.open("w", encoding="utf-8") as outf:
        # Add prefix if provided
        if prefix:
            outf.write(f"{prefix}\n\n")
        
        # Add directory tree
        tree_content = generate_tree(gitignore_data)
        outf.write(f"\n{tree_content}\n")
        
        # Add README.md
        readme_file = Path("README.md")
        if readme_file.is_file():
            outf.write("# README.md\n")
            outf.write(f"<content>\n{readme_file.read_text(encoding='utf-8')}\n</content>\n")

        # Add package.json if exists
        package_file = Path("package.json")
        if package_file.is_file():
            outf.write("\n\n# package.json\n")
            outf.write(f"<content>\n{package_file.read_text(encoding='utf-8')}\n</content>\n")

        # Add pyproject.toml if exists
        pyproject_file = Path("pyproject.toml")
        if pyproject_file.is_file():
            outf.write("\n\n# pyproject.toml\n")
            outf.write(f"<content>\n{pyproject_file.read_text(encoding='utf-8')}\n</content>\n")

    # Valid file extensions to include
    valid_extensions = {
        # HTML/Web
        ".html", ".htm",
        
        # JavaScript/TypeScript
        ".js", ".jsx", ".mjs", ".cjs",
        ".ts", ".tsx", ".d.ts",
        
        # Web frameworks
        ".svelte", ".vue", ".prisma",
        
        # Stylesheets
        ".css", ".scss", ".sass", ".less",
        
        # Python
        ".py",
        
        # Data/config files
        ".json", ".yml", ".yaml", ".toml",
        
        # Java/Kotlin/Android
        ".java", ".kt", ".xml", ".gradle",
        
        # C/C++/C#
        ".c", ".cpp", ".cc", ".h", ".hpp", ".cs",
        
        # Other programming languages
        ".php", ".rb", ".go", ".rs", ".dart",
        
        # Markdown/documentation
        ".md", ".markdown", ".rst",
        
        # Database
        ".sql", ".graphql", ".gql",
        
        # iOS/macOS
        ".swift", ".m", ".storyboard", ".xib", ".pbxproj", ".plist"
    }

    # Directories to exclude
    exclude_dirs = {"node_modules", ".venv", "build", "dist", "Pods", ".git"}
    
    # Process files
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Processing files..."),
    ) as progress:
        task = progress.add_task("Processing", total=None)
        
        for root, dirs, files in os.walk("."):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip files with invalid extensions
                if file_path.suffix not in valid_extensions:
                    continue
                
                try:
                    rel_path = file_path.resolve().relative_to(Path(".").resolve())
                except ValueError:
                    rel_path = file_path

                # Skip files that match .gitignore patterns
                if should_ignore_file(file_path, gitignore_data):
                    logger.debug(f"Ignoring file: {file_path}")
                    continue

                try:
                    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        
                        # Skip files with more than 1000 lines
                        if line_count > 1000:
                            with output_path.open("a", encoding="utf-8") as outf:
                                outf.write(f"\n\n# {file_path}\n")
                                outf.write(f"<skipped - {line_count} lines (exceeds 1000 line limit)>\n")
                            continue
                        
                        # Add file content
                        content = "".join(lines)
                        with output_path.open("a", encoding="utf-8") as outf:
                            outf.write(f"\n\n# {file_path}\n")
                            if prefix:
                                outf.write(f"<content>\n{prefix}\n\n{content}\n</content>\n")
                            else:
                                outf.write(f"<content>\n{content}\n</content>\n")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
        
        progress.update(task, completed=True)
    
    # Get file size
    char_count = len(output_path.read_text(encoding="utf-8"))
    return char_count


def copy_to_clipboard(file_path: Path) -> bool:
    """
    Copy file contents to clipboard (macOS only).
    
    Args:
        file_path: Path to the file to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()
        
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(content.encode("utf-8"))
        return True
    except Exception as e:
        logger.error(f"Error copying to clipboard: {e}")
        return False


def init_command():
    """Handle the initialization command to set up LLM and API keys."""
    console.print("[bold blue]LLMPack Initialization[/]")
    console.print("Let's set up your LLM provider and API keys.")
    
    # LLM provider selection
    providers = ["gemini", "openai", "anthropic", "ollama"]
    console.print("\n[bold]Select LLM provider (default: Gemini recommended for large token capacity):[/]")
    for i, provider in enumerate(providers, 1):
        console.print(f"{i}. {provider.capitalize()}{' [recommended]' if provider == 'gemini' else ''}")
    
    choice = input("Enter choice (1-4, default 1): ").strip() or "1"
    try:
        provider_idx = int(choice) - 1
        selected_provider = providers[provider_idx] if 0 <= provider_idx < len(providers) else "gemini"
    except ValueError:
        selected_provider = "gemini"
    
    from llmpack.settings import set_setting, set_api_key
    from llmpack.model_manager import get_models_for_provider, get_default_model_for_provider
    
    set_setting("llm_provider", selected_provider)
    console.print(f"[bold green]✓[/] LLM provider set to {selected_provider.capitalize()}")
    
    # Model selection
    models = get_models_for_provider(selected_provider)
    if models:
        console.print("\n[bold]Select model:[/]")
        for i, model in enumerate(models, 1):
            console.print(f"{i}. {model['name']} - {model['description']}")
        
        max_choice = len(models)
        choice = input(f"Enter choice (1-{max_choice}, default 1): ").strip() or "1"
        try:
            model_idx = int(choice) - 1
            selected_model = models[model_idx]["id"] if 0 <= model_idx < len(models) else models[0]["id"]
        except ValueError:
            selected_model = models[0]["id"]
        
        set_setting("llm_model", selected_model)
        console.print(f"[bold green]✓[/] Model set to {selected_model}")
    else:
        console.print(f"[bold yellow]⚠[/] No models found for {selected_provider}. Using default.")
        default_model = get_default_model_for_provider(selected_provider)
        if default_model:
            set_setting("llm_model", default_model)
    
    # API key input (not required for Ollama)
    if selected_provider != "ollama":
        # Check if API key exists in environment variable
        env_var_name = f"{selected_provider.upper()}_API_KEY"
        env_api_key = os.environ.get(env_var_name)
        
        if env_api_key:
            console.print(f"[bold green]✓[/] API key found in environment variable {env_var_name}")
            console.print("You can leave the input blank to use the environment variable.")
        
        api_key = input(f"Enter API key for {selected_provider.capitalize()} (leave blank to use environment variable or skip): ").strip()
        if api_key:
            set_api_key(selected_provider, api_key)
            console.print(f"[bold green]✓[/] API key for {selected_provider.capitalize()} saved")
        else:
            if env_api_key:
                console.print(f"[bold green]✓[/] Using API key from environment variable {env_var_name}")
            else:
                console.print(f"[bold yellow]⚠[/] API key for {selected_provider.capitalize()} not provided. You can set it later with 'llmpack set-api-key'.")
    
    # Language selection
    language = input("Select language (en/ja, default en): ").strip().lower() or "en"
    language = language if language in ["en", "ja"] else "en"
    set_setting("language", language)
    console.print(f"[bold green]✓[/] Language set to {language}")
    
    console.print("\n[bold green]✓[/] Initialization complete! You can now use 'llmpack query' to interact with the LLM.")

def set_api_key_command():
    """Handle setting API keys for LLM providers."""
    console.print("[bold blue]Set API Key for LLM Provider[/]")
    providers = ["openai", "anthropic", "gemini"]
    console.print("[bold]Select provider:[/]")
    for i, provider in enumerate(providers, 1):
        console.print(f"{i}. {provider.capitalize()}")
    
    choice = input("Enter choice (1-3): ").strip()
    try:
        provider_idx = int(choice) - 1
        selected_provider = providers[provider_idx] if 0 <= provider_idx < len(providers) else None
    except ValueError:
        selected_provider = None
    
    if selected_provider:
        # Check if API key exists in environment variable
        env_var_name = f"{selected_provider.upper()}_API_KEY"
        env_api_key = os.environ.get(env_var_name)
        
        if env_api_key:
            console.print(f"[bold green]✓[/] API key found in environment variable {env_var_name}")
            console.print("You can leave the input blank to use the environment variable.")
        
        api_key = input(f"Enter API key for {selected_provider.capitalize()} (leave blank to use environment variable): ").strip()
        
        if api_key:
            from llmpack.settings import set_api_key
            set_api_key(selected_provider, api_key)
            console.print(f"[bold green]✓[/] API key for {selected_provider.capitalize()} updated")
        else:
            if env_api_key:
                console.print(f"[bold green]✓[/] Using API key from environment variable {env_var_name}")
            else:
                console.print("[bold red]✗[/] API key cannot be empty and no environment variable found")
    else:
        console.print("[bold red]✗[/] Invalid provider selection")

def set_model_command():
    """Handle setting the model for the current LLM provider."""
    from llmpack.settings import get_setting, set_setting
    from llmpack.model_manager import get_models_for_provider
    
    console.print("[bold blue]Set Model for LLM Provider[/]")
    
    # Get current provider
    current_provider = get_setting("llm_provider")
    if not current_provider:
        console.print("[bold red]✗[/] No LLM provider set. Please run 'llmpack init' first.")
        return
    
    console.print(f"[bold]Current provider:[/] {current_provider.capitalize()}")
    
    # Get models for the provider
    models = get_models_for_provider(current_provider)
    if not models:
        console.print(f"[bold red]✗[/] No models found for {current_provider}.")
        return
    
    # Display available models
    console.print("\n[bold]Available models:[/]")
    for i, model in enumerate(models, 1):
        console.print(f"{i}. {model['name']} - {model['description']}")
    
    # Get user choice
    max_choice = len(models)
    choice = input(f"Enter choice (1-{max_choice}): ").strip()
    try:
        model_idx = int(choice) - 1
        if 0 <= model_idx < len(models):
            selected_model = models[model_idx]["id"]
            set_setting("llm_model", selected_model)
            console.print(f"[bold green]✓[/] Model set to {selected_model}")
        else:
            console.print("[bold red]✗[/] Invalid selection")
    except ValueError:
        console.print("[bold red]✗[/] Invalid input")

def main() -> None:
    """Main entry point for the llmpack command."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="LLMPack - Tool for combining code files or querying LLMs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Parser for the default combine command
    combine_parser = subparsers.add_parser("combine", help="Combine code files into a single markdown document", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    combine_parser.add_argument("-p", "--prefix", help="Text to add at the beginning of each file")
    combine_parser.add_argument("-o", "--output", help="Output file path", default=".llmpack_files.md")
    combine_parser.add_argument("--no-clipboard", help="Disable copying to clipboard", action="store_true")
    
    # Parser for the query command
    query_parser = subparsers.add_parser("query", help="Query an LLM with a task", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    query_parser.add_argument("task", help="Task or question for the LLM", nargs='?', default=None)
    query_parser.add_argument("--provider", help="LLM provider to use (overrides default)", choices=["openai", "anthropic", "gemini", "ollama"])
    query_parser.add_argument("--model", help="LLM model to use (overrides default)")
    query_parser.add_argument("--lang", help="Language for response (overrides default)", choices=["en", "ja"])
    query_parser.add_argument("-o", "--output", help="Output file path for query result", default=".llmpack_result")
    query_parser.add_argument("--no-clipboard", help="Disable copying to clipboard", action="store_true")
    
    # Parser for the init command
    subparsers.add_parser("init", help="Initialize LLMPack settings and API keys")
    
    # Parser for the set-api-key command
    subparsers.add_parser("set-api-key", help="Set or update API key for an LLM provider")
    
    # Parser for the set-model command
    subparsers.add_parser("set-model", help="Set or update the model for the current LLM provider")
    
    # Common arguments
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    if args.command == "init":
        init_command()
        return
    
    if args.command == "set-api-key":
        set_api_key_command()
        return
    
    if args.command == "set-model":
        set_model_command()
        return
    
    if args.command == "query":
        if not args.task:
            args.task = input("Enter your task or question for the LLM: ").strip()
        if not args.task:
            console.print("[bold red]✗[/] Task cannot be empty")
            sys.exit(1)
        
        from llmpack.llm import query_llm
        from llmpack.settings import set_setting
        
        if args.lang:
            set_setting("language", args.lang)
        
        if args.model:
            set_setting("llm_model", args.model)
        
        result = query_llm(args.task, args.provider)
        if result:
            output_path = Path(args.output)
            with output_path.open("w", encoding="utf-8") as outf:
                outf.write(result)
            
            console.print(f"[bold green]✓[/] Result saved to {output_path}")
            console.print("\n[bold]LLM Response:[/]\n")
            console.print(result)
            if not args.no_clipboard and sys.platform == "darwin":
                if copy_to_clipboard(output_path):
                    console.print(f"[bold green]✓[/] Result copied to clipboard")
                else:
                    console.print("[bold red]✗[/] Failed to copy to clipboard")
            
        else:
            console.print("[bold red]✗[/] Failed to get response from LLM")
            sys.exit(1)
        return
    
    # Default to combine mode if no command specified
    if not args.command:
        args.command = "combine"
        output_path = Path(".llmpack_files.md")  # Default output path
        
        try:
            # Load .gitignore patterns
            gitignore_data = load_gitignore_patterns()
            
            # Combine files
            char_count = combine_files(gitignore_data, output_path, getattr(args, 'prefix', None))
            
            # Copy to clipboard if enabled
            if not getattr(args, 'no_clipboard', False) and sys.platform == "darwin":
                if copy_to_clipboard(output_path):
                    console.print(f"[bold green]✓[/] Content copied to clipboard")
                else:
                    console.print("[bold red]✗[/] Failed to copy to clipboard")
            
            # Print summary
            console.print(f"[bold green]✓[/] Created {output_path}")
            console.print(f"[bold]Total characters:[/] {char_count:,}")
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Operation cancelled by user[/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            if args.verbose:
                import traceback
                console.print(traceback.format_exc())
            sys.exit(1)


if __name__ == "__main__":
    main()
