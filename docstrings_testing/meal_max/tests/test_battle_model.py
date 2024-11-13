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
    #Create a BattleModel instance
    return BattleModel()


@pytest.fixture()
def sample_meal1():
    #Create the first sample meal
    return Meal(id=1, meal='Pasta', price=10.5, cuisine='Italian', difficulty='MED')


@pytest.fixture()
def sample_meal2():
    #Create the second sample meal
    return Meal(id=2, meal='Sushi', price=12.0, cuisine='Japanese', difficulty='HIGH')


@pytest.fixture()
def sample_meal3():
    #Create the third sample meal
    return Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW')


def test_battle_model_initialization():
    #Test if the BattleModel Initializes everything properly
    battle_model = BattleModel()
    assert battle_model.combatants == [] 

@pytest.fixture()
def prepared_combatants(sample_meal1, sample_meal2):
    #Make a list of prepared combatants to keep for the future
    return [sample_meal1, sample_meal2]



@pytest.fixture()
def mock_update_meal_stats(mocker):
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")


@pytest.fixture()
def mock_get_random(mocker):
    return mocker.patch("meal_max.utils.random_utils.get_random")


# Tests

def test_prep_combatant(battle_model, sample_meal1):
    #Test adding combatants and making sure it does it right
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Pasta'


def test_prep_combatant_full_list(battle_model, prepared_combatants):
    #Tests adding combatants  when the list is full
    battle_model.combatants.extend(prepared_combatants)
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW'))


def test_clear_combatants(battle_model, sample_meal1):
    #Makes sure clear combatants empties the list
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


def test_battle_insufficient_combatants(battle_model):
    #Tests that the error is thrown when there is not enough combatants
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()


def test_battle_success(battle_model, prepared_combatants, mock_cursor, mock_update_meal_stats, mock_get_random):
    #Tests a normal battle, ensures everything works out
    mock_get_random.return_value = 0.42

    mock_cursor.fetchone.return_value = (0,)  # Meal is not deleted

    battle_model.combatants.extend(prepared_combatants)
    
    winner = battle_model.battle()
    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1


def test_get_battle_score(battle_model, sample_meal1):
    #Makes sure the battle score is acting normally
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2  # MED has a modifier of 2
    assert score == expected_score, f"Expected {expected_score}, but got {score}"


def test_get_combatants(battle_model, prepared_combatants):
    #Makes sure we can get our list of combatants normally
    battle_model.combatants.extend(prepared_combatants)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == 'Pasta'
    assert combatants[1].meal == 'Sushi'


def test_battle_with_more_than_two(battle_model, prepared_combatants, sample_meal3, mock_get_random):
    #Tests how the battles act when you try to add too many meals
    mock_get_random.return_value = 0.2
    battle_model.combatants.extend(prepared_combatants)
    

    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

def test_prep_duplicate_combatant(battle_model, sample_meal1):
    #Tests when you try to add the same combatant twice
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 2

def test_clear_combatants_when_empty(battle_model):
    #Tests nothing weird happening when you clear combatants when it's empty
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

def test_get_combatants_after_mods(battle_model, sample_meal1, sample_meal2):
    #Makes sure get_combatants still works after modifications
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.get_combatants()) == 2
    
    battle_model.clear_combatants()
    assert len(battle_model.get_combatants()) == 0



