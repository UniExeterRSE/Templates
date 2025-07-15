from typing import Tuple, Union

from dash import Input, Output, State, callback, no_update
from dash._callback import NoUpdate

from auth.authentication_proxy import authenticate_user


@callback(
    Output("login-button", "disabled"),
    [Input("login-username", "value"), Input("login-password", "value")],
)
def set_login_button_disabled(username: str, password: str) -> bool:
    """
    Disable the login button unless both username and password fields are filled.

    Returns
    -------
    bool
        True if button should be disabled, False if enabled.
    """
    return not (username and password)


@callback(
    [
        Output("login-message", "children"),
        Output("login-message", "color"),
        Output("login-url", "pathname"),
    ],
    Input("login-button", "n_clicks"),
    [State("login-username", "value"), State("login-password", "value")],
    prevent_initial_call=True,
)
def handle_login(
    n_clicks: Union[int, None], username: str, password: str
) -> Tuple[str, str, Union[str, NoUpdate]]:
    """
    Attempt to authenticate the user and provide feedback and redirect on login attempt.

    Returns
    -------
    Tuple[str, str, Union[str, NoUpdate]]
        Message to display, color for the message, and redirect path.
    """
    if not n_clicks:
        return "", "success", no_update

    success, message = authenticate_user(username, password)
    color = "success" if success else "danger"
    redirect = "/select-images" if success else no_update

    return message, color, redirect
