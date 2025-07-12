from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime

app = Flask(__name__)

# abbreviating states
VALID_STATES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
}

# common city name patterns to validate

CITY_PATTERN = re.compile(r'^[a-zA-Z\s\-\.\']{2,50}$')

def validate_city_name(city):
    """
    This function will validate that the city name is valid! City name must
    not contain any invalid characters (city_pattern) or be shorter than two
    characters
    """
    if not city or len(city.strip()) < 2:
        return False, "The city name must be at least two characters long"
    
    if not CITY_PATTERN.match(city.strip()):
        return False, "The city name contains invalid characters"
    
    return True, None

def validate_state_code(state):
    """
    This function will validate that the state code is valid! Must have two
    letters (example WA not WAA) and must a valid state (in "valid_states)

    """
    state_upper = state.strip().upper()

    if len(state_upper) != 2:
        return False, "State must be 2-letter abbreviation"
    
    if state_upper not in VALID_STATES:
        return False, f"'{state}' is not a valid abbreviation"
    
    return True, None


print(validate_city_name("Seattle"))
print(validate_state_code("WA"))

