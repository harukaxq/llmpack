# LLMPack

A command-line tool for combining code files into a single markdown document, designed for use with LLMs (Large Language Models).

[日本語のREADME](README_ja.md)

## Features

- Generates a directory tree structure
- Combines code files into a single markdown document
- Respects `.gitignore` patterns
- Automatically copies output to clipboard (macOS only)
- Provides rich terminal output with progress indicators

## Installation

### Using Homebrew (macOS/Linux)

```bash
# Install from Homebrew tap
brew tap harukaxq/tools
brew install llmpack
```

### From Source

```bash
# Clone the repository
git clone https://github.com/harukaxq/llmpack.git
cd llmpack

# Install in development mode
pip install -e .
```

## Usage

Run the `llmpack` command in your project directory:

```bash
# Basic usage
llmpack

# With custom output file
llmpack -o output.md

# Add a prefix to each file
llmpack -p "Your prefix text here"

# Enable verbose output
llmpack -v

# Disable clipboard copy
llmpack --no-clipboard
```

## Options

- `-p, --prefix`: Text to add at the beginning of each file
- `-o, --output`: Output file path (default: `.llmpack_files.md`)
- `-v, --verbose`: Enable verbose output
- `--no-clipboard`: Disable copying to clipboard

## Output Format

The generated markdown file includes:

1. Directory structure
2. Contents of `README.md`, `package.json`, and `pyproject.toml` (if they exist)
3. Contents of all code files (with supported extensions)

Each file is formatted as:

```markdown
# path/to/file.ext
<content>
File contents here...
</content>
```

## Supported File Extensions

LLMPack supports a wide range of file extensions, including:

- Web: `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.less`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`
- Web frameworks: `.svelte`, `.vue`, `.prisma`
- Python: `.py`
- Configuration: `.json`, `.yml`, `.yaml`, `.toml`
- And many more...

## License

MIT
