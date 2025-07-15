from pathlib import Path

import pytest

from callbacks.app.review_images_callbacks import (
    get_image_files,
    review_images_warning_callback,
)


def test_get_image_files_user_logged_in_with_images(
    auth_mock_helper, file_util_mock_helper
):
    """
    Returns the user directory and all .tif image filenames when a user is authenticated and has .tif images in their directory and the review page loads.
    """
    auth_mock_helper.authenticate(username="testuser")
    user_dir = Path("mock", "path", "testuser")
    file_util_mock_helper.set_user_path(user_dir)
    file_util_mock_helper.mock.get_image_filenames.return_value = [
        "img1.tif",
        "img2.tif",
    ]
    result = get_image_files(None)
    expected_dir = str(user_dir / "images")
    assert result == (expected_dir, ["img1.tif", "img2.tif"])


def test_get_image_files_user_logged_in_no_images(
    auth_mock_helper, file_util_mock_helper
):
    """
    Returns the user directory and an empty list when a user is authenticated but has no .tif images in their directory and the review page loads.
    """
    auth_mock_helper.authenticate(username="testuser")
    user_dir = Path("mock", "path", "testuser")
    file_util_mock_helper.set_user_path(user_dir)
    file_util_mock_helper.mock.get_image_filenames.return_value = []
    result = get_image_files(None)
    expected_dir = str(user_dir / "images")
    assert result == (expected_dir, [])


def test_get_image_files_user_not_logged_in(auth_mock_helper):
    """
    Returns an empty directory and empty list when no user is authenticated and the review page loads.
    """
    auth_mock_helper.logout()
    result = get_image_files(None)
    assert result == ("", [])


@pytest.mark.parametrize(
    "image_filenames,expected",
    [
        (["img1.tif"], ("", {"display": "none"})),
        ([], ("No images found for the current user.", {"display": "block"})),
    ],
)
def test_review_images_warning_callback_param(image_filenames, expected):
    """
    Hides the alert and shows no message when there are .tif image filenames and the warning callback is called.
    Shows the alert with a warning message when there are no .tif image filenames and the warning callback is called.
    """
    result = review_images_warning_callback(image_filenames)
    assert result == expected
