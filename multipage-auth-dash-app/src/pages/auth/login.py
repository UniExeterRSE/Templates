import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html,
    register_page,
)

register_page(__name__, path="/login", location="auth", name="Login")

layout = html.Div(
    children=[
        dcc.Location(id="login-url", refresh=True),
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H2("Welcome Back")),
                            dbc.CardBody(
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    "Username",
                                                    html_for="login-username",
                                                ),
                                                dbc.Input(
                                                    id="login-username",
                                                    type="text",
                                                    placeholder="Enter your username",
                                                    autoFocus=True,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    "Password",
                                                    html_for="login-password",
                                                ),
                                                dbc.Input(
                                                    id="login-password",
                                                    type="password",
                                                    placeholder="Enter your password",
                                                ),
                                            ],
                                            className="mb-4",
                                        ),
                                        dbc.Row(
                                            dbc.Button(
                                                "Sign In",
                                                type="submit",
                                                id="login-button",
                                                color="primary",
                                                size="lg",
                                            ),
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            html.Div(id="login-message"),
                                            className="mb-3",
                                        ),
                                        html.Hr(className="my-4"),
                                        dbc.Row(
                                            dcc.Link(
                                                "Don't have an account? Register here.",
                                                href="/register",
                                            )
                                        ),
                                    ]
                                )
                            ),
                        ]
                    ),
                    width=12,
                    lg=5,
                    md=6,
                    sm=8,
                ),
                justify="center",
            ),
            fluid=True,
        ),
    ],
)
