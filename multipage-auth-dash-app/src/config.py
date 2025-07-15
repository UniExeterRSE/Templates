import os
from pathlib import Path

from flask.cli import load_dotenv

# Load environment variables from .env file if it exists
# This is useful for local development and testing.
load_dotenv()


def get_config() -> dict:
    """Get the configuration for the application. Where environment variables are
    not set, defaults are used.

    Environment Variables:
    ----------------------
    DEFAULT_USER_BASE_FOLDER : str
        Base directory for user data storage (default: project_root/data/users)
    SECRET_KEY : str
        Flask secret key for session encryption
    DATABASE_URL : str
        Database connection URL (default: sqlite:///project_root/data/users.db)
    SESSION_FILE_DIR : str
        Directory for Flask session files (default: project_root/data/flask_session)

    Returns
    -------
        dict
            A dictionary containing the configuration for the application.
    """
    # Get project root directory (where pyproject.toml is located)
    project_root = Path(__file__).parent.parent

    return {
        # Base folder for user data - move to project root level
        "DEFAULT_USER_BASE_FOLDER": os.getenv(
            "DEFAULT_USER_BASE_FOLDER", str(project_root / "data" / "users")
        ),
        # Flask configuration
        "SECRET_KEY": os.getenv("SECRET_KEY", "a8f5f167f44f4964e6c998dee827110c"),
        # Move database to data directory at project root
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "DATABASE_URL", f"sqlite:///{project_root / 'data' / 'users.db'}"
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_TYPE": "filesystem",
        # Move Flask session files to data directory
        "SESSION_FILE_DIR": os.getenv(
            "SESSION_FILE_DIR", str(project_root / "data" / "flask_session")
        ),
    }
