import pytest
from dash import no_update

from callbacks.layout_callbacks import auth_guard_and_logout, update_menu_visibility


@pytest.fixture(autouse=True)
def mock_page_registry(mocker):
    mock_pages = {
        "page1": {"location": "auth", "name": "Login", "path": "/login"},
        "page2": {
            "location": "app",
            "name": "Select Images",
            "path": "/select-images",
        },
        "page3": {"location": "auth", "name": "Register", "path": "/register"},
        "page4": {"location": "app", "name": "Review", "path": "/review"},
        "page5": {
            "location": "app",
            "name": "Review Images",
            "path": "/review-images",
        },
        "page6": {"location": "home", "name": "Home", "path": "/"},
    }

    mocker.patch("callbacks.layout_callbacks.page_registry", mock_pages)
    yield mock_pages


class TestLayoutCallbacks:
    """Test cases for core navigation and callback logic."""

    def test_update_menu_visibility_authenticated(
        self,
        auth_mock_helper,
    ):
        """
        Simulates a user who is authenticated and visits the app.
        The menu should display a welcome message with the username, hide the auth menu, and show the user menu.
        """
        auth_mock_helper.authenticate("testuser")

        auth_style, user_style, user_label = update_menu_visibility("/")

        assert user_label == "Welcome, testuser"
        assert auth_style == {"display": "none"}
        assert user_style == {}

    def test_update_menu_visibility_unauthenticated(
        self,
        auth_mock_helper,
    ):
        """
        Simulates a user who is not authenticated and visits the app.
        The menu should hide the user menu, show the auth menu, and not display a welcome message.
        """
        auth_mock_helper.logout()

        auth_style, user_style, user_label = update_menu_visibility("/")

        assert user_label == ""
        assert auth_style == {}
        assert user_style == {"display": "none"}

    @pytest.mark.parametrize(
        "logout_clicks",
        [1, 2],
    )
    def test_logout_clicks_then_logout(
        self,
        auth_mock_helper,
        logout_clicks,
    ):
        """
        Simulates a user who is currently authenticated and then clicks the logout button one or more times.
        When the user clicks the logout button, the application should log them out and redirect them to the login page ("/login").
        """
        auth_mock_helper.authenticate("testuser")

        result = auth_guard_and_logout("/any", logout_clicks)

        # Should redirect to login after logout
        assert result == "/login"

    @pytest.mark.parametrize(
        "path,expected_redirect",
        [
            ("/select-images", "/login"),
            ("/review-images", "/login"),
            ("/unknown-path", "/login"),
            ("/", "/login"),
            ("/login", no_update),
            ("/register", no_update),
            ("/nonexistent", "/login"),
        ],
    )
    @pytest.mark.parametrize("logout_clicks", [0, None])
    def test_auth_guard_redirects_when_not_authenticated(
        self,
        auth_mock_helper,
        logout_clicks,
        path,
        expected_redirect,
    ):
        """
        Simulates a user who is logged out or not authenticated.
        If the user tries to access a protected page, they are redirected to the login page.
        If the user is already on an auth page, there is no redirect.
        The home page always redirects to login when unauthenticated.
        """
        auth_mock_helper.logout()

        result = auth_guard_and_logout(path, logout_clicks)

        assert result == expected_redirect
        auth_mock_helper.mock.logout.assert_not_called()

    @pytest.mark.parametrize(
        "path,expected_redirect",
        [
            ("/login", "/select-images"),
            ("/register", "/select-images"),
            ("/", "/select-images"),
            ("/select-images", no_update),
            ("/review-images", no_update),
            (
                "/unknown-path",
                "/select-images",
            ),  # Unknown paths redirect to main app for authenticated users
        ],
    )
    @pytest.mark.parametrize("logout_clicks", [0, None])
    def test_auth_guard_redirects_when_authenticated(
        self,
        auth_mock_helper,
        path,
        expected_redirect,
        logout_clicks,
    ):
        """
        Simulates a user who is authenticated.
        If the user tries to access an auth page (login/register), they are redirected to the main app page (select-images).
        If the user is already on a protected page, there is no redirect.
        The home page always redirects to select-images when authenticated.
        """
        auth_mock_helper.authenticate("testuser")

        result = auth_guard_and_logout(path, logout_clicks)

        assert result == expected_redirect
        auth_mock_helper.mock.logout.assert_not_called()

    def test_auth_guard_logout_redirects_authenticated(
        self,
        auth_mock_helper,
    ):
        """
        Simulates a user who is authenticated and clicks the logout button.
        The application should log the user out and redirect them to the login page ("/login").
        """
        auth_mock_helper.authenticate("testuser")

        result = auth_guard_and_logout("/any", 1)

        assert result == "/login"

    def test_auth_guard_logout_redirects_unauthenticated(
        self,
        auth_mock_helper,
    ):
        """
        Simulates a user who is not authenticated and clicks the logout button.
        The application should redirect the user to the login page ("/login") even if they are already logged out.
        """
        auth_mock_helper.logout()

        result = auth_guard_and_logout("/any", 1)

        assert result == "/login"
