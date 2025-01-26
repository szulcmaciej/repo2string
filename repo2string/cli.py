import argparse
import os
import sys

import pyperclip
from pathspec import PathSpec

from repo2string.scan import count_tokens


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
        "**/package-lock.json",  # Node.js lock file (package.json has enough context)
    ]
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
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


def run_cli(path, verbose=False):
    """Run in CLI mode"""
    files_data, content = get_files_content(path)
    final_text = assemble_text(files_data)
    total_tokens = count_tokens(final_text)

    if verbose:
        # Show per-file tokens
        file_token_info = []
        lines = final_text.split("\n")
        current_file = None
        current_content = []

        for line in lines:
            if line.startswith("--- ") and line.endswith(" ---"):
                if current_file:
                    file_text = "\n".join(current_content)
                    file_token_info.append((current_file, file_text, count_tokens(file_text)))
                current_file = line[4:-4]
                current_content = []
            elif current_file:
                current_content.append(line)

        if current_file and current_content:
            file_text = "\n".join(current_content)
            file_token_info.append((current_file, file_text, count_tokens(file_text)))

        file_token_info.sort(key=lambda x: x[2], reverse=True)

    pyperclip.copy(final_text)
    print("Repository contents have been copied to your clipboard!")
    print(f"Total tokens for the entire prompt: {total_tokens}")

    if verbose:
        print("\nPer-file token counts (descending):")
        for abs_path, _, tok_count in file_token_info:
            print(f"{tok_count:>8}  {abs_path}")


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
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch a local browser UI instead of printing to the console",
    )
    args = parser.parse_args()

    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # If user wants the UI, launch it and exit
    if args.ui:
        from repo2string.ui_server import run_ui_server

        run_ui_server(args.path)
        sys.exit(0)

    # Otherwise, run the original CLI flow
    run_cli(args.path, args.verbose)


if __name__ == "__main__":
    main()
