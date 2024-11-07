import pytest
import sqlite3
from contextlib import contextmanager
import re 



from meal_max.models.kitchen_model import *

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()


@pytest.fixture
def mock_cursor(mocker):
    """Fixture to create a mock cursor and database connection."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []  
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch('meal_max.models.kitchen_model.get_db_connection', mock_get_db_connection)

    return mock_cursor  # Return the mock cursor for test configuration


# __post_init__ testing 

def test_meal_valid_init():
    """
    Tests creating a Meal with valid attributes
    """

    meal_2_test = Meal(id=1, meal="Chicken Tikka Masala", cuisine="Indian", price=14.99, difficulty="MED")

    assert meal_2_test.id == 1
    assert meal_2_test.meal == "Chicken Tikka Masala"
    assert meal_2_test.cuisine == "Indian"
    assert meal_2_test.price == 14.99
    assert meal_2_test.difficulty == "MED"


def test_meal_invalid_price():
    """ 
    Tests creating a Meal with non-negative price to ensure it raises a ValueError
    """

    #Attempt to create a Meal with a negative float price
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=1, meal="Chicken Tikka Masala", cuisine="Indian", price = -14.99, difficulty="MED")


def test_meal_invalid_dif():
    """
    Tests creating a Meal with invalid difficulty level to ensure it raises a ValueError 
    """
    
    #tests with a difficulty outside of the specified list 
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Chicken Tikka Masala", cuisine="Indian", price = 14.99, difficulty="OKAYISH")

    #Attempt to create a Meal with a non-string difficulty 
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Chicken Tikka Masala", cuisine="Indian", price = 14.99, difficulty=10)



#create_meal tests

def test_create_meal(mock_cursor):
    """Test creating a new meal in the kitchen model."""

    # Call the function to create a new meal
    create_meal("Burger", "American", 15.99, "MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Burger", "American", 15.99, "MED")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."



def test_invalid_price():
    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Burger", "American", -15.99, "LOW")

    # Attempt to create a meal with a 0 price
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Burger", "American", 0, "LOW")
    
    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Burger", "American", "eepy", "LOW")

def test_invalid_dif():
    # Attempt to create a meal with an invalid difficulty 
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Burger", "American", 15.99, "LOWi")
    
    # Attempt to create a meal with a non-string difficulty 
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Burger", "American", 15.99, 77)

def test_duplicate_meal(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.IntegrityError

    #Attempts with meal already created in the database 
    with pytest.raises(ValueError, match="Meal with name"):
        create_meal("Burger", "American", 15.99, "LOW")


# clear_meal tests 


def test_clear_meals_success(mocker, mock_cursor):
    """
    Tests if meal clearing was successful 
    """

    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': '/app/sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals..."))

    # call function
    clear_meals()


    # checks if SQL file opened correctly 
    mock_open.assert_called_once_with("/app/sql/create_meal_table.sql", "r")

    # checks if SQL file executed 
    mock_cursor.executescript.assert_called_once_with("CREATE TABLE meals...")

    # checks if transaction comiited 
    










# delete_meal tests

def test_delete_meal_success(mock_cursor):
    """
    Attempt to delete a meal from the database by meal ID
    """

    # Simulate that the meal exists (id = 1) and is NOT marked as deleted
    mock_cursor.fetchone.return_value = (False,)

    # Delete the meal
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_sql = "UPDATE meals SET deleted = TRUE WHERE id = ?"

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_sql = mock_cursor.execute.call_args_list[1][0][0]

    # Ensure the correct SQL queries were executed
    assert actual_select_sql.strip() == expected_select_sql.strip(), "The SELECT query did not match the expected structure."
    assert actual_update_sql.strip() == expected_update_sql.strip(), "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_meal_already_deleted(mock_cursor):
    """
    Attempt to delete a meal already marked as deleted 
    """

    # Simulate that the meal exists (id = 1) and is marked as deleted
    mock_cursor.fetchone.return_value = (True,)

    #Ensure ValueError is raised for an already deleted meal
    with pytest.raises(ValueError, match="has been deleted"):
        delete_meal(1)


def test_delete_meal_invalid_id(mock_cursor):
    """
    Attempt to delete a meal with an id that does not exist 
    """

    # Simulate meal not existing
    mock_cursor.fetchone.return_value = None

    # Ensure ValueError is raised for a non-existent meal
    with pytest.raises(ValueError, match="not found"):
        delete_meal(1)


def test_get_learderboard_win_sort(mock_cursor):
    """
    Test getting a leaderboard sorted by number of wins 
    """

    # Simuluate databse rows 
    mock_cursor.fetchall.return_value = [
        (1, 'Borsch', 'Ukrainian', 12.99, 'MED', 5, 4, 0.8),
        (2, 'Limoncello Al Farfalle', 'Italian', 24.99, 'HIGH', 20, 12, 0.6)
    ]

    # call the function
    leaderboard = get_leaderboard("wins")

     # Expected output format
    expected_leaderboard = [
        {'id': 1, 'meal': 'Borsch', 'cuisine': 'Ukrainian', 'price': 12.99, 'difficulty': 'MED', 'battles': 5, 'wins': 4, 'win_pct': 80.0},
        {'id': 2, 'meal': 'Limoncello Al Farfalle', 'cuisine': 'Italian', 'price': 24.99, 'difficulty': 'HIGH', 'battles': 20, 'wins': 12, 'win_pct': 60.0}
    ] 
    
    print("Actual leaderboard:", leaderboard)

    # Verify output against expected
    assert leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {leaderboard}"

    # Verify correct arguments were used in SQL query 
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals
        WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."



def test_get_learderboard_win_pct_sort(mock_cursor):
    """
    Test getting a leaderboard sorted by percentage of wins 
    """

    # Simuluate databse rows 
    mock_cursor.fetchall.return_value = [
        (1, 'Borsch', 'Ukrainian', 12.99, 'MED', 5, 4, 0.8),
        (2, 'Limoncello Al Farfalle', 'Italian', 24.99, 'HIGH', 20, 12, 0.6)
    ]

    # call the function
    leaderboard = get_leaderboard("win_pct")

     # Expected output format
    expected_leaderboard = [
        {'id': 1, 'meal': 'Borsch', 'cuisine': 'Ukrainian', 'price': 12.99, 'difficulty': 'MED', 'battles': 5, 'wins': 4, 'win_pct': 80.0},
        {'id': 2, 'meal': 'Limoncello Al Farfalle', 'cuisine': 'Italian', 'price': 24.99, 'difficulty': 'HIGH', 'battles': 20, 'wins': 12, 'win_pct': 60.0}
    ]

    # Verify output against expected
    assert leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {leaderboard}"


    # Verify correct arguments were used in SQL query 
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals
        WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_invalid_sort_by():
    """ 
    Tests a leaderboard request with an invalid 'sort_by' to ensure ValueError is raised
    """

    # Attempts with a faulty parameter 
    with pytest.raises(ValueError, match="Invalid sort_by parameter"):
        get_leaderboard("invalid_sort")



# get_meal_by_id

def test_get_meal_by_id_success(mock_cursor):
    """
    Tests retreiving a Meal by a valid id 
    """
    # Mock a valid Meal database row
    mock_cursor.fetchone.return_value = (1, 'Borscht', 'Ukrainian', 12.99, 'MED', False)

    # Call function
    meal = get_meal_by_id(1)

    # Creates expected result 
    expected_meal = Meal(id=1, meal='Borscht', cuisine='Ukrainian', price=12.99, difficulty='MED')

    # Verify that the returned meal and expected meal are the same 
    assert meal.id == expected_meal.id
    assert meal.meal == expected_meal.meal
    assert meal.cuisine == expected_meal.cuisine
    assert meal.price == expected_meal.price
    assert meal.difficulty == expected_meal.difficulty



def test_get_meal_by_id_deleted(mock_cursor):
    """ 
    Tests getting a meal by id marked as deleted, ensuring it raises a ValueError
    """

    # Mock a valid Meal database row with a True 'deleted' flag
    mock_cursor.fetchone.return_value = (1, 'Borscht', 'Ukrainian', 12.99, 'MED', True)

    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_id(1)


def test_get_meal_by_id_nonexistent(mock_cursor):
    """ Tests retrieving a meal by id that doesn't exist """

    # Mock a meal that isn't
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_meal_by_id(999)


