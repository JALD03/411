import pytest
import sqlite3
import pytest
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel
from meal_max.utils.logger import configure_logger
from meal_max.models.battle_model import *

# trial unit tests
@pytest.fixture()
def mock_cursor(mocker):
    return mocker.Mock()


@pytest.fixture()
def mock_db_connection(mocker, mock_cursor):
    mock_conn = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("your_db_module.get_db_connection", return_value=mock_conn)
    return mock_conn

@pytest.fixture
def battle_model():
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal='Pasta', price=10.5, cuisine='Italian', difficulty='MED')

@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal='Sushi', price=12.0, cuisine='Japanese', difficulty='HIGH')

@pytest.fixture
def prepared_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


def test_prep_combatant(battle_model, sample_meal1):
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Pasta'

def test_prep_combatant_full_list(battle_model, prepared_combatants):
    battle_model.combatants.extend(prepared_combatants)
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW'))

def test_clear_combatants(battle_model, sample_meal1):
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

def test_battle_insufficient_combatants(battle_model):
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

# Edit this to match the style
def test_battle_success(battle_model, prepared_combatants, mock_update_meal_stats, mocker):
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.05)
    battle_model.combatants.extend(prepared_combatants)
    winner = battle_model.battle()
    
    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1
    mock_update_meal_stats.assert_any_call(prepared_combatants[0].id, 'win')
    mock_update_meal_stats.assert_any_call(prepared_combatants[1].id, 'loss')


def test_get_battle_score(battle_model, sample_meal1):
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2  # MED has a modifier of 2
    assert score == expected_score, f"Expected {expected_score}, but got {score}"

def test_get_combatants(battle_model, prepared_combatants):
    battle_model.combatants.extend(prepared_combatants)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == 'Pasta'
    assert combatants[1].meal == 'Sushi'