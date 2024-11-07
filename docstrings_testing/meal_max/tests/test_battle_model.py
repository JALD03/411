import pytest
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel, update_meal_stats
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


# Configure logger
logger = logging.getLogger(__name__)
configure_logger(logger)


# Test Fixtures

@pytest.fixture()
def battle_model():
    """Fixture to create a BattleModel instance."""
    return BattleModel()


@pytest.fixture()
def sample_meal1():
    """Fixture for a sample meal."""
    return Meal(id=1, meal='Pasta', price=10.5, cuisine='Italian', difficulty='MED')


@pytest.fixture()
def sample_meal2():
    """Fixture for a second sample meal."""
    return Meal(id=2, meal='Sushi', price=12.0, cuisine='Japanese', difficulty='HIGH')


@pytest.fixture()
def sample_meal3():
    """Fixture for a third sample meal."""
    return Meal(id=3, meal='Pizza', price=8.0, cuisine='Italian', difficulty='LOW')


@pytest.fixture()
def prepared_combatants(sample_meal1, sample_meal2):
    """Fixture to prepare a list of combatants."""
    return [sample_meal1, sample_meal2]


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


def test_battle_success(battle_model, prepared_combatants, mock_update_meal_stats, mock_get_random):
    """
    Test a successful battle between two combatants.
    """
    mock_get_random.return_value = 0.05
    battle_model.combatants.extend(prepared_combatants)
    winner = battle_model.battle()

    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1
    mock_update_meal_stats.assert_any_call(prepared_combatants[0].id, 'win')
    mock_update_meal_stats.assert_any_call(prepared_combatants[1].id, 'loss')


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


def test_battle_with_identical_scores(battle_model, sample_meal1, sample_meal3, mock_get_random):
    """
    Test the battle when both meals have the same score.
    """
    mock_get_random.return_value = 0.1
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal3)
    winner = battle_model.battle()

    assert winner in ['Pasta', 'Pizza']
    assert len(battle_model.combatants) == 1


def test_battle_with_close_scores(battle_model, sample_meal1, sample_meal2, mock_get_random):
    """
    Test the battle when both meals have very close scores.
    """
    mock_get_random.return_value = 0.3
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    winner = battle_model.battle()

    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1


def test_battle_with_more_than_two_combatants(battle_model, prepared_combatants, sample_meal3, mock_get_random):
    """
    Test the behavior when trying to start a battle with more than two combatants.
    """
    mock_get_random.return_value = 0.2
    battle_model.combatants.extend(prepared_combatants)
    battle_model.prep_combatant(sample_meal3)

    winner = battle_model.battle()

    assert winner in ['Pasta', 'Sushi']
    assert len(battle_model.combatants) == 1


def test_invalid_meal_data(battle_model, mock_get_random):
    """
    Test battle with invalid Meal data (e.g., missing attributes).
    """
    invalid_meal = Meal(id=4, meal=None, price=None, cuisine=None, difficulty=None)

    with pytest.raises(TypeError, match="Meal attributes cannot be None"):
        battle_model.prep_combatant(invalid_meal)
