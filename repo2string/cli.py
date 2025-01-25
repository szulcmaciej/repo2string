import argparse
import os
import sys

import pyperclip
from pathspec import PathSpec

# Attempt to import tiktoken for real token counting.
try:
    import tiktoken

    ENCODER = tiktoken.encoding_for_model("gpt-4o")

    def count_tokens(text):
        return len(ENCODER.encode(text))
except ImportError:
    # Fallback to a simple approximation if tiktoken is not available
    def count_tokens(text):
        return len(text.split())


def get_files_content(path="."):
    """Get the contents of all tracked files in the repository."""
    # Get absolute path
    abs_path = os.path.abspath(path)

    # Check if .gitignore exists
    gitignore_path = os.path.join(abs_path, ".gitignore")
    # Common patterns to ignore across all languages/frameworks
    patterns = [
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
        "**/.env*/",  # Environment directories
        "**/venv/",  # Python virtual environments
    ]
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            patterns.extend(f.readlines())
    spec = PathSpec.from_lines("gitwildmatch", patterns)

    # Store file data as we discover it
    files_data = []

    # Walk through all files
    for root, _, files in os.walk(abs_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, abs_path)

            # Skip files that match gitignore patterns
            if spec.match_file(rel_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                files_data.append((file_path, content))
            except (UnicodeDecodeError, IOError):
                # Skip binary files or files we can't read
                continue

    return files_data, assemble_text(files_data)


def assemble_text(files_data):
    """Assemble the final text from file data."""
    parts = []

    # First, show the file tree
    parts.append("File tree:")
    for file_path, _ in files_data:
        parts.append(file_path)

    # Then show file contents
    parts.append("\nFile contents:")
    for file_path, content in files_data:
        parts.append(f"\n--- {file_path} ---\n")
        parts.append(content)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a repository's tracked files into a single text for LLM context."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository (defaults to current directory)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show token counts per file",
    )
    args = parser.parse_args()

    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Get the content
    files_data, content = get_files_content(args.path)

    # Count tokens for the entire prompt
    total_tokens = count_tokens(content)

    # If verbose, get per-file token counts
    if args.verbose:
        file_token_info = []
        lines = content.split("\n")
        current_file = None
        current_content = []

        # Parse the content to get per-file information
        for line in lines:
            if line.startswith("--- ") and line.endswith(" ---"):
                if current_file:
                    file_content = "\n".join(current_content)
                    file_token_info.append((current_file, file_content, count_tokens(file_content)))
                current_file = line[4:-4]  # Remove "--- " and " ---"
                current_content = []
            elif current_file:
                current_content.append(line)

        # Don't forget the last file
        if current_file and current_content:
            file_content = "\n".join(current_content)
            file_token_info.append((current_file, file_content, count_tokens(file_content)))

        # Sort by token count (descending)
        file_token_info.sort(key=lambda x: x[2], reverse=True)

    # Build the final text
    # (Re-assemble in the same order they were discovered, ignoring the sorting.)
    # But if we want the final text in the *original* discovery order,
    # we just re-use `files_data`.
    final_text = assemble_text(files_data)

    # Copy to clipboard
    pyperclip.copy(final_text)
    print("Repository contents have been copied to your clipboard!")
    print(f"Total tokens for the entire prompt: {total_tokens}")

    # Print per-file token counts if verbose
    if args.verbose:
        print("\nPer-file token counts (descending):")
        for abs_path, _, tok_count in file_token_info:
            print(f"{tok_count:>8}  {abs_path}")
