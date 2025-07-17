"""
Authentication service module providing user authentication and management functions.

This module acts as an abstraction layer over the underlying authentication infrastructure
(such as Flask-Login and the database), exposing a clean API for authentication, registration,
and user session management. All direct interactions with infrastructure should be encapsulated
here, so that the rest of the application can remain decoupled from implementation details.
"""

from typing import Tuple

from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from file_io.file_utilities import create_user_directory

from .infrastructure import User, user_db


def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate a user and return success status and message.

    Parameters
    ----------
    username : str
        The username to authenticate.
    password : str
        The password to check.

    Returns
    -------
    tuple of (bool, str)
        (success, message):
        - success: True if authentication succeeded, else False
        - message: Status or error message
    """
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.hashed_password, password):
        return False, "Invalid username or password."

    if login_user(user):
        create_user_directory(user.username)
        return True, "Login successful. Redirecting..."
    return False, "Login unsuccessful. Please try again."


def register_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user and return success status and message.

    Parameters
    ----------
    username : str
        The username to register.
    password : str
        The password for the new user.

    Returns
    -------
    tuple of (bool, str)
        (success, message):
        - success: True if registration succeeded, else False
        - message: Status or error message
    """
    if User.query.filter_by(username=username).first():
        return False, "Username already exists"

    hashed_password = generate_password_hash(password)
    new_user = User(username, hashed_password)
    user_db.session.add(new_user)
    user_db.session.commit()
    return (
        True,
        "Registration successful. You can now log in with your new account.",
    )


def logout() -> None:
    """
    Logout the current user.

    Returns
    -------
    None
    """
    logout_user()


def is_authenticated() -> bool:
    """
    Check if current user is authenticated.

    Returns
    -------
    bool
        True if the current user is authenticated, else False.
    """
    return current_user.is_authenticated


def get_current_username() -> str:
    """
    Retrieve the username of the currently authenticated user.

    Returns
    -------
    str
        The username of the current user.

    Raises
    ------
    PermissionError
        If no authenticated user is found.
    """
    if not is_authenticated():
        raise PermissionError("No authenticated user found")

    return current_user.username


def username_is_valid(username: str) -> bool:
    """
    Validate username and return error message if invalid.

    Parameters
    ----------
    username : str
        The username to validate.

    Returns
    -------
    bool
        Error message if username is invalid, else None.
    """
    if User.query.filter_by(username=username).first():
        return False
    return True
