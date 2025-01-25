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


def test_index_route(client):
    """Test that the main UI page is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data
    # Check for key UI elements
    assert b"repo2string" in response.data.lower()
    assert b"copy to clipboard" in response.data.lower()


def test_get_tree_route(client):
    """Test the file tree endpoint."""
    response = client.get("/get_tree")
    assert response.status_code == 200
    data = response.get_json()
    assert "tree" in data
    assert isinstance(data["tree"], list)
    # Verify some expected files are present
    tree_str = str(data["tree"]).lower()  # Case-insensitive comparison
    assert "pyproject.toml" in tree_str
    assert "readme.md" in tree_str


def test_get_tokens_empty_selection(client):
    """Test token counting with no files selected."""
    response = client.post("/get_tokens", json={"selected_files": []})
    assert response.status_code == 200
    data = response.get_json()
    assert "total_tokens" in data
    assert data["total_tokens"] == 0
    assert "token_counts" in data
    assert isinstance(data["token_counts"], dict)
    assert len(data["token_counts"]) == 0


def test_get_tokens_with_files(client):
    """Test token counting with actual files."""
    test_files = [f[1] for f in get_included_files(".")][:2]  # Get first two files
    response = client.post("/get_tokens", json={"selected_files": test_files})
    assert response.status_code == 200
    data = response.get_json()
    assert "total_tokens" in data
    assert data["total_tokens"] > 0
    assert "token_counts" in data
    assert isinstance(data["token_counts"], dict)
    assert len(data["token_counts"]) == len(test_files)
    # Verify each file has a positive token count
    for count in data["token_counts"].values():
        assert count > 0


@patch("repo2string.ui_server.pyperclip")
def test_copy_to_clipboard_route(mock_pyperclip, client):
    """Test the clipboard copy endpoint."""
    test_files = [f[1] for f in get_included_files(".")][:2]  # Get first two files

    response = client.post("/copy_to_clipboard", json={"selected_files": test_files})
    assert response.status_code == 200
    data = response.get_json()
    assert "success" in data
    assert data["success"] is True
    assert "total_tokens" in data
    assert data["total_tokens"] > 0

    # Verify clipboard function was called
    mock_pyperclip.copy.assert_called_once()


def test_error_handling(client):
    """Test error handling for invalid requests."""
    # Test invalid JSON
    response = client.post("/get_tokens", data="invalid json")
    assert response.status_code == 400

    # Test missing required field
    response = client.post("/get_tokens", json={})
    assert response.status_code == 400

    # Test invalid file paths
    response = client.post("/get_tokens", json={"selected_files": ["nonexistent.py"]})
    assert response.status_code == 200  # Should handle gracefully
    data = response.get_json()
    assert data["total_tokens"] == 0
