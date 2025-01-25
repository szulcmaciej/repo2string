"""
A tool to convert a repository's tracked files into a single text for LLM context.
See cli.py for main functionality.
"""

from repo2string.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    import sys

    sys.exit(main())
