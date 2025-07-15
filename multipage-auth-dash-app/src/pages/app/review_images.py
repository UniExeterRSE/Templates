from pathlib import Path

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, register_page
from PIL import Image

register_page(
    __name__,
    path="/review-images",
    location="app",
    name="Review Images",
)


def layout():
    return html.Div(
        [
            html.H1("Review Images"),
            dcc.Store(id="review-images-image-filenames"),
            dcc.Store(id="review-images-user-directory"),
            dbc.Alert(
                id="review-images-static-alert",
                children="",
                color="danger",
                className="mt-3",
                style={"display": "none"},
            ),
            html.Div(id="review-images-image-list"),
        ]
    )


@callback(
    Output("review-images-image-list", "children"),
    Input("review-images-image-filenames", "data"),
    State("review-images-user-directory", "data"),
)
def display_images(filenames: list[str], user_dir: str) -> list[html.Div]:
    """
    Display a list of user image files as image cards on the review page.


    Note
    ----
    This callback is defined in the layout file (not the callbacks file)
    to maintain separation of concerns: it directly updates layout components
    specific to this page, rather than being part of the domain-level callback logic.

    If there are no image files, returns an empty list. Otherwise, returns a list of Divs,
    each showing the filename and the image preview.

    Parameters
    ----------
    image_files : list of str or None
        Filenames of images to display, or None/empty if no images.

    Returns
    -------
    list of dash.html.Div
        List of Divs containing image previews and filenames, or empty if no images.
    """
    if not filenames:
        return []

    image_divs = [
        html.Div(
            [
                html.Div(filename),
                html.Img(
                    src=Image.open(Path(user_dir, filename)),  # type: ignore
                    alt=filename,
                    style={"maxWidth": "100%", "height": "auto", "margin": "10px"},
                ),
            ],
            style={
                "display": "inline-block",
                "textAlign": "center",
                "margin": "10px",
            },
        )
        for filename in filenames
    ]
    return image_divs
