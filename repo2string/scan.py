import os

from pathspec import PathSpec

# Common patterns to ignore across all languages/frameworks
DEFAULT_IGNORE_PATTERNS = [
    ".git/",  # Git
    "**/.*cache/",  # Various cache directories (.pytest_cache, .ruff_cache, etc.)
    "**/__pycache__/",  # Python cache
    "**/node_modules/",  # Node.js
    "**/build/",  # Common build directories
    "**/dist/",  # Distribution directories
    "**/target/",  # Rust, Maven
    "**/bin/",  # Binary directories
    "**/obj/",  # .NET, C#
    "**/out/",  # Java, Kotlin
    "**/.idea/",  # JetBrains IDEs
    "**/.vscode/",  # VS Code
    "**/.vs/",  # Visual Studio
    "**/vendor/",  # PHP, Go
    "**/.env*",  # Environment files and directories
    "**/venv/",  # Python virtual environments
    "**/package-lock.json",  # Node.js lock file (package.json has enough context)
]

try:
    import tiktoken

    ENCODER = tiktoken.encoding_for_model("gpt-4")

    def count_tokens(text):
        """Count tokens in text using tiktoken, treating special tokens as normal text."""
        # Treat special tokens as normal text
        return len(ENCODER.encode(text, disallowed_special=()))
except ImportError:
    # Fallback to a simple approximation if tiktoken is not available
    def count_tokens(text):
        """Count tokens by splitting on whitespace (fallback method)."""
        return len(text.split())


def get_included_files(path="."):
    """
    Return a list of (absolute_path, relative_path, content, token_count).
    By default, it ignores any patterns from .gitignore plus some defaults.
    """
    abs_path = os.path.abspath(path)
    gitignore_path = os.path.join(abs_path, ".gitignore")

    patterns = DEFAULT_IGNORE_PATTERNS.copy()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns.extend(f.readlines())

    spec = PathSpec.from_lines("gitwildmatch", patterns)

    result = []
    for root, _, files in os.walk(abs_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, abs_path)
            if spec.match_file(rel_path):
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as rf:
                    text = rf.read()
                tokens = count_tokens(text)
                result.append((full_path, rel_path, text, tokens))
            except (UnicodeDecodeError, IOError):
                # binary or unreadable file
                continue

    return result


def get_files_content(path="."):
    """
    Original function that returns (files_data, big_string).
    files_data is list of (absolute_path, file_text).
    big_string is the combined file tree + contents.
    """
    included = get_included_files(path)
    files_data = [(x[0], x[2]) for x in included]
    return files_data, assemble_text(files_data)


def assemble_text(files_data):
    """Assemble the final text from file data."""
    parts = []
    parts.append("File tree:")
    for file_path, _ in files_data:
        parts.append(file_path)

    parts.append("\nFile contents:")
    for file_path, content in files_data:
        parts.append(f"\n--- {file_path} ---\n")
        parts.append(content)

    return "\n".join(parts)
