import os
import sys
import argparse

import pyperclip
from pathspec import PathSpec

# Attempt to import tiktoken for real token counting.
# If not available, fall back to a naive approach (word-splitting).
try:
    import tiktoken

    def count_tokens(text, model="gpt-3.5-turbo"):
        # Get the appropriate tokenizer for the given model
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))

except ImportError:
    def count_tokens(text, model="gpt-3.5-turbo"):
        # Fallback: naive token approximation via whitespace splitting
        return len(text.split())

def load_gitignore_patterns(gitignore_path):
    """
    Load patterns from .gitignore file (if it exists),
    returning a PathSpec object. Otherwise, return None.
    """
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        spec = PathSpec.from_lines('gitwildmatch', lines)
        return spec
    return None

def is_ignored(path, spec, root):
    """
    Return True if `path` is matched by the .gitignore spec,
    or if it is the .git directory.
    """
    if os.path.abspath(path).endswith(os.sep + '.git'):
        return True

    if spec is None:
        return False

    relative_path = os.path.relpath(path, root)
    return spec.match_file(relative_path)

def build_file_tree_and_contents(start_path):
    """
    Traverse directory from `start_path`, skipping ignored files/directories.
    Build and return a list of (abs_path, file_content) for each included file.
    """
    start_path = os.path.abspath(start_path)
    gitignore_path = os.path.join(start_path, '.gitignore')
    spec = load_gitignore_patterns(gitignore_path)

    files_data = []  # Will hold tuples of (absolute_path, content)

    for root, dirs, files in os.walk(start_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs
                   if not is_ignored(os.path.join(root, d), spec, start_path)]

        for f in files:
            file_path = os.path.join(root, f)
            if is_ignored(file_path, spec, start_path):
                continue

            abs_path = os.path.abspath(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as ff:
                    content = ff.read()
            except Exception as e:
                content = f"Could not read file ({e})"

            files_data.append((abs_path, content))

    return files_data

def assemble_text(files_data):
    """
    Given a list of (abs_path, file_content), assemble:
    1) A file tree listing (absolute paths),
    2) All contents.

    Returns the final big string.
    """
    file_tree_lines = [path for (path, _) in files_data]

    file_tree_text = "FILE TREE (absolute paths):\n" + "\n".join(file_tree_lines)

    contents_parts = []
    for path, content in files_data:
        contents_parts.append(f"\n---[ {path} ]---\n{content}")

    contents_text = "FILE CONTENTS:\n" + "\n".join(contents_parts)

    final_text = file_tree_text + "\n\n" + contents_text
    return final_text

def main():
    parser = argparse.ArgumentParser(
        description="Turn a repo/folder into a single text for LLM context (with token counts)."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the folder to process (default current directory)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print token counts per file in descending order."
    )

    args = parser.parse_args()
    start_path = os.path.abspath(args.path)

    if not os.path.exists(start_path):
        print(f"Error: Path '{start_path}' does not exist.")
        sys.exit(1)

    print(f"Reading files from: {start_path} ...")
    files_data = build_file_tree_and_contents(start_path)

    # Compute token counts per file
    file_token_info = []
    for abs_path, content in files_data:
        num_tokens = count_tokens(content)
        file_token_info.append((abs_path, content, num_tokens))

    # Sort by token count descending if verbose
    if args.verbose:
        file_token_info.sort(key=lambda x: x[2], reverse=True)

    # Build the final text
    # (Re-assemble in the same order they were discovered, ignoring the sorting.)
    # But if we want the final text in the *original* discovery order, 
    # we just re-use `files_data`.
    final_text = assemble_text(files_data)

    # Count total tokens of the entire final text
    total_tokens = count_tokens(final_text)

    # Copy to clipboard
    pyperclip.copy(final_text)
    print(f"Repository contents have been copied to your clipboard!")
    print(f"Total tokens for the entire prompt: {total_tokens}")

    if args.verbose:
        print("\nPer-file token counts (descending):")
        for abs_path, content, tok_count in file_token_info:
            print(f"{tok_count:>8}  {abs_path}")