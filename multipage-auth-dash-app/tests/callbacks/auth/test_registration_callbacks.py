import pytest
from dash import no_update

from callbacks.auth.registration_callbacks import (
    check_password_message,
    check_username_message,
    register_user_message,
    set_register_button_disabled,
)


@pytest.mark.parametrize(
    "username, password, confirm_password, expected",
    [
        ("user", "password", "password", False),
        ("user", "password", "wrong_password", True),
        ("", "password", "password", True),
        ("user", "", "", True),
    ],
)
def test_set_register_button_disabled(username, password, confirm_password, expected):
    """Given the username, password, and confirm password, when
    set_register_button_disabled, then return expected."""
    assert (
        set_register_button_disabled(username, password, confirm_password) is expected
    )


@pytest.mark.parametrize(
    "clicks, expected_message_length",
    [
        (None, 0),
        (0, 0),
    ],
)
def test_register_user_message_no_clicks(
    auth_mock_helper, clicks, expected_message_length
):
    """Test register_user_message when button is not clicked."""
    message, redirect = register_user_message(clicks, "user", "password")

    assert len(message) == expected_message_length
    assert redirect == no_update
    auth_mock_helper.mock.register_user.assert_not_called()


def test_register_user_message_success(auth_mock_helper):
    """Test register_user_message when registration succeeds."""
    auth_mock_helper.set_registration_success(
        "Registration successful. You can now log in with your new account."
    )

    message, redirect = register_user_message(1, "newuser", "password")

    assert (
        message == "Registration successful. You can now log in with your new account."
    )
    assert redirect == "/login"


def test_register_user_message_failure(auth_mock_helper):
    """Test register_user_message when registration fails."""
    auth_mock_helper.set_authentication_failure("Username already exists")

    message, redirect = register_user_message(1, "existing_user", "password")

    assert message == "Username already exists"
    assert redirect == no_update


def test_check_username_invalid(auth_mock_helper):
    """Test check_username_message when username is invalid (already exists)."""
    auth_mock_helper.set_username_valid(False)

    result = check_username_message("existing_user")

    assert result == "Username already exists"


def test_check_username_valid(auth_mock_helper):
    """Test check_username_message when username is valid."""
    auth_mock_helper.set_username_valid(True)

    result = check_username_message("new_user")

    assert result == ""


@pytest.mark.parametrize(
    "username",
    ["", None],
)
def test_check_username_empty_or_none(auth_mock_helper, username):
    """Test check_username_message when username is empty or None."""
    result = check_username_message(username)

    assert result == ""
    auth_mock_helper.mock.username_is_valid.assert_not_called()


@pytest.mark.parametrize(
    "confirm_password, password, expected",
    [
        ("password", "password", ""),
        ("wrong_password", "password", "Passwords do not match"),
        ("", "password", ""),  # Empty confirm password
        (None, "password", ""),  # None confirm password
    ],
)
def test_check_password(confirm_password, password, expected):
    """Test check_password_message with various password combinations."""
    assert check_password_message(confirm_password, password) == expected
