#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

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
  name=$1
  cuisine=$2
  price=$3
  dificulty=$4

  echo "Adding meal ($meal - $cuisine, $price) to the database..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'


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

  curl -s -X POST "$BASE_URL/clear-meals" | grep -q '"status": "success"'

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
  sort_by = $1 

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

  response=$(curl -s -G "$BASE_URL/get-meal-by-id" --data-urlencode "meal_id=$meal_id")

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

  response=$(curl -s -X PUT "$BASE_URL/update-meal-stats/$meal_id" -d "{\"result\": \"$result\"}")

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
  response=$(curl -s -X POST "$BASE_URL/prep-combtatant" \
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