# get_meal_by_name 

def test_get_meal_by_id_success(mock_cursor):
    """
    Tests retreiving a Meal by a valid id 
    """
    # Mock a valid Meal database row
    mock_cursor.fetchone.return_value = (1, 'Borscht', 'Ukrainian', 12.99, 'MED', False)

    # Call function
    meal = get_meal_by_name("Borscht")

    # Creates expected result 
    expected_meal = Meal(id=1, meal='Borscht', cuisine='Ukrainian', price=12.99, difficulty='MED')

    # Verify that the returned meal and expected meal are the same 
    assert meal.id == expected_meal.id
    assert meal.meal == expected_meal.meal
    assert meal.cuisine == expected_meal.cuisine
    assert meal.price == expected_meal.price
    assert meal.difficulty == expected_meal.difficulty


def test_get_meal_by_id_deleted(mock_cursor):
    """ 
    Tests getting a meal marked as deleted by name, ensuring it raises a ValueError
    """

    # Mock a valid Meal database row with a True 'deleted' flag
    mock_cursor.fetchone.return_value = (1, 'Borscht', 'Ukrainian', 12.99, 'MED', True)

    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_name("Borscht")


def test_get_meal_by_id_nonexistent(mock_cursor):
    """ Tests retrieving a meal by name that doesn't exist """

    # Mock a meal that isn't
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("EPEPEPEPEPEPEPEPEPEPEPEPEEPEEEEEPEEEPEEEP")


