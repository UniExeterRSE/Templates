from typing import Union

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, register_page

register_page(__name__, path="/select-images", location="app", name="Select Images")


layout = html.Div(
    [
        dcc.Store(id="upload-status", data={}),
        dcc.Store(id="review-images-status", data={}),
        dcc.Location(id="select-images-url"),
        html.H1("Select Mother Machine Images", className="mb-4"),
        html.P(
            "Upload your images. Supported formats: TIFF, PNG, JPEG",
            className="mb-4",
        ),
        dbc.Card(
            [
                dbc.CardHeader("Upload Images"),
                dbc.CardBody(
                    [
                        dcc.Upload(
                            id="upload-images",
                            multiple=True,
                            children=html.Div(
                                [
                                    html.I(className="fas fa-upload me-2"),
                                    "Drag and drop or ",
                                    html.A(
                                        "click to select files", className="fw-bold"
                                    ),
                                ],
                                className="text-center p-4",
                            ),
                            style={
                                "width": "100%",
                                "height": "120px",
                                "lineHeight": "120px",
                                "borderWidth": "2px",
                                "borderStyle": "dashed",
                                "borderRadius": "10px",
                                "borderColor": "#007bff",
                                "textAlign": "center",
                                "margin": "10px",
                                "backgroundColor": "#f8f9fa",
                            },
                            className="mb-3",
                        ),
                        html.Div(
                            id="upload-status-display",
                            className="mt-3",
                        ),
                        html.Div(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-search me-2"),
                                        "Review Images",
                                    ],
                                    id="run-btn",
                                    color="primary",
                                    className="mt-4",
                                    n_clicks=0,
                                ),
                                dcc.Download(id="download"),
                                html.Div(
                                    id="review-images-status-display",
                                    className="mt-3",
                                ),
                            ],
                            className="text-center",
                        ),
                    ]
                ),
            ],
            className="mb-4",
        ),
    ],
    className="container mt-4",
)


def _create_status_alert(
    message: Union[str, html.Span], alert_type: str = "info"
) -> dbc.Alert:
    """Create a status alert with consistent styling."""
    icons = {
        "success": "fas fa-check-circle",
        "warning": "fas fa-exclamation-triangle",
        "danger": "fas fa-times-circle",
        "error": "fas fa-times-circle",
        "info": "fas fa-info-circle",
    }
    color = alert_type if alert_type in ["success", "warning", "danger"] else "info"
    if alert_type == "error":
        color = "danger"
    return dbc.Alert(
        [html.I(className=f"{icons.get(alert_type, icons['info'])} me-2"), message],
        color=color,
        className="mt-3",
    )


@callback(
    Output("upload-status-display", "children"),
    Input("upload-status", "data"),
    prevent_initial_call=True,
)
def render_upload_status(status_data):
    """Render upload status UI based on data from callback."""
    if not status_data or status_data.get("type") == "empty":
        return html.Div()

    status_type = status_data.get("type")
    errors = status_data.get("errors", [])
    valid_files = status_data.get("valid_files", [])

    success_msg = html.Span(
        [
            "Uploaded image(s):",
            html.Ul([html.Li(f) for f in valid_files], className="mb-0"),
        ]
    )

    if status_type == "partial_success":
        warning_msg = f"Some errors occurred: {'; '.join(errors)}"
        return html.Div(
            [
                _create_status_alert(success_msg, "success"),
                _create_status_alert(warning_msg, "warning"),
            ]
        )

    if status_type == "success":
        return _create_status_alert(success_msg, "success")

    if status_type == "error":
        error_msg = (
            "; ".join(errors) if errors else status_data.get("message", "Unknown error")
        )
        return _create_status_alert(f"Upload failed. {error_msg}", "danger")

    return html.Div()


@callback(
    Output("review-images-status-display", "children"),
    Input("review-images-status", "data"),
    prevent_initial_call=True,
)
def render_review_images_status(status_data):
    """Render image status UI based on data from callback."""
    if not status_data or status_data.get("type") == "empty":
        return html.Div()
    status_type = status_data.get("type")
    message = status_data.get("message", "")
    return _create_status_alert(message, status_type)
