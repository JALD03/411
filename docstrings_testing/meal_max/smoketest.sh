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

  echo "Retrieving leaderboard sorted by: $sort_by..."

  response=$(curl -s -G "$BASE_URL/leaderboard" \
    -H "Content-Type: application/json" \
    --data-urlencode "sort=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Successfully retrieved leaderboard sorted by $sort_by."
    echo "Leaderboard: $response"
  else
    echo "Failed to retrieve leaderboard."
    echo "Response: $response"
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

  echo "Preparing combatant for meal: $meal..."

  # Make a POST request to the /api/prep-combatant route
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully for meal: $meal."
  elif echo "$response" | grep -q '"error": "Combatant list is full, cannot add more combatants."'; then
    echo "Cannot add combatant: Combatant list is full."
  else
    echo "Failed to prepare combatant for meal: $meal."
    echo "Response: $response"
    exit 1
  fi
}

###############################################
#
# Combatant Addition Tests
#
###############################################


battle() {
  echo "Initiating battle with current combatants..."

  response=$(curl -s -X GET "$BASE_URL/battle" -H "Content-Type: application/json")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle executed successfully."
    
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle JSON response:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error": "Two combatants must be prepped for a battle."'; then
    echo "Battle initiation failed: Two combatants must be prepped for a battle."
  else
    echo "Failed to begin the battle."
    echo "Response: $response"
    exit 1
  fi
}

get_combatants() {
  echo "Retrieving the current list of combatants..."

 
  response=$(curl -s -X GET "$BASE_URL/get-combatants" \
    -H "Content-Type: application/json")

  if echo "$response" | grep -q '"combatants"'; then
    echo "Successfully retrieved the current list of combatants."
    echo "Combatants: $response"
  else
    echo "Failed to retrieve the current list of combatants."
    echo "Response: $response"
    exit 1
  fi
}




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
  echo "Clearing the combatants list..."
  
  response=$(curl -s -X POST "$BASE_URL/clear-combatants" \
    -H "Content-Type: application/json")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    echo "Response: $response"
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


clear_combatants

get_combatants




#here 
prep_combatant "Burger"

# battle with 1 - should fail
battle


prep_combatant "Geese" 

# adding 3rd - should fail
prep_combatant "Hawaiian Pizza"


clear_combatants


prep_combatant "Burger"
prep_combatant "Tikka Masala" 

get_combatants

#battle with 2
battle


get_leaderboard "wins"
get_leaderboard "win_pct"

echo "All tests passed (or intentionally failed) successfully!"






