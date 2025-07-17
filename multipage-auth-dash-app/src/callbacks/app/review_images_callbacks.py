from pathlib import Path

from dash import Input, Output, callback

from auth.authentication_proxy import get_current_username
from file_io.file_utilities_proxy import (
    get_image_filenames,
    get_user_directory,
)


@callback(
    Output("review-images-user-directory", "data"),
    Output("review-images-image-filenames", "data"),
    Input("review-images-image-list", "id"),  # fires on page load
    prevent_initial_call=False,
)
def get_image_files(_) -> tuple[str, list[str]]:
    """
    Return all .tif image files for the current user, if available.

    Returns
    -------
    list of str
        Filenames of .tif images for the user, or an empty list if not logged in or no directory.
    """
    try:
        username = get_current_username()

        user_dir = Path(get_user_directory(username), "images")
        image_files = get_image_filenames(user_dir)
        return str(user_dir), image_files
    except Exception:
        return "", []


@callback(
    Output("review-images-static-alert", "children"),
    Output("review-images-static-alert", "style"),
    Input("review-images-image-filenames", "data"),
    prevent_initial_call=False,
)
def review_images_warning_callback(image_filenames):
    """
    Show a warning on the review page if the user is not logged in or has no .tif images in their directory.

    Returns
    -------
    msg : str
        Warning message if no user or no images, otherwise empty string.
    style : dict
        CSS style dict to show or hide the alert.
    """
    hide_style = {"display": "none"}
    show_style = {"display": "block"}
    if image_filenames:
        return "", hide_style
    else:
        return "No images found for the current user.", show_style
