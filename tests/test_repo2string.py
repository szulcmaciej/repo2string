import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from repo2string.cli import count_tokens, get_files_content, main
from repo2string.scan import get_included_files


def test_get_files_content_basic():
    """Test basic functionality with a simple file structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
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
    """Test behavior when no .gitignore exists."""
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
    """Test handling of binary files."""
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


def test_get_files_content_empty_directory():
    """Test handling of empty directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create empty subdirectories
        (test_dir / "empty1").mkdir()
        (test_dir / "empty2").mkdir()

        # Test file collection
        files_data, content = get_files_content(str(test_dir))

        # Assertions
        assert len(files_data) == 0
        assert "File tree:" in content
        assert "File contents:" in content


def test_get_files_content_nested_structure():
    """Test handling of deeply nested directory structures."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create nested structure
        nested_dir = test_dir / "a" / "b" / "c" / "d"
        nested_dir.mkdir(parents=True)

        # Create files at different levels
        (test_dir / "root.txt").write_text("root")
        (test_dir / "a" / "a.txt").write_text("level 1")
        (test_dir / "a" / "b" / "b.txt").write_text("level 2")
        (nested_dir / "d.txt").write_text("level 4")

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Assertions
        assert "root.txt" in content
        assert "a.txt" in content
        assert "b.txt" in content
        assert "d.txt" in content
        assert "root" in content
        assert "level 1" in content
        assert "level 2" in content
        assert "level 4" in content


def test_get_files_content_special_characters():
    """Test handling of files with special characters in names and content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create files with special characters in names
        (test_dir / "spaces in name.txt").write_text("normal content")
        (test_dir / "unicode-⭐️.txt").write_text("unicode content")
        (test_dir / "symbols-#@!.txt").write_text("symbols")

        # Create file with special content
        (test_dir / "special.txt").write_text("Unicode: ⭐️\nTabs:\t\tSpaces    \nNewlines\n\n")

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Assertions
        assert "spaces in name.txt" in content
        assert "unicode-⭐️.txt" in content
        assert "symbols-#@!.txt" in content
        assert "Unicode: ⭐️" in content
        assert "Tabs:" in content
        assert "Newlines" in content


def test_get_files_content_symlinks():
    """Test handling of symbolic links."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create a real file
        real_file = test_dir / "real.txt"
        real_file.write_text("real content")

        # Create a symlink to the file
        link_file = test_dir / "link.txt"
        os.symlink(real_file, link_file)

        # Create a broken symlink
        broken_link = test_dir / "broken.txt"
        os.symlink(test_dir / "nonexistent.txt", broken_link)

        # Test file collection
        _, content = get_files_content(str(test_dir))

        # Assertions
        assert "real.txt" in content
        assert "real content" in content
        # Symlinks should be followed
        assert "link.txt" in content
        # Broken symlinks should be ignored
        assert "broken.txt" not in content


def test_token_counting_with_tiktoken():
    """Test token counting with tiktoken."""
    text = "Hello, world!"
    assert count_tokens(text) > 0


def test_token_counting_fallback():
    """Test fallback token counting when tiktoken is not available."""
    # Simulate tiktoken not being available
    with patch.dict(sys.modules, {"tiktoken": None}):
        # Re-import to trigger the fallback
        from importlib import reload

        import repo2string.cli

        reload(repo2string.cli)

        text = "Hello, world!"
        # Fallback should count words
        assert repo2string.cli.count_tokens(text) == 2


def test_cli_main(capsys):
    """Test CLI functionality in both normal and verbose modes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create test files
        test_file1 = test_dir / "test1.py"
        test_file1.write_text("print('hello')")
        test_file2 = test_dir / "test2.py"
        test_file2.write_text("print('world')")

        # Test CLI with verbose mode
        with patch("sys.argv", ["repo2string", str(test_dir), "--verbose"]):
            with patch("pyperclip.copy") as mock_copy:
                main()
                captured = capsys.readouterr()

                # Check if files were processed
                assert "test1.py" in captured.out
                assert "test2.py" in captured.out
                assert "token" in captured.out.lower()
                assert mock_copy.called

        # Test CLI without verbose mode
        with patch("sys.argv", ["repo2string", str(test_dir)]):
            with patch("pyperclip.copy") as mock_copy:
                main()
                captured = capsys.readouterr()

                # Check basic output
                assert "copied to your clipboard" in captured.out
                assert mock_copy.called


def test_cli_main_nonexistent_path(capsys):
    """Test CLI behavior with nonexistent path."""
    with patch("sys.argv", ["repo2string", "/nonexistent/path"]):
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "Error" in captured.err
        assert "/nonexistent/path" in captured.err


def test_env_file_exclusion():
    """Test that .env files are properly excluded."""
    files = get_included_files(".")

    # Convert all paths to lowercase for case-insensitive comparison
    file_paths = [rel_path.lower() for _, rel_path, _, _ in files]

    # Verify .env file is not included
    assert "tests/.env" not in file_paths
    assert ".env" not in file_paths

    # Also verify no file path contains .env anywhere (like .env.local, .env.test, etc)
    assert not any(".env" in path for path in file_paths)


def test_token_counting_with_special_tokens():
    """Test token counting with text containing special tiktoken tokens."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)

        # Create a file with the special token
        test_file = test_dir / "test.txt"
        test_file.write_text("Here is some text with <|endoftext|> special token")

        # This should not raise an error
        files = get_included_files(str(test_dir))
        assert len(files) == 1
        assert files[0][3] > 0  # token count should be positive
