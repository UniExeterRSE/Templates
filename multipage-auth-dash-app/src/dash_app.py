import importlib
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from auth import server
from pages.layout import create_page_layout

"""This module contains the Flask server and the Dash app for the app.

The Flask server is used for user management, while the Dash app is used for the main
functionality of the app."""


def register_all_callbacks() -> None:
    """
    Recursively import all Python modules whose filenames contain 'callbacks' in the
    callback directory and its subdirectories.
    """
    src_path = Path(__file__).parent
    callbacks_dir = src_path / "callbacks"
    for item in callbacks_dir.rglob("*.py"):
        if "callbacks" in item.stem:
            rel_path = item.with_suffix("").relative_to(callbacks_dir.parent)
            module_name = ".".join(rel_path.parts)
            try:
                importlib.import_module(module_name)
            except Exception:
                pass  # Skip problematic modules


def create_app():
    """Create and configure the Dash application."""
    # Create the Dash app with automatic page discovery
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.SOLAR],
        use_pages=True,
        pages_folder="pages",  # Use standard pages folder
        suppress_callback_exceptions=True,
    )

    # Automatically register all callbacks
    register_all_callbacks()

    # Create layout after pages are registered
    app.layout = create_page_layout()

    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
