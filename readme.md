# repo2string

[![PyPI - Version](https://img.shields.io/pypi/v/repo2string)](https://pypi.org/project/repo2string)
[![Python Versions](https://img.shields.io/pypi/pyversions/repo2string)](https://pypi.org/project/repo2string/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/repo2string)](https://pepy.tech/project/repo2string)
[![CI](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml/badge.svg)](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/szulcmaciej/repo2string/branch/master/graph/badge.svg)](https://codecov.io/gh/szulcmaciej/repo2string)

## TLDR: "Help! I need to feed my entire codebase to ChatGPT!"
```bash
pip install repo2string
cd your/project/path
r2s  # That's it! Your entire codebase is now in your clipboard 📋
```

**repo2string** is a tool that helps you prepare your codebase for large language models (LLMs) like ChatGPT. In CLI mode, it automatically processes all relevant files in your project, excluding common build artifacts and respecting `.gitignore`. For more control, the selection mode lets you interactively select specific files and folders while tracking token counts. Either way, the result is copied to your clipboard, ready to be pasted into your favorite LLM.

Features:

- Recursively traverse directories.
- Skip files listed in `.gitignore` (if present) or skip only `.git` if no `.gitignore` exists.
- Skip common directories like build outputs, dependencies, and IDE files ([see default exclusions](#default-exclusions)).
- Generate and include a file tree, making it easy to understand the codebase structure.
- Include the contents of all non-ignored files.
- Copy all text to your clipboard automatically.
- **Token counting**: Displays the token count of the entire prompt. 
- **Verbose mode** (`-v` or `--verbose`): Also prints the token counts per file, 
  sorted from highest to lowest.
- **Selection mode** (`-s` or `--select`): Opens a lightweight web interface to select exactly 
  which files and folders to include.

## Installation

You can install `repo2string` directly from PyPI:

```bash
pip install repo2string
```

Or install from source:

```bash
git clone https://github.com/szulcmaciej/repo2string.git
cd repo2string
pip install .
```

## Usage (CLI Mode)

```bash
repo2string [PATH] [--verbose]
```
Or use the shorter alias:
```bash
r2s [PATH] [--verbose]
```

The CLI mode processes all relevant files in the directory (excluding those matched by `.gitignore` and default exclusions). Use this when you want to quickly copy the entire codebase.

- `PATH` is optional; defaults to `.` (current directory).
- `--verbose` or `-v` prints a token-count summary per file (descending).

Example:

```bash
r2s /path/to/myproject --verbose
```

For example, if you're in your project directory:

```bash
r2s .
# Or simply:
r2s
```

You will see console output summarizing the total token count, plus a per-file token breakdown if in verbose mode. The entire text is copied to your clipboard.

## Usage (Selection Mode)

If you need to select specific files or folders to include:

```bash
r2s [PATH] --select
# Or use the short flag:
r2s [PATH] -s
```

This opens a lightweight web interface in your default browser. The UI runs on a local Flask server - no data ever leaves your machine, and the server automatically shuts down when you're done.

This opens an interactive interface where you can:
1. See a tree view of all files in the repository
2. Select/deselect individual files or entire folders
3. Search for specific files
4. See token counts for each file and selection
5. Copy only the selected files to clipboard

The selection mode is particularly useful when:
- You want to exclude certain files or folders
- You need to stay under a token limit
- You want to focus on specific parts of the codebase

When done, click **"Copy to Clipboard"** to copy the selected files and close the UI.

### Default Exclusions

The tool automatically excludes common directories and files that typically don't need to be included in the LLM context:

- Version control: `.git/`
- Cache directories: `**/.*cache/`, `**/__pycache__/`
- Build outputs: `**/build/`, `**/dist/`, `**/target/`, `**/bin/`, `**/obj/`, `**/out/`
- Dependencies: `**/node_modules/`, `**/vendor/`, `**/package-lock.json`
- IDE files: `**/.idea/`, `**/.vscode/`, `**/.vs/`
- Environment: `**/.env*/`, `**/venv/`

These are in addition to any patterns specified in your `.gitignore` file.

Now you can paste the combined repo data into ChatGPT or another LLM interface to work on your code with maximum context.

## Development Setup

To set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/szulcmaciej/repo2string.git
   cd repo2string
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

To run tests manually:
```bash
pytest
```

### Release Process

The release process is fully automated through a chain of GitHub Actions:

1. When you push to `master`, the CI workflow runs tests and linting
2. If CI passes and the version in `pyproject.toml` was bumped:
   - A new GitHub release is created automatically
   - Release notes are generated from commit messages
3. When the release is published:
   - The package is automatically built and published to PyPI
   - Using trusted publishing for enhanced security

No manual intervention is needed beyond pushing your changes with a version bump.

## License

[MIT](https://opensource.org/licenses/MIT)