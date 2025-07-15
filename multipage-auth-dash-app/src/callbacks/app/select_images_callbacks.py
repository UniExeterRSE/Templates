from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

from dash import Input, Output, State, callback, no_update

from auth.authentication_proxy import get_current_username, is_authenticated
from file_io.file_utilities_proxy import (
    create_tif_zip_archive,
    decode_base64_image,
    get_image_arrays_from_folder,
    get_user_directory,
    save_image_from_bytes,
    validate_image_content,
)

"""Callbacks for handling image upload functionality in the select_images page."""


class UploadResponse(TypedDict, total=False):
    type: str
    message: str
    valid_files: List[str]
    errors: List[str]


class ReviewImagesResponse(TypedDict, total=False):
    type: str
    message: str
    errors: List[str]


class ProcessedFileInfo(TypedDict, total=False):
    saved_files: List[str]
    errors: List[str]


@callback(
    Output("upload-status", "data"),
    Input("upload-images", "contents"),
    State("upload-images", "filename"),
    prevent_initial_call=True,
)
def handle_image_upload(
    contents: Optional[List[str]], filenames: Optional[List[str]]
) -> UploadResponse:
    """
    Handle uploaded images by saving them the user's directory.

    Parameters
    ----------
    contents : Optional[List[str]]
        List of base64 encoded file contents, or None if no files uploaded.
    filenames : Optional[List[str]]
        List of original filenames, or None if no files uploaded.

    Returns
    -------
    UploadResponse
        Dictionary with keys: type, message, valid_files, errors.
    """
    if not is_authenticated():
        return _upload_error_response("You must be logged in to upload images.", [])

    if not contents or not filenames:
        return _empty_upload_response()

    try:
        processed_images_results = _process_uploaded_images(contents, filenames)

        saved_files = processed_images_results.get("saved_files")
        errors = processed_images_results.get("errors")

        if not saved_files or len(saved_files) == 0:
            return _upload_error_response(
                "Upload failed", errors or ["Unknown error occurred"]
            )

        upload_type = "partial_success" if errors else "success"
        return _successful_upload_response(upload_type, saved_files, errors)

    except Exception as e:
        return _upload_error_response("Upload failed", [str(e)])


def _process_uploaded_images(
    contents: List[str], filenames: List[str]
) -> ProcessedFileInfo:
    """
    Process a batch of uploaded images.

    Parameters
    ----------
    contents : List[str]
        List of base64 encoded file contents.
    filenames : List[str]
        List of original filenames.

    Returns
    -------
    ProcessedFileInfo
        Dictionary with keys: saved_files (List[str]), errors (List[str]), upload_dir (Path).

    Raises
    ------
    ValueError
        If no authenticated user is found.
    """
    username = get_current_username()
    if not username:
        raise ValueError("No authenticated user found")

    user_dir = get_user_directory(username)
    image_dir = Path(user_dir, "images")

    saved_files = []
    errors = []

    for content, filename in zip(contents, filenames):
        try:
            _validate_file_extension(filename)
            decoded_content = decode_base64_image(content)
            validate_image_content(decoded_content)

            saved_path = save_image_from_bytes(
                decoded_content, filename, image_dir
            )
            saved_files.append(saved_path.name)

        except Exception as e:
            errors.append(f"{filename}: {str(e)}")

    # Return None for upload_dir if no files were saved
    return ProcessedFileInfo(saved_files=saved_files, errors=errors)


@callback(
    Output("run-btn", "disabled"),
    Input("upload-images", "contents"),
    prevent_initial_call=False,
)
def update_review_images_button_state(contents):
    """
    Enable the review images button only if there are uploaded images.

    Parameters
    ----------
    contents : Optional[List[str]]
        List of base64 encoded file contents, or None if no files uploaded.

    Returns
    -------
    bool
        True if button should be disabled (no valid images), False if enabled.
    """
    if not contents or not any(contents):
        return True
    return False


