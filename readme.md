# repo2string

[![PyPI - Version](https://img.shields.io/pypi/v/repo2string)](https://pypi.org/project/repo2string)
[![Python Versions](https://img.shields.io/pypi/pyversions/repo2string)](https://pypi.org/project/repo2string/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/repo2string)](https://pepy.tech/project/repo2string)
[![CI](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml/badge.svg)](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/szulcmaciej/repo2string/branch/master/graph/badge.svg)](https://codecov.io/gh/szulcmaciej/repo2string)

## TLDR: "Help! ChatGPT needs to see my code!"
Yeet your entire codebase into clipboard:
```bash
pip install repo2string
cd your/project/path
r2s  # Yoink! Your entire codebase is now in your clipboard 📋
```

Token limit got you down? Cherry-pick your files:
```bash
r2s -s  # Opens a nice UI for file selection 🎯
```

---

**repo2string** is a tool that helps you prepare your codebase for large language models (LLMs) like ChatGPT. In CLI mode, it automatically processes all relevant files in your project, excluding common build artifacts and respecting `.gitignore`. For more control, the file selection UI lets you interactively select specific files and folders while tracking token counts. Either way, the result is copied to your clipboard, ready to be pasted into your favorite LLM.

Features:

- Recursively traverse directories.
- Skip files listed in `.gitignore` (if present) or skip only `.git` if no `.gitignore` exists.
- Skip common directories like build outputs, dependencies, and IDE files ([see default exclusions](#default-exclusions)).
- Generate and include a file tree, making it easy to understand the codebase structure.
- Include the contents of all non-ignored files.
- Copy all text to your clipboard automatically.
- **Token counting**: Displays the token count of the 
entire prompt (uses the **gpt-4o**/**o1** tokenizer)
- **Verbose mode** (`-v` or `--verbose`): Also prints the token counts per file, 
  sorted from highest to lowest.
- **File selection UI** (`-s` or `--select`): Opens a lightweight web interface to select exactly 
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

## Usage

You can use either the full command `repo2string` or its shorter alias `r2s`.

### CLI Mode

The CLI mode processes all relevant files in the directory, excluding those matched by `.gitignore` and [default exclusions](#default-exclusions). Use this when you want to quickly copy the entire codebase.

```bash
r2s [PATH] [--verbose]
```

- `PATH` is optional; defaults to current directory
- `--verbose` or `-v` shows token counts per file

Example:
```bash
r2s                           # Copy current directory
r2s /path/to/project         # Copy specific directory
r2s -v                     # Show token counts per file
```

### File Selection UI

Need more control? The file selection UI lets you choose specific files and folders while tracking token counts.

```bash
r2s [PATH] --select  # or -s
```

This opens a local web interface where you can:
1. Browse the file tree
2. Select/deselect files and folders
3. Search for specific files
4. Monitor token counts
5. Copy only what you need

![Selection Mode Screenshot](https://raw.githubusercontent.com/szulcmaciej/repo2string/master/.github/images/selection-mode.png)

The UI runs locally - no data leaves your machine, and the server shuts down automatically when you're done.

### Default Exclusions

The tool automatically excludes common directories and files that typically don't need to be included in the LLM context:

- Version control: `.git/`
- Cache directories: `**/.*cache/`, `**/__pycache__/`
- Build outputs: `**/build/`, `**/dist/`, `**/target/`, `**/bin/`, `**/obj/`, `**/out/`
- Dependencies: `**/node_modules/`, `**/vendor/`, `**/package-lock.json`
- IDE files: `**/.idea/`, `**/.vscode/`, `**/.vs/`
- Environment: `**/.env*/`, `**/venv/`

These are in addition to any patterns specified in your `.gitignore` file.



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