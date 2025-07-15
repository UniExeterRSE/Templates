import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html,
    page_container,
    page_registry,
)


def _create_auth_menu_items():
    """Create auth menu items (login, register)."""
    auth_pages = [
        page for page in page_registry.values() if page.get("location") == "auth"
    ]
    return [
        dbc.DropdownMenuItem(
            page.get("title", page["name"]),
            href=page["path"],
            id={"type": "menu-item", "location": "auth", "path": page["path"]},
        )
        for page in auth_pages
    ]


def _create_app_menu_items():
    """Create app menu items with logout."""
    app_pages = [
        page for page in page_registry.values() if page.get("location") == "app"
    ]
    menu_items = [
        dbc.DropdownMenuItem(
            page.get("title", page["name"]),
            href=page["path"],
            id={"type": "menu-item", "location": "app", "path": page["path"]},
        )
        for page in app_pages
    ]

    # Add logout button
    menu_items.append(
        dbc.DropdownMenuItem(
            "Logout",
            id={"type": "menu-item", "location": "logout", "path": "logout"},
        )
    )

    return menu_items


def create_page_layout():
    """Create the page layout after pages have been registered."""
    return html.Div(
        [
            dcc.Location(id="url"),
            dbc.NavbarSimple(
                brand="Example App",
                fluid=True,
                style={"width": "100%", "margin": "0"},
                children=[
                    dbc.DropdownMenu(
                        id="auth-dropdown-menu",
                        nav=True,
                        in_navbar=True,
                        label="Login / Register",
                        align_end=True,
                        children=_create_auth_menu_items(),
                        style={
                            "display": "none"
                        },  # Initially hidden, callback will control
                    ),
                    dbc.DropdownMenu(
                        id="user-dropdown-menu",
                        nav=True,
                        in_navbar=True,
                        label="",  # Will be updated by callback
                        align_end=True,
                        children=_create_app_menu_items(),
                        style={
                            "display": "none"
                        },  # Initially hidden, callback will control
                    ),
                ],
            ),
            html.Div(style={"paddingBottom": "24px"}),  # Padding after navbar
            html.Div(
                page_container,
                style={"padding": "24px 0"}  # Padding around page_container
            ),
        ]
    )
