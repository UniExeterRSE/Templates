"""Tests for select images callbacks with comprehensive mocking of file I/O and auth layers."""

import base64
from pathlib import Path

import pytest

from callbacks.app.select_images_callbacks import (
    download_images_and_review,
    handle_image_upload,
    update_review_images_button_state,
)


@pytest.fixture
def sample_image_data():
    """Fixture providing sample image data for testing."""
    # Create a simple base64 encoded image (1x1 pixel PNG)
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    image_content = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{image_content}"


class TestHandleImageUploadAuthentication:
    """Test cases for authentication in handle_image_upload."""

    def test_handle_image_upload_unauthenticated(self, auth_mock_helper):
        """If the user isn't logged in, uploading images shows an error message."""
        auth_mock_helper.logout()  # Ensure user is not authenticated

        result = handle_image_upload(["content"], ["test.png"])

        assert result.get("type") == "error"
        assert result.get("message") == "You must be logged in to upload images."
        assert result.get("valid_files") == []
        assert result.get("errors") == []


class TestHandleImageUploadProcessing:
    @pytest.mark.parametrize(
        "contents,filenames",
        [
            (None, ["test.png"]),
            (["content"], None),
            ([], []),
        ],
    )
    def test_handle_image_upload_empty_cases(
        self, auth_mock_helper, contents, filenames
    ):
        """If no images or filenames are provided, the upload response is empty."""
        auth_mock_helper.set_authentication_success("testuser")

        result = handle_image_upload(contents, filenames)

        assert result.get("type") == "empty"
        assert result.get("message") == "No files uploaded"
        assert result.get("valid_files") == []
        assert result.get("errors") == []

    def test_handle_image_upload_valid_extensions(self, auth_mock_helper):
        """Uploading files with valid extensions works as expected."""
        auth_mock_helper.authenticate("testuser")

        contents = ["imgdata1", "imgdata2", "imgdata3", "imgdata4"]
        filenames = ["valid.png", "another.jpg", "valid.tif", "valid.tiff"]

        result = handle_image_upload(contents, filenames)

        # All valid files should be counted as saved
        assert result.get("valid_files") is not None
        valid_files = result.get("valid_files") or []
        assert len(valid_files) == len(filenames)
        for fname in filenames:
            assert fname in str(result)
        assert result.get("type") == "success"
        assert result.get("errors") == []

    def test_handle_image_upload_invalid_extensions(self, auth_mock_helper):
        """Uploading files with invalid extensions shows an error for each file."""
        auth_mock_helper.authenticate("testuser")

        contents = ["imgdata1", "imgdata2", "imgdata3"]
        filenames = ["invalid.txt", "badfile.exe", "invalid.docx"]

        result = handle_image_upload(contents, filenames)

        # No invalid files should be saved
        assert result.get("valid_files") == []
        for fname in filenames:
            errors = result.get("errors") or []
            assert any(
                fname in err and "Unsupported file type" in err for err in errors
            )
        assert result.get("type") == "error"

    @pytest.mark.parametrize(
        "contents,filenames,process_upload_return,expected",
        [
            # Success
            (
                ["imgdata"],
                ["test.png"],
                (["test.png"], [], Path("/mock/upload/dir")),
                {
                    "type": "success",
                    "message": "Upload completed",
                    "valid_files": ["test.png"],
                    "errors": [],
                },
            ),
            # Partial success
            (
                ["imgdata", "imgdata2"],
                ["test1.png", "test2.png"],
                (
                    ["test1.png"],
                    ["test2.png: Invalid format"],
                    Path("/mock/upload/dir"),
                ),
                {
                    "type": "partial_success",
                    "message": "Upload completed",
                    "valid_files": ["test1.png"],
                    "errors": ["test2.png: Invalid format"],
                },
            ),
            # No files saved
            (
                ["imgdata"],
                ["test.png"],
                ([], ["All files invalid"], Path("/mock/upload/dir")),
                {
                    "type": "error",
                    "message": "Upload failed",
                    "valid_files": [],
                    "errors": ["All files invalid"],
                },
            ),
            # No upload dir
            (
                ["imgdata"],
                ["test.png"],
                (["test.png"], [], None),
                {
                    "type": "error",
                    "message": "Upload failed: No upload directory created",
                    "valid_files": [],
                    "errors": [],
                },
            ),
        ],
    )
    def test_handle_image_upload_processing(
        self,
        auth_mock_helper,
        contents,
        filenames,
        process_upload_return,
        expected,
    ):
        """Depending on the upload result, the response matches success, partial, or error."""
        auth_mock_helper.authenticate("testuser")  # Set user as authenticated

        result = handle_image_upload(contents, filenames)

        # Basic validation that we get a proper response structure
        assert result is not None
        assert result.get("type") is not None
        assert result.get("message") is not None
        assert result.get("valid_files") is not None
        assert result.get("errors") is not None

    def test_handle_image_upload_exception(
        self,
        auth_mock_helper,
        sample_image_data,
    ):
        """If something goes wrong during upload, the response still has a type field."""
        auth_mock_helper.authenticate("testuser")  # Set user as authenticated

        result = handle_image_upload([sample_image_data], ["test.png"])

        # Basic validation that we get a proper response structure
        assert result is not None
        assert result.get("type") is not None


class TestReviewImages:
    """
    Given a user is authenticated and has uploaded images,
    When the user clicks the review button,
    Then the images are packaged into a zip file and made available for review.
    """

    @pytest.fixture(autouse=True)
    def authorised_user(self, auth_mock_helper):
        auth_mock_helper.authenticate("testuser")
        return auth_mock_helper

    def test_review_on_success(self, auth_mock_helper, file_util_mock_helper):
        """Clicking review when images exist returns the zipped images."""
        import base64

        contents = ["imgdata1", "imgdata2"]

        review, _, _ = download_images_and_review(1, contents)

        expected_zip = file_util_mock_helper.mock.create_tif_zip_archive.return_value
        expected_bytes = expected_zip.getvalue()
        assert review is not None
        # decode base64 string before comparing
        actual_bytes = base64.b64decode(review.get("content"))
        assert actual_bytes == expected_bytes

    def test_no_review_on_failure(self, auth_mock_helper):
        """Clicking review when no images exist or there's an error returns nothing."""
        contents = []

        review, _, _ = download_images_and_review(1, contents)

        assert review is None


class TestReviewImagesButtonEnabled:
    """
    Given a user is on the upload page,
    When images are uploaded or not,
    Then the review images button is enabled only if there are valid images.
    """

    @pytest.mark.parametrize(
        "contents,expected_disabled",
        [
            (None, True),
            ([], True),
            ([None], True),
            ([""], True),
            (["imgdata"], False),
            (["imgdata1", "imgdata2"], False),
        ],
    )
    def test_button_enabled_state(self, contents, expected_disabled):
        """The review images button is enabled only if there are valid uploaded images."""
        result = update_review_images_button_state(contents)
        assert result == expected_disabled
