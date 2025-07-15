from typing import Union

from dash import Input, Output, State, callback, no_update
from dash._callback import NoUpdate

from auth.authentication_proxy import (
    register_user,
    username_is_valid,
)


@callback(
    Output("register-button", "disabled"),
    [
        Input("register-username", "value"),
        Input("register-password", "value"),
        Input("register-confirm-password", "value"),
    ],
)
def set_register_button_disabled(
    username: str, password: str, confirm_password: str
) -> bool:
    """
    Disable the register button unless username is filled, password is filled, and passwords match.

    Returns
    -------
    bool
        True if button should be disabled, False if enabled.
    """
    if username and password and password == confirm_password:
        return False
    return True


@callback(
    [
        Output("register-success", "children"),
        Output("register-redirect", "pathname"),
    ],
    Input("register-button", "n_clicks"),
    [
        State("register-username", "value"),
        State("register-password", "value"),
    ],
    prevent_initial_call=True,
)
def register_user_message(
    register_clicks: Union[int, None], username: str, password: str
) -> tuple[str, Union[str, NoUpdate]]:
    """
    Attempt to register a new user and redirect to login on success.

    Returns
    -------
    tuple[str, Union[str, NoUpdate]]
        Message to display and redirect path.
    """
    if not register_clicks:
        return "", no_update
    if password is None:
        return "Password empty", no_update

    success, message = register_user(username, password)

    # Local redirect: redirect to login page after successful registration
    redirect = "/login" if success else no_update

    return message, redirect


@callback(
    Output("register-username-alert", "children"),
    Input("register-username", "value"),
)
def check_username_message(username):
    """
    Show a warning if the username already exists.

    Returns
    -------
    str
        Empty string if valid username, warning message if already taken.
    """
    if not username or username_is_valid(username):
        return ""

    return "Username already exists"


@callback(
    Output("register-password-alert", "children"),
    Input("register-confirm-password", "value"),
    State("register-password", "value"),
)
def check_password_message(confirm_password, password):
    """
    Show a warning if the password and confirm password do not match.

    Returns
    -------
    str
        Empty string if passwords match, warning message if not.
    """
    if not confirm_password:
        return ""
    if password != confirm_password:
        return "Passwords do not match"
    return ""
