import pytest

from tests.test_helpers import (
    AuthenticationMockHelper,
    FileUtilitiesMockHelper,
)


@pytest.fixture(autouse=True)
def auth_mock_helper(mocker) -> AuthenticationMockHelper:
    return AuthenticationMockHelper(mocker)


@pytest.fixture(autouse=True)
def file_util_mock_helper(mocker) -> FileUtilitiesMockHelper:
    return FileUtilitiesMockHelper(mocker)
