# repo2string

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

```bash
git clone https://github.com/szulcmaciej/repo2string
cd repo2string
pip install .
```

*(Make sure [pyperclip](https://pypi.org/project/pyperclip/) and [tiktoken](https://pypi.org/project/tiktoken/) are installed; they’re declared as dependencies in `pyproject.toml`.)*

## Usage

```bash
repo2string [PATH] [--verbose]
```

- `PATH` is optional; defaults to `.` (current directory).
- `--verbose` or `-v` prints a token-count summary per file (descending).

Example:

```bash
repo2string /path/to/myproject --verbose
```

You will see console output summarizing the total token count, plus a per-file token breakdown if in verbose mode. The entire text is copied to your clipboard.

Now you can paste the combined repo data into ChatGPT or another LLM interface to work on your code with maximum context.

## License

[MIT](https://opensource.org/licenses/MIT)