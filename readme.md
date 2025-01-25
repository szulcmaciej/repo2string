# repo2string

[![PyPI version](https://badge.fury.io/py/repo2string.svg)](https://badge.fury.io/py/repo2string)
[![Python Versions](https://img.shields.io/pypi/pyversions/repo2string)](https://pypi.org/project/repo2string/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/repo2string)](https://pepy.tech/project/repo2string)
[![CI](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml/badge.svg)](https://github.com/szulcmaciej/repo2string/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/szulcmaciej/repo2string/branch/master/graph/badge.svg)](https://codecov.io/gh/szulcmaciej/repo2string)

**repo2string** is a Python package and CLI tool that gathers all files in a repository 
(or any folder), excluding ignored files as specified by a `.gitignore` (if present), 
and concatenates them into a single string. This is useful for copying the entire 
codebase as a context to large language models (LLMs) like ChatGPT.

Features:

- Recursively traverse directories.
- Skip files listed in `.gitignore` (if present) or skip only `.git` if no `.gitignore` exists.
- Generate a file tree (with absolute paths).
- Include the contents of all non-ignored files.
- Copy all text to your clipboard automatically.
- **Token counting**: Displays the token count of the entire prompt. 
- **Verbose mode** (`-v` or `--verbose`): Also prints the token counts per file, 
  sorted from highest to lowest.

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

```bash
repo2string [PATH] [--verbose]
```
Or use the shorter alias:
```bash
r2s [PATH] [--verbose]
```

- `PATH` is optional; defaults to `.` (current directory).
- `--verbose` or `-v` prints a token-count summary per file (descending).

Example:

```bash
repo2string /path/to/myproject --verbose
```

You will see console output summarizing the total token count, plus a per-file token breakdown if in verbose mode. The entire text is copied to your clipboard.

### Default Exclusions

The tool automatically excludes common directories and files that typically don't need to be included in the LLM context:

- Version control: `.git/`
- Cache directories: `**/.*cache/`, `**/__pycache__/`
- Build outputs: `**/build/`, `**/dist/`, `**/target/`, `**/bin/`, `**/obj/`, `**/out/`
- Dependencies: `**/node_modules/`, `**/vendor/`
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

3. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e ".[test]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

The pre-commit hooks will:
- Run Ruff for linting and auto-formatting
- Run pytest to ensure all tests pass
- Block commits if any checks fail

To run tests manually:
```bash
pytest
```

### Release Process

The release process is automated. When you bump the version in `pyproject.toml` and push to the `master` branch:
1. A GitHub Action will detect the version change
2. Create a new release with the version number
3. Generate release notes automatically
4. Publish the package to PyPI

No manual tagging or release creation is needed.

## License

[MIT](https://opensource.org/licenses/MIT)