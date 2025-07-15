"""Pytest configuration file to add src directory to Python path and shared fixtures."""

from io import BytesIO
from pathlib import Path

import auth.authentication_proxy as authentication


class AuthenticationMockHelper:
    """
    Helper for mocking authentication logic in tests.

    Parameters
    ----------
    mocker : pytest_mock.MockerFixture
        The pytest-mock fixture used to patch and create MagicMock objects.

    Attributes
    ----------
    mock : MagicMock
        The mock authentication object with patched methods and properties.
    """

    def __init__(self, mocker):
        mock = mocker.MagicMock(spec=authentication)
        mock.current_user = mocker.Mock()
        mock.is_authenticated = mocker.MagicMock(return_value=False)
        mock.get_current_username = mocker.MagicMock(return_value=None)
        mock.logout = mocker.MagicMock(return_value=None)
        mock.authenticate_user = mocker.MagicMock(
            return_value=(False, "Invalid username or password.")
        )
        mock.register_user = mocker.MagicMock(
            return_value=(False, "Username already exists")
        )
        mock.username_is_valid = mocker.MagicMock(return_value=True)
        self._mock = mock

        mocker.patch("auth.authentication_proxy.authentication", mock)

    def authenticate(self, username="testuser"):
        """
        Simulate a successful authentication for a given username.

        Parameters
        ----------
        username : str, optional
            The username to authenticate as (default is "testuser").
        """
        self._mock.is_authenticated.return_value = True
        self._mock.get_current_username.return_value = username

    def logout(self):
        """
        Simulate logging out the current user.
        """
        self._mock.is_authenticated.return_value = False
        self._mock.get_current_username.return_value = None

    def set_authentication_success(
        self, username="testuser", message="Login successful. Redirecting..."
    ):
        """
        Set the authentication mock to simulate a successful login.

        Parameters
        ----------
        username : str, optional
            The username to authenticate as (default is "testuser").
        message : str, optional
            The message to return on successful authentication.
        """
        self._mock.authenticate_user.return_value = (True, message)
        self.authenticate(username)

    def set_authentication_failure(self, message="Invalid username or password."):
        """
        Set the authentication mock to simulate a failed login.

        Parameters
        ----------
        message : str, optional
            The message to return on failed authentication.
        """
        self._mock.authenticate_user.return_value = (False, message)
        self.logout()

    def set_registration_success(
        self,
        message="Registration successful. You can now log in with your new account.",
    ):
        """
        Set the registration mock to simulate a successful registration.

        Parameters
        ----------
        message : str, optional
            The message to return on successful registration.
        """
        self._mock.register_user.return_value = (True, message)

    def set_registration_failure(self, message="Username already exists"):
        """
        Set the registration mock to simulate a failed registration.

        Parameters
        ----------
        message : str, optional
            The message to return on failed registration.
        """
        self._mock.register_user.return_value = (False, message)

    def set_username_valid(self, is_valid=True):
        """
        Set the username validity check result.

        Parameters
        ----------
        is_valid : bool, optional
            Whether the username is valid (default is True).
        """
        self._mock.username_is_valid.return_value = is_valid

    @property
    def mock(self):
        """
        Returns the mock authentication object.

        Returns
        -------
        MagicMock
            The mock authentication object.
        """
        return self._mock


class FileUtilitiesMockHelper:
    """
    Helper for mocking file utility logic in tests.

    Parameters
    ----------
    mocker : pytest_mock.MockerFixture
        The pytest-mock fixture used to patch and create MagicMock objects.

    Attributes
    ----------
    user_path : pathlib.Path
        The mocked user directory path.
    timestamped_path : pathlib.Path
        The mocked timestamped folder path.
    zip_archive : io.BytesIO
        The mocked zip archive for image data.
    mock : MagicMock
        The mock file utilities object with patched methods and properties.
    """

    def __init__(self, mocker):
        # Folder utilities
        self.user_path = Path("/mock/user/testuser")
        self.timestamped_path = Path(
            "/mock/user/testuser/mothermachine/20250103_120000"
        )
        # Image utilities
        self.zip_archive = BytesIO()
        self.zip_archive.write(b"Mock zip content for testing")
        self.zip_archive.seek(0)
        # Import and mock
        from file_io import file_utilities_proxy

        mock = mocker.MagicMock(spec=file_utilities_proxy)
        # Folder utility mocks
        mock.get_user_directory = mocker.MagicMock(return_value=self.user_path)
        mock.create_user_directory = mocker.MagicMock(return_value=None)
        mock.create_timestamped_folder = mocker.MagicMock(
            return_value=self.timestamped_path
        )
        mock.user_directory = mocker.MagicMock(return_value=self.user_path)
        # Image utility mocks
        mock.create_tif_zip_archive = mocker.MagicMock(return_value=self.zip_archive)
        mock.get_tiff_bytes = mocker.MagicMock(return_value=b"mock_tiff_bytes")
        mock.write_images_to_folder = mocker.MagicMock()
        mock.get_image_filenames = mocker.MagicMock(return_value=[])
        mock.decode_base64_image = mocker.MagicMock(
            return_value=b"mock_decoded_image_bytes"
        )

        # Patch save_image_from_bytes to return a mock with .name attribute set to the filename
        def save_image_from_bytes_side_effect(image_bytes, filename, folder):
            file_mock = mocker.Mock()
            file_mock.name = filename
            return file_mock

        mock.save_image_from_bytes = mocker.MagicMock(
            side_effect=save_image_from_bytes_side_effect
        )

        # Patch process_upload to simulate error messages for invalid extensions

        self._mock = mock

        mocker.patch("file_io.file_utilities_proxy.file_utilities", mock)

    # Folder utility helpers
    def set_user_path(self, path: Path):
        """
        Set the mocked user directory path.

        Parameters
        ----------
        path : str or Path
            The path to set as the user directory.
        """
        self.user_path = path
        self._mock.get_user_directory.return_value = self.user_path
        self._mock.user_directory.return_value = self.user_path

    def set_get_image_files(self, filenames):
        """
        Set the mocked image files.

        Parameters
        ----------
        files : list of str
            The list of file names to return for images.
        """
        self._mock.get_image_files.return_value = filenames

    # Image utility helpers
    def set_zip_content(self, content):
        """
        Set the mocked zip archive content.

        Parameters
        ----------
        content : bytes
            The content to use for the zip archive.
        """
        self.zip_archive = BytesIO(content)
        self._mock.create_tif_zip_archive.return_value = self.zip_archive

    def set_tiff_bytes(self, content):
        """
        Set the mocked TIFF bytes content.

        Parameters
        ----------
        content : bytes
            The TIFF bytes to return.
        """
        self._mock.get_tiff_bytes.return_value = content

    @property
    def mock(self):
        """
        Returns the mock file utilities object.

        Returns
        -------
        MagicMock
            The mock file utilities object.
        """
        return self._mock
