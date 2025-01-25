import logging
import os
import signal
import sys
import threading
import webbrowser

import pyperclip
from flask import Flask, jsonify, request, send_from_directory

from repo2string.scan import assemble_text, get_included_files


def create_app(base_path=None):
    """Create and configure the Flask application."""
    # Configure Flask to show minimal output
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *args: None

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    app = Flask(__name__, static_folder=None)  # We'll serve ui.html by a custom route

    # Store path and files in app config
    app.config["BASE_PATH"] = base_path
    app.config["ALL_FILES"] = []
    if base_path:
        app.config["ALL_FILES"] = get_included_files(os.path.abspath(base_path))

    @app.route("/")
    def serve_ui():
        """Serve the single-page app from ui.html in the same directory."""
        dir_path = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(dir_path, "ui.html")

    @app.route("/api/files", methods=["GET"])
    def api_files():
        """Return file tree and token counts."""
        data = []
        for full_path, rel_path, _, tokens in app.config["ALL_FILES"]:
            data.append(
                {
                    "relPath": rel_path,
                    "absPath": full_path,
                    "tokens": tokens,
                }
            )
        return jsonify({"files": data, "basePath": app.config["BASE_PATH"]})

    @app.route("/api/submit", methods=["POST"])
    def api_submit():
        """Copy selected files to clipboard and prepare for shutdown."""
        if not request.is_json:
            return jsonify({"error": "Invalid JSON"}), 400

        data = request.get_json()
        included_paths = data.get("include", [])
        filtered = []
        total_tokens = 0

        for full_path, rel_path, text, tokens in app.config["ALL_FILES"]:
            if rel_path in included_paths:
                filtered.append((full_path, text))
                total_tokens += tokens

        final_text = assemble_text(filtered)
        pyperclip.copy(final_text)

        print(f"\nCopied {total_tokens} tokens to clipboard")

        # Only schedule shutdown if not in testing mode
        if not app.config.get("TESTING"):
            threading.Thread(
                target=lambda: (
                    threading.Event().wait(0.1),  # Small delay to ensure response is sent
                    os.kill(os.getpid(), signal.SIGTERM),  # Send SIGTERM to self
                )
            ).start()

        return jsonify({"status": "ok", "total_tokens": total_tokens})

    return app


def run_ui_server(path):
    """
    The main entry point from the CLI when --ui is used.
    Gathers file data, starts the server on a free port, and opens the browser.
    """
    # Create and configure the app
    app = create_app(path)

    # Find an available port
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    url = f"http://127.0.0.1:{port}"
    print(f"Running on {url}")

    # Open the browser automatically
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    # Handle SIGTERM gracefully
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

    app.run(host="127.0.0.1", port=port)
