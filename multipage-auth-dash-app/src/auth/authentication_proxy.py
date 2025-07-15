"""
Authentication Proxy module.

This module provides a proxy interface to the authentication service functions.
It allows for easy swapping, mocking, or extension of authentication logic without
modifying the core authentication implementation.
"""

from typing import Tuple

from . import authentication


def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
    return authentication.authenticate_user(username, password)


def register_user(username: str, password: str) -> Tuple[bool, str]:
    return authentication.register_user(username, password)


def logout() -> None:
    return authentication.logout()


def is_authenticated() -> bool:
    return authentication.is_authenticated()


def get_current_username() -> str:
    return authentication.get_current_username()


def username_is_valid(username: str) -> bool:
    return authentication.username_is_valid(username)
