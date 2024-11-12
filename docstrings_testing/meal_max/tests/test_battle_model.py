import pytest
import sqlite3
from contextlib import contextmanager
from meal_max.models.kitchen_model import Meal, create_meal
from meal_max.models.battle_model import BattleModel, update_meal_stats
from meal_max.utils.random_utils import get_random
from meal_max.utils.sql_utils import get_db_connection



# Test Fixtures

@pytest.fixture
def mock_cursor(mocker):
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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

@pytest.fixture()
def battle_model():
    """Fixture to create a BattleModel instance."""
    return BattleModel()


@pytest.fixture()
def sample_meal1():
    """Fixture for a sample meal."""
    #create_meal(meal='Pasta', cuisine='Italian', price=10.5, difficulty='MED')
    return Meal(id=1, meal='Pasta', price=10.5, cuisine='Italian', difficulty='MED')


@pytest.fixture()
def sample_meal2():
    """Fixture for a second sample meal."""
    
    #create_meal(meal='Suhi', cuisine='Japanese', price=12.0, difficulty='HIGH')
    return Meal(id=2, meal='Sushi', price=12.0, cuisine='Japanese', difficulty='HIGH')


@pytest.fixture()
def sample_meal3():
    """Fixture for a third sample meal."""
    #create_meal(meal='Pizza', cuisine='Italian', price=8.0, difficulty='LOW')
    return Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW')


@pytest.fixture()
def prepared_combatants(sample_meal1, sample_meal2):
    """Fixture to prepare a list of combatants."""
    return [sample_meal1, sample_meal2]

@pytest.fixture()
def prepared_combatants2(sample_meal1, sample_meal3):
    """Fixture to prepare a list of combatants."""
    return [sample_meal1, sample_meal3]


@pytest.fixture()
def mock_update_meal_stats(mocker):
    """Fixture to mock update_meal_stats."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")


@pytest.fixture()
def mock_get_random(mocker):
    """Fixture to mock get_random."""
    return mocker.patch("meal_max.utils.random_utils.get_random")


# Tests

def test_prep_combatant(battle_model, sample_meal1):
    """
    Test adding a combatant to the battle model.
    """
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Pasta'


def test_prep_combatant_full_list(battle_model, prepared_combatants):
    """
    Test adding a combatant when the list is full.
    """
    battle_model.combatants.extend(prepared_combatants)
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW'))


def test_clear_combatants(battle_model, sample_meal1):
    """
    Test clearing the combatants list.
    """
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


def test_battle_insufficient_combatants(battle_model):
    """
    Test starting a battle with not enough combatants.
    """
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()


def test_battle_success(battle_model, prepared_combatants, mock_cursor, mock_update_meal_stats, mock_get_random):
    """
    Test a successful battle between two combatants.
    """
    mock_get_random.return_value = 0.42
    mock_cursor.fetchall.side_effect = [
        (prepared_combatants[0].id, "Pasta", "Italian", 10.5, "MED"),
        (prepared_combatants[1].id, "Sushi", "Japanese", 12.0, "HIGH")
    ]

    mock_cursor.fetchone.return_value = (0,)  # Meal is not deleted

    battle_model.combatants.extend(prepared_combatants)
    
    winner = battle_model.battle()
    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1


def test_get_battle_score(battle_model, sample_meal1):
    """
    Test the calculation of battle score.
    """
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2  # MED has a modifier of 2
    assert score == expected_score, f"Expected {expected_score}, but got {score}"


def test_get_combatants(battle_model, prepared_combatants):
    """
    Test retrieving the list of combatants.
    """
    battle_model.combatants.extend(prepared_combatants)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == 'Pasta'
    assert combatants[1].meal == 'Sushi'


def test_battle_with_identical_scores(battle_model, prepared_combatants2, mock_get_random, mock_cursor):
    """
    Test the battle when both meals have the same score.
    """
    mock_get_random.return_value = 0.1
    battle_model.combatants.extend(prepared_combatants2)
    mock_cursor.fetchone.return_value = (0,) 
    winner = battle_model.battle()

    assert winner in ['Pasta', 'Pizza']
    assert len(battle_model.combatants) == 1





def test_battle_with_close_scores(battle_model, prepared_combatants, mock_get_random, mock_cursor):
    """
    Test the battle when both meals have very close scores.
    """
    mock_get_random.return_value = 0.3
    battle_model.combatants.extend(prepared_combatants)
    mock_cursor.fetchone.return_value = (0,) 
    winner = battle_model.battle()
    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1


def test_battle_with_more_than_two_combatants(battle_model, prepared_combatants, sample_meal3, mock_get_random):
    """
    Test the behavior when trying to start a battle with more than two combatants.
    """
    mock_get_random.return_value = 0.2
    battle_model.combatants.extend(prepared_combatants)
    

    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)