# update_meal_stats

def test_update_meal_stats_win(mock_cursor):
    """ 
    Testing updating the meal stats with a win 
    """

    # Mock the mean being not deleted 
    mock_cursor.fetchone.return_value = (False,)

    # call function with a 'win' result 
    update_meal_stats(1, 'win')

    # Update meal stats with a win
    update_meal_stats(1, 'win')
    
    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_sql = "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?"

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_sql = mock_cursor.execute.call_args_list[1][0][0]

    # Ensure the correct SQL queries were executed
    assert actual_select_sql.strip() == expected_select_sql.strip(), "The SELECT query did not match the expected structure."
    assert actual_update_sql.strip() == expected_update_sql.strip(), "The UPDATE query for win did not match the expected structure."

    # Ensure the correct arguments were used
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments for win did not match. Expected {expected_update_args}, got {actual_update_args}."



def test_update_meal_stats_loss(mock_cursor):
    """
    Test updating meal stats with a loss.        """
    
    # Simulate that the meal exists (id = 1) and is NOT marked as deleted
    mock_cursor.fetchone.return_value = (False,)
    
    # Update meal stats with a loss
    update_meal_stats(1, 'loss')

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_sql = "UPDATE meals SET battles = battles + 1 WHERE id = ?"

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_sql = mock_cursor.execute.call_args_list[1][0][0]

     # Ensure the correct SQL queries were executed
    assert actual_select_sql.strip() == expected_select_sql.strip(), "The SELECT query did not match the expected structure."
    assert actual_update_sql.strip() == expected_update_sql.strip(), "The UPDATE query for loss did not match the expected structure."

    # Ensure the correct arguments were used
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments for loss did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_update_meal_stats_deleted(mock_cursor):
    """ 
    Test updating stats of a deleted meal, should raise a ValuError 
    """

    # Mock a meal that exists but is flagged as deleted 
    mock_cursor.fetchone.return_value = (True,)

    with pytest.raises(ValueError, match="has been deleted"):
        update_meal_stats(1, 'win')


def test_update_meal_stats_nonexistent(mock_cursor):
    """ 
    Test updating a meal that's been deleted, should raise a ValueError
    """
    # Simulate a meal that isn't
    mock_cursor.fetchone.side_effect = TypeError() 

    with pytest.raises(ValueError, match="not found"):
        update_meal_stats(1, 'win')



def test_update_meal_stats_invalid_result(mock_cursor):
    """ 
    Test updating a meal with an invalid result, should raise a ValueError
    """

    # Simulate a meal with an id that has not been deleted
    mock_cursor.fetchone.return_value = (False,)

    with pytest.raises(ValueError, match="Invalid result: invalid_result. Expected 'win' or 'loss'."):
        update_meal_stats(1, 'invalid_result')

