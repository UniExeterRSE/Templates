"""
Integration tests for authentication.

These tests cover:
- User registration and login flows
- Authentication state and session management
- Username validation
- Real database and password hashing

All tests use an in-memory SQLite database and Flask test context.
"""

import pytest
from werkzeug.security import generate_password_hash

from auth import User, server, user_db
from auth.authentication import (
    authenticate_user,
    get_current_username,
    is_authenticated,
    logout,
    register_user,
    username_is_valid,
)


@pytest.fixture
def app_with_db():
    """
    Flask test client with isolated in-memory database.

    Provides a complete testing environment with:
    - Flask app in testing mode with clean database per test
    - Automatic setup and teardown of database tables
    - Request context management for Flask-Login operations
    """
    server.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with server.app_context():
        user_db.create_all()
        yield server
        user_db.session.remove()
        user_db.drop_all()


@pytest.fixture
def test_user(app_with_db):
    """
    Creates a test user in the database.

    Returns:
        tuple: (user_object, plain_password) for authentication tests
    """
    username = "testuser"
    password = "password123"
    hashed_password = generate_password_hash(password)

    user = User(username, hashed_password)
    user_db.session.add(user)
    user_db.session.commit()

    yield user, password

    # Cleanup
    user_db.session.delete(user)
    user_db.session.commit()


class TestAuthenticationFlow:
    """Tests for complete authentication workflows."""

    def test_successful_authentication_flow(self, app_with_db, test_user, mocker):
        """Test complete successful authentication including user directory creation."""
        user, password = test_user
        mock_create_directory = mocker.patch(
            "auth.authentication.create_user_directory"
        )

        with app_with_db.test_request_context():
            success, message = authenticate_user("testuser", password)

        assert success is True
        assert message == "Login successful. Redirecting..."
        mock_create_directory.assert_called_once_with("testuser")

    def test_authentication_with_invalid_username(self, app_with_db):
        """Test authentication fails with non-existent username."""
        with app_with_db.test_request_context():
            success, message = authenticate_user("nonexistent", "password")

        assert success is False
        assert message == "Invalid username or password."

    def test_authentication_with_invalid_password(self, app_with_db, test_user):
        """Test authentication fails with wrong password."""
        user, password = test_user

        with app_with_db.test_request_context():
            success, message = authenticate_user("testuser", "wrongpassword")

        assert success is False
        assert message == "Invalid username or password."


class TestAuthenticationState:
    """Tests for authentication state management."""

    def test_is_authenticated_after_login(self, app_with_db, test_user):
        """Test user is authenticated after successful login."""
        user, password = test_user

        with app_with_db.test_request_context():
            success, message = authenticate_user("testuser", password)
            assert success is True
            assert is_authenticated() is True

    def test_is_authenticated_without_login(self, app_with_db):
        """Test user is not authenticated without login."""
        with app_with_db.test_request_context():
            assert is_authenticated() is False

    def test_get_username_when_authenticated(self, app_with_db, test_user):
        """Test current username retrieval after authentication."""
        user, password = test_user

        with app_with_db.test_request_context():
            success, message = authenticate_user("testuser", password)
            assert success is True
            assert get_current_username() == "testuser"

    def test_get_username_when_not_authenticated(self, app_with_db):
        """Test get_current_username raises exception when not authenticated."""
        with app_with_db.test_request_context():
            with pytest.raises(ValueError, match="No authenticated user found"):
                get_current_username()

    def test_logout_functionality(self, app_with_db):
        """Test logout works without errors in request context."""
        with app_with_db.test_request_context():
            logout()  # Should not raise any exceptions


class TestUserRegistration:
    """Tests for user registration functionality."""

    def test_register_new_user(self, app_with_db):
        """Test successful registration of new user."""
        with app_with_db.test_request_context():
            success, message = register_user("newuser", "password123")

        assert success is True
        assert (
            message
            == "Registration successful. You can now log in with your new account."
        )

        # Verify user exists in database
        with app_with_db.test_request_context():
            new_user = User.query.filter_by(username="newuser").first()
            assert new_user is not None
            assert new_user.username == "newuser"

    def test_register_existing_user(self, app_with_db, test_user):
        """Test registration fails with existing username."""
        user, password = test_user

        with app_with_db.test_request_context():
            success, message = register_user("testuser", "newpassword")

        assert success is False
        assert message == "Username already exists"


class TestUsernameValidation:
    """Tests for username validation functionality."""

    def test_username_validation_for_new_user(self, app_with_db):
        """Test username validation returns True for available username."""
        with app_with_db.test_request_context():
            result = username_is_valid("brandnewuser")

        assert result is True

    def test_username_validation_for_existing_user(self, app_with_db, test_user):
        """Test username validation returns False for existing username."""
        user, password = test_user

        with app_with_db.test_request_context():
            result = username_is_valid("testuser")

        assert result is False
