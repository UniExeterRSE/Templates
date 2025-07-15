"""
Authentication guards and menu management for the application.

Handles authentication-based access control and dynamic menu visibility.
Individual feature callbacks handle their own navigation redirects.
"""

from dash import Input, Output, callback, no_update, page_registry

from auth.authentication_proxy import get_current_username, is_authenticated, logout

# Define which locations require authentication
PROTECTED_LOCATIONS = {"app"}
AUTH_LOCATIONS = {"auth"}


def _get_location(pathname):
    """Get the location of a page from the page registry."""
    # get page whose path is contained in the pathname
    current_page = next(
        (page for page in page_registry.values() if page["path"] in pathname), None
    )
    return current_page.get("location") if current_page else None


@callback(
    [
        Output("auth-dropdown-menu", "style"),
        Output("user-dropdown-menu", "style"),
        Output("user-dropdown-menu", "label"),
    ],
    Input("url", "pathname"),
)
def update_menu_visibility(pathname):
    """
    Show or hide the authentication and user dropdown menus, and set the user label, based on authentication status.

    When the user is authenticated, the user menu is shown with a personalized label and the auth menu is hidden.
    When the user is not authenticated, the auth menu is shown and the user menu is hidden.

    Parameters
    ----------
    pathname : str
        The current URL path.

    Returns
    -------
    auth_style : dict
        CSS style for the auth dropdown menu.
    user_style : dict
        CSS style for the user dropdown menu.
    user_label : str
        The label to display in the user dropdown menu.
    """
    user_is_authenticated = is_authenticated()
    if user_is_authenticated:
        auth_style = {"display": "none"}
        user_style = {}
        username = get_current_username() or "User"
        user_label = f"Welcome, {username}"
    else:
        auth_style = {}
        user_style = {"display": "none"}
        user_label = ""
    return auth_style, user_style, user_label


@callback(
    Output("url", "pathname"),
    [
        Input("url", "pathname"),
        Input(
            {"type": "menu-item", "location": "logout", "path": "logout"}, "n_clicks"
        ),
    ],
    prevent_initial_call=True,
)
def auth_guard_and_logout(pathname, logout_clicks):
    """
    Handle user authentication and navigation redirects based on user actions and authentication state.

    If the user clicks logout, they are logged out and redirected to the login page.
    If the user is authenticated and visits a non-protected page, they are redirected to the select-images page.
    If the user is not authenticated and visits a non-auth page, they are redirected to the login page.
    Otherwise, the current page is shown.

    Parameters
    ----------
    pathname : str
        The current URL path.
    logout_clicks : int or None
        Number of times the logout menu item has been clicked.

    Returns
    -------
    str or dash.no_update
        The new pathname to redirect to, or no_update to stay on the current page.
    """
    # Handle logout clicks
    if logout_clicks:
        logout()
        return "/login"

    # Get current authentication status and page location
    user_authenticated = is_authenticated()
    page_location = _get_location(pathname)

    # Authenticated users: redirect to select-images(except for protected pages)
    if user_authenticated and page_location not in PROTECTED_LOCATIONS:
        return "/select-images"

    # Unauthenticated users: redirect to login (except for auth pages)
    if not user_authenticated and page_location not in AUTH_LOCATIONS:
        return "/login"

    # No redirect needed
    return no_update
