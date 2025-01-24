import os
import tempfile
from pathlib import Path
import pytest
from repo2string.cli import get_files_content

def test_get_files_content():
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
        content = get_files_content(str(test_dir))
        
        # Basic assertions
        assert "test.py" in content
        assert "print('hello')" in content
        assert "should be ignored" not in content 