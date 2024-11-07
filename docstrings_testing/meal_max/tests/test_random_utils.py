import pytest
import sqlite3

from meal_max.utils.random_utils import *

# trial unit tests
@pytest.fixture()
def mock_cursor(mocker):
    """Fixture to create a mock cursor for testing."""
    return mocker.Mock()


@pytest.fixture()
def mock_db_connection(mocker, mock_cursor):
    """Fixture to mock the database connection for testing."""
    mock_conn = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("your_db_module.get_db_connection", return_value=mock_conn)
    return mock_conn

def test_get_random(mock_cursor):