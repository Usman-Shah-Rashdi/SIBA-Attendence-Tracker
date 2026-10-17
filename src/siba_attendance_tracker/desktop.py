"""Native desktop entry point for the SIBA Attendance Tracker."""

from __future__ import annotations

import threading
import webbrowser

import webview
from werkzeug.serving import BaseWSGIServer, make_server

from siba_attendance_tracker.app import app


def main() -> None:
    """Start the local API and show it in a native desktop window."""

    server: BaseWSGIServer = make_server("127.0.0.1", 0, app)
    server_thread = threading.Thread(
        target=server.serve_forever,
        name="siba-api",
        daemon=True,
    )
    server_thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"

    window = webview.create_window(
        "SIBA Attendance Tracker",
        url,
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True,
    )

    try:
        webview.start()
    except webview.WebViewException:
        app.logger.exception("Native WebView unavailable; opening the dashboard in a browser")
        if not webbrowser.open(url):
            raise
        server_thread.join()
    finally:
        server.shutdown()
        server_thread.join(timeout=5)


if __name__ == "__main__":
    main()
