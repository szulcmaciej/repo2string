from unittest.mock import patch

import pytest

from repo2string.scan import get_included_files
from repo2string.ui_server import create_app


@pytest.fixture
def app():
    app = create_app(".")
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_pyperclip():
    """Mock pyperclip for all tests to avoid clipboard dependency."""
    with patch("repo2string.ui_server.pyperclip") as mock:
        yield mock


def test_index_route(client):
    """Test that the main UI page is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data
    # Check for key UI elements
    assert b"repo2string" in response.data.lower()
    assert b"copy to clipboard" in response.data.lower()


def test_api_files_route(client):
    """Test the file list endpoint."""
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.get_json()
    assert "files" in data
    assert "basePath" in data
    assert isinstance(data["files"], list)
    # Verify some expected files are present
    files_str = str(data["files"]).lower()  # Case-insensitive comparison
    assert "pyproject.toml" in files_str
    assert "readme.md" in files_str
    # Verify file structure
    for file_info in data["files"]:
        assert "relPath" in file_info
        assert "absPath" in file_info
        assert "tokens" in file_info
        assert isinstance(file_info["tokens"], int)


def test_api_submit(mock_pyperclip, client):
    """Test the submit endpoint."""
    test_files = [f[1] for f in get_included_files(".")][:2]  # Get first two files

    response = client.post("/api/submit", json={"include": test_files})
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "total_tokens" in data
    assert data["total_tokens"] > 0

    # Verify clipboard function was called
    mock_pyperclip.copy.assert_called_once()


def test_error_handling(client):
    """Test error handling for invalid requests."""
    # Test invalid JSON
    response = client.post("/api/submit", data="invalid json")
    assert response.status_code == 400

    # Test empty selection
    response = client.post("/api/submit", json={"include": []})
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_tokens"] == 0

    # Test invalid file paths
    response = client.post("/api/submit", json={"include": ["nonexistent.py"]})
    assert response.status_code == 200  # Should handle gracefully
    data = response.get_json()
    assert data["total_tokens"] == 0
