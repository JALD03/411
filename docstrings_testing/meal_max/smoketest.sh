#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://127.0.0.1:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


# Meal Management

# create_meal 

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the database..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'


  # if added, then it will exit with a 0
  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}


clear_meals() {
  echo "Clearing meals from database..."

  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'

}


delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."

  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi

}


get_leaderboard() {
  sort_by=$1 

  echo "Retreiving leaderboard sorted by $sort_by..."

  response=$(curl -s -G "$BASE_URL/get-leaderboard" --data-urlencode "sort_by=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully:"
  
  else
    echo "Failed to retrieve leaderboard. Response:"
    exit 1
  fi

}


get_meal_by_id() {
  meal_id=$1

  echo "Retrieving meal by ID ($meal_id)..."

  response=$(curl -s "$BASE_URL/get-meal-by-id/$meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}


get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}


update_meal_stats() {
  meal_id=$1
  result=$2

  echo "Updating meal stats for meal ID ($meal_id) with result ($result)..."

  response=$(curl -s -X PUT "$BASE_URL/update-meal-stats/$meal_id" \
    -H "Content-Type: application/json" \
    -d "{\"result\": \"$result\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal stats updated successfully for meal ID ($meal_id)."
  else
    echo "Failed to update meal stats for meal ID ($meal_id)."
    exit 1
  fi
}


##########################################################
#
# Battle Management
#
##########################################################

prep_combatant() {
  meal=$1
  cuisine=$2
  price=$3

  echo "Adding combatant to battle: $meal - $cuisine ($price)..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to battle successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to battle."
    exit 1
  fi
}

###############################################
#
# Combatant Addition Tests
#
###############################################

# Test adding one combatant
add_one_combatant() {
  echo "Adding one combatant..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
battle_model = BattleModel()
battle_model.prep_combatant(combatant)
print('PASS' if len(battle_model.get_combatants()) == 1 else 'FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Successfully added one combatant: PASS"
  else
    echo "Failed to add combatant: FAIL"
    exit 1
  fi
}

# Test adding two combatants
add_two_combatants() {
  echo "Adding two combatants..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant1 = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
combatant2 = Meal(id=2, meal='Sushi', price=12, cuisine='Japanese', difficulty='HIGH')
battle_model = BattleModel()
battle_model.prep_combatant(combatant1)
battle_model.prep_combatant(combatant2)
print('PASS' if len(battle_model.get_combatants()) == 2 else 'FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Successfully added two combatants: PASS"
  else
    echo "Failed to add two combatants: FAIL"
    exit 1
  fi
}

# Test trying to add a third combatant (should fail)
add_third_combatant() {
  echo "Trying to add a third combatant..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant1 = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
combatant2 = Meal(id=2, meal='Sushi', price=12, cuisine='Japanese', difficulty='HIGH')
combatant3 = Meal(id=3, meal='Tacos', price=8, cuisine='Mexican', difficulty='LOW')
battle_model = BattleModel()
battle_model.prep_combatant(combatant1)
battle_model.prep_combatant(combatant2)
response = 'FAIL'
try:
    battle_model.prep_combatant(combatant3)
except ValueError:
    response = 'PASS'
print(response)
")
  if [ "$response" == "PASS" ]; then
    echo "Attempting to add more than two combatants raises ValueError: PASS"
  else
    echo "Failed to catch attempt to add a third combatant: FAIL"
    exit 1
  fi
}

###############################################
#
# Battle Tests
#
###############################################

# Test battle with insufficient combatants
battle_with_insufficient_combatants() {
  echo "Testing battle with insufficient combatants..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

battle_model = BattleModel()
try:
    battle_model.battle()
    print('FAIL')
except ValueError:
    print('PASS')
")
  if [ "$response" == "PASS" ]; then
    echo "Battle with insufficient combatants raises ValueError: PASS"
  else
    echo "Insufficient combatants check failed: FAIL"
    exit 1
  fi
}

# Test battle with two combatants
battle_with_two_combatants() {
  echo "Starting a battle with two combatants..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

battle_model = BattleModel()
combatant1 = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
combatant2 = Meal(id=2, meal='Sushi', price=12, cuisine='Japanese', difficulty='HIGH')
battle_model.prep_combatant(combatant1)
battle_model.prep_combatant(combatant2)
try:
    winner = battle_model.battle()
    print('PASS' if winner in [combatant1.meal, combatant2.meal] else 'FAIL')
except Exception:
    print('FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Battle with two combatants completed successfully: PASS"
  else
    echo "Battle with two combatants failed: FAIL"
    exit 1
  fi
}

battle_with_three_combatants() {
  echo "Trying to start a battle with three combatants..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant1 = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
combatant2 = Meal(id=2, meal='Sushi', price=12, cuisine='Japanese', difficulty='HIGH')
combatant3 = Meal(id=3, meal='Tacos', price=8, cuisine='Mexican', difficulty='LOW')
battle_model = BattleModel()
battle_model.prep_combatant(combatant1)
battle_model.prep_combatant(combatant2)

response = 'FAIL'
try:
    battle_model.prep_combatant(combatant3)
except ValueError:
    response = 'PASS'

print(response)
")
  if [ "$response" == "PASS" ]; then
    echo "Attempting to start a battle with three combatants raises ValueError: PASS"
  else
    echo "Failed to catch attempt to start a battle with three combatants: FAIL"
    exit 1
  fi
}

# Test that a battle results in one combatant being removed
battle_removes_loser() {
  echo "Testing that a loser is removed from combatants list..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

battle_model = BattleModel()
combatant1 = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
combatant2 = Meal(id=2, meal='Sushi', price=12, cuisine='Japanese', difficulty='HIGH')
battle_model.prep_combatant(combatant1)
battle_model.prep_combatant(combatant2)
winner = battle_model.battle()
remaining_combatants = battle_model.get_combatants()
print('PASS' if len(remaining_combatants) == 1 and winner.meal in [combatant1.meal, combatant2.meal] else 'FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Loser successfully removed after battle: PASS"
  else
    echo "Failed to remove loser after battle: FAIL"
    exit 1
  fi
}

###############################################
#
# Score Calculation Tests
#
###############################################

# Test battle score calculation (valid combatant data)
calculate_battle_score_valid() {
  echo "Testing valid battle score calculation..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
battle_model = BattleModel()
score = battle_model.get_battle_score(combatant)
print('PASS' if score > 0 else 'FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Valid battle score calculated: PASS"
  else
    echo "Invalid battle score calculation: FAIL"
    exit 1
  fi
}

# Test battle score calculation with invalid difficulty level
calculate_battle_score_invalid_difficulty() {
  echo "Testing battle score calculation with invalid difficulty..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

combatant = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='INVALID')
battle_model = BattleModel()
try:
    score = battle_model.get_battle_score(combatant)
    print('FAIL')
except KeyError:
    print('PASS')
")
  if [ "$response" == "PASS" ]; then
    echo "Invalid difficulty level handled correctly: PASS"
  else
    echo "Invalid difficulty level handling failed: FAIL"
    exit 1
  fi
}

###############################################
#
# Combatant Clearing Tests
#
###############################################

# Test clearing combatants
clear_combatants() {
  echo "Clearing combatants list..."
  response=$(python3 -c "
from meal_max.models.kitchen_model import Meal
from meal_max.battle.battle_model import BattleModel

battle_model = BattleModel()
combatant = Meal(id=1, meal='Pasta', price=10, cuisine='Italian', difficulty='MED')
battle_model.prep_combatant(combatant)
battle_model.clear_combatants()
print('PASS' if len(battle_model.get_combatants()) == 0 else 'FAIL')
")
  if [ "$response" == "PASS" ]; then
    echo "Combatants cleared successfully: PASS"
  else
    echo "Failed to clear combatants: FAIL"
    exit 1

  fi 
}




check_health
check_db


create_meal "Burger" "American" 15.99 "MED"
create_meal "Tikka Masala" "Indian" 12.99 "LOW"
create_meal "Pizza" "Italian" 29.99 "HIGH" 
create_meal "Geese" "Silly" 1000 "HIGH" 
create_meal "Hawaiian Pizza" "Sin" 1 "LOW" 

delete_meal 1 

clear_meals


create_meal "Burger" "American" 15.99 "MED"
create_meal "Tikka Masala" "Indian" 12.99 "LOW"
create_meal "Pizza" "Italian" 29.99 "HIGH" 
create_meal "Geese" "Silly" 1000 "HIGH" 
create_meal "Hawaiian Pizza" "Sin" 1 "LOW" 


get_meal_by_id 1
get_meal_by_name "Pizza"









#here 
prep_combatant "Burger" "American" 15.99
battle_with_insufficient_combatants

prep_combatant "Tikka Masala" "Indian" 12.99
battle_with_two_combatants


battle_removes_loser

prep_combatant "Pizza" "Italian" 29.99
prep_combatant "Geese" "Silly" 1000.0
battle_with_three_combatants



get_leaderboard "win"
get_leaderboard "win_pct"



calculate_battle_score_valid
calculate_battle_score_invalid_difficulty

clear_combatants 

echo "All tests passed successfully!"