@callback(
    [
        Output("download", "data"),
        Output("select-images-url", "pathname"),
        Output("review-images-status", "data"),
    ],
    Input("run-btn", "n_clicks"),
    State("upload-images", "contents"),
    prevent_initial_call=True,
)
def download_images_and_review(n_clicks: int, contents: List[str]) -> list:
    """
    Handle the click of the run button to download images and prepare for review.

    Parameters
    ----------
    n_clicks : int
        Number of times the run button has been clicked.

    Returns
    -------
    List[Optional[Dict[str, Any]], Union[str, NoUpdate], ReviewImagesResponse]
        - Download data for Dash (or None)
        - Pathname for redirect (or no_update)
        - ReviewImagesResponse: dict with keys type, message, errors
    """
    if not n_clicks or n_clicks <= 0 or contents == []:
        return [None, no_update, {}]

    try:
        username = get_current_username()

        user_dir = get_user_directory(username)
        images_dir = Path(user_dir, "images")
        images = get_image_arrays_from_folder(images_dir)
        download_data = _create_download_zip(images)

        if not download_data:
            return [None, no_update, _zip_error_response()]

        return [
            download_data,
            "/review-images",
            {
                "type": "success",
                "message": "Images ready for review.",
                "errors": [],
            },
        ]

    except Exception as e:
        return [
            None,
            no_update,
            {
                "type": "error",
                "message": "Failed to download images.",
                "errors": [str(e)],
            },
        ]


def _validate_file_extension(filename: str) -> None:
    """
    Validate the file extension of the uploaded image.

    Parameters
    ----------
    filename : str
        Name of the file being validated.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    """
    valid_extensions = [".tif", ".tiff", ".png", ".jpg", ".jpeg"]
    if not any(filename.lower().endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Unsupported file type: {filename}")


def _create_download_zip(results) -> Optional[Dict[str, Any]]:
    """
    Create a ZIP archive of images for download.

    Parameters
    ----------
    results : Any
        Images to include in the ZIP archive.

    Returns
    -------
    Any or None
        Download data for Dash, or None if creation failed.
    """
    import base64

    zip_archive = create_tif_zip_archive(results)
    if zip_archive is None:
        return None
    # Encode zip content as base64 string for Dash Download component
    zip_bytes = zip_archive.getvalue()
    zip_b64 = base64.b64encode(zip_bytes).decode("utf-8")
    download_data = {
        "filename": "images.zip",
        "content": zip_b64,
        "base64": True,
        "type": "application/zip",
    }
    return download_data


def _upload_error_response(
    message: str, errors: Optional[List[str]] = None
) -> UploadResponse:
    """
    Create an error response for image upload failures.

    Parameters
    ----------
    message : str
        Error message to display.
    errors : Optional[List[str]]
        List of error details.

    Returns
    -------
    UploadResponse
        Dictionary with keys: type, message, valid_files, errors.
    """
    return UploadResponse(
        type="error",
        message=message,
        valid_files=[],
        errors=errors or [],
    )


def _empty_upload_response() -> UploadResponse:
    """
    Create an empty upload response when no files are uploaded.

    Returns
    -------
    UploadResponse
        Dictionary with keys: type, message, valid_files, errors.
    """
    return UploadResponse(
        type="empty", message="No files uploaded", valid_files=[], errors=[]
    )


def _successful_upload_response(
    upload_type: str, valid_files: List[str], errors: Optional[List[str]] = None
) -> UploadResponse:
    """
    Create a successful upload response.

    Parameters
    ----------
    upload_type : str
        Type of upload result (e.g., 'success', 'partial_success').
    valid_files : List[str]
        List of successfully uploaded filenames.
    errors : Optional[List[str]]
        List of error details.

    Returns
    -------
    UploadResponse
        Dictionary with keys: type, message, valid_files, errors.
    """
    return UploadResponse(
        type=upload_type,
        message="Upload completed",
        valid_files=valid_files,
        errors=errors or [],
    )


def _zip_error_response() -> ReviewImagesResponse:
    """
    Create an error response for ZIP archive creation failures.

    Returns
    -------
    ReviewImagesResponse
        Dictionary with keys: type, message, errors.
    """
    return {
        "type": "error",
        "message": "Files uploaded, but failed to create ZIP archive for download.",
        "errors": ["ZIP archive creation failed."],
    }
