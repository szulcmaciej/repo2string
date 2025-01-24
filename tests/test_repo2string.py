import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from repo2string.cli import count_tokens, get_files_content, main


def test_get_files_content_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file structure
        test_dir = Path(tmpdir)

        # Create a test file
        test_file = test_dir / "test.py"
        test_file.write_text("print('hello')")

        # Create a .gitignore
        gitignore = test_dir / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n")

        # Create an ignored file
        ignored_file = test_dir / "test.pyc"
        ignored_file.write_text("should be ignored")

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Basic assertions
        assert "test.py" in content
        assert "print('hello')" in content
        assert "should be ignored" not in content


def test_get_files_content_without_gitignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create a test file
        test_file = test_dir / "test.py"
        test_file.write_text("print('hello')")

        # Create a .git directory that should be ignored
        git_dir = test_dir / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("git config")

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Assertions
        assert "test.py" in content
        assert "print('hello')" in content
        assert "git config" not in content


def test_get_files_content_binary_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create a text file
        test_file = test_dir / "test.py"
        test_file.write_text("print('hello')")

        # Create a binary file
        binary_file = test_dir / "binary.bin"
        binary_file.write_bytes(bytes([0x89, 0x50, 0x4E, 0x47]))  # PNG magic numbers

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Assertions
        assert "test.py" in content
        assert "print('hello')" in content
        assert "binary.bin" not in content


def test_token_counting_with_tiktoken():
    text = "Hello, world!"
    assert count_tokens(text) > 0


def test_token_counting_fallback():
    # Simulate tiktoken not being available
    with patch.dict(sys.modules, {'tiktoken': None}):
        # Re-import to trigger the fallback
        from importlib import reload
        import repo2string.cli
        reload(repo2string.cli)

        text = "Hello, world!"
        # Fallback should count words
        assert repo2string.cli.count_tokens(text) == 2


def test_cli_main(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create test files
        test_file1 = test_dir / "test1.py"
        test_file1.write_text("print('hello')")
        test_file2 = test_dir / "test2.py"
        test_file2.write_text("print('world')")

        # Test CLI with verbose mode
        with patch('sys.argv', ['repo2string', str(test_dir), '--verbose']):
            with patch('pyperclip.copy') as mock_copy:
                main()
                captured = capsys.readouterr()

                # Check if files were processed
                assert "test1.py" in captured.out
                assert "test2.py" in captured.out
                assert "token" in captured.out.lower()
                assert mock_copy.called

        # Test CLI without verbose mode
        with patch('sys.argv', ['repo2string', str(test_dir)]):
            with patch('pyperclip.copy') as mock_copy:
                main()
                captured = capsys.readouterr()

                # Check basic output
                assert "copied to your clipboard" in captured.out
                assert mock_copy.called
