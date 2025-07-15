import pytest
from dash import no_update

from callbacks.auth.login_callbacks import handle_login, set_login_button_disabled


@pytest.mark.parametrize(
    "username, password, expected_disabled",
    [
        ("", "", True),
        ("username", "", True),
        ("", "password", True),
        ("a username", "a password", False),
        ("user", "pass", False),
    ],
)
def test_set_login_button_disabled_states(username, password, expected_disabled):
    """Test login button disabled state with various input combinations."""

    is_disabled = set_login_button_disabled(username, password)
    assert is_disabled == expected_disabled


@pytest.mark.parametrize(
    "clicks, expected_message_length",
    [
        (0, 0),
        (None, 0),
    ],
)
def test_handle_login_no_clicks(auth_mock_helper, clicks, expected_message_length):
    """Test handle_login when button is not clicked."""

    message, color, redirect = handle_login(clicks, "", "")
    assert len(message) == expected_message_length
    assert redirect == no_update
    auth_mock_helper.mock.authenticate_user.assert_not_called()


@pytest.mark.parametrize(
    "username,password",
    [
        ("unregistered user", "a password"),
        ("nonexistent", "test123"),
        ("", ""),
        ("test", ""),
        ("", "test"),
    ],
)
def test_handle_login_failures(auth_mock_helper, username, password):
    """Test handle_login with various failure scenarios using mocked authentication."""

    auth_mock_helper.set_authentication_failure("Invalid username or password.")
    message, color, redirect = handle_login(1, username, password)
    assert message == "Invalid username or password."
    assert color == "danger"
    assert redirect == no_update


def test_handle_login_authentication_failure(auth_mock_helper):
    """Test handle_login when authentication fails for registered user."""
    auth_mock_helper.set_authentication_failure("Invalid username or password.")
    message, color, redirect = handle_login(1, "testuser", "wrongpassword")
    assert message == "Invalid username or password."
    assert color == "danger"
    assert redirect == no_update


def test_handle_login_authentication_success(auth_mock_helper):
    """Test handle_login when authentication succeeds."""
    auth_mock_helper.set_authentication_success("testuser")

    message, color, redirect = handle_login(1, "testuser", "password")
    assert message == "Login successful. Redirecting..."
    assert color == "success"
    assert redirect == "/select-images"
