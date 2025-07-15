import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html,
    register_page,
)

register_page(__name__, path="/register", location="auth", name="Register")

layout = html.Div(
    children=[
        dcc.Location(id="register-redirect", refresh=True),
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H2("Create Account")),
                            dbc.CardBody(
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    "Username",
                                                    html_for="register-username",
                                                ),
                                                dbc.Input(
                                                    id="register-username",
                                                    type="text",
                                                    placeholder="Enter your username",
                                                    autoFocus=True,
                                                ),
                                                html.Div(id="register-username-alert"),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    "Password",
                                                    html_for="register-password",
                                                ),
                                                dbc.Input(
                                                    id="register-password",
                                                    type="password",
                                                    placeholder="Enter your password",
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    "Confirm Password",
                                                    html_for="register-confirm-password",
                                                ),
                                                dbc.Input(
                                                    id="register-confirm-password",
                                                    type="password",
                                                    placeholder="Confirm your password",
                                                ),
                                                html.Div(id="register-password-alert"),
                                            ],
                                            className="mb-4",
                                        ),
                                        dbc.Row(
                                            dbc.Button(
                                                "Register",
                                                type="submit",
                                                id="register-button",
                                                color="primary",
                                                size="lg",
                                                disabled=True,
                                            ),
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            html.Div(id="register-success"),
                                            className="mb-3",
                                        ),
                                        html.Hr(className="my-4"),
                                        dbc.Row(
                                            dcc.Link(
                                                "Already have an account? Login here.",
                                                href="/login",
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
