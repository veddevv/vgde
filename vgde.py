import os
import requests
import sys
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve the RAWG API key from environment variables
API_KEY = os.getenv('RAWG_API_KEY')
BASE_URL = 'https://api.rawg.io/api'

class MissingAPIKeyError(Exception):
    """Custom exception for missing API key."""
    pass

class InvalidInputError(Exception):
    """Custom exception for invalid user input."""
    pass

def sanitize_game_name(game_name):
    """
    Validates and sanitizes the user input.

    Parameters:
    game_name (str): The name of the game to validate and sanitize.

    Returns:
    str: The sanitized game name.

    Raises:
    InvalidInputError: If the input is invalid.
    """
    if not isinstance(game_name, str):
        raise InvalidInputError("Invalid input. Game name must be a string.")

    game_name = game_name.strip()

    if not game_name:
        raise InvalidInputError("Invalid input. Please enter a non-empty game name.")

    if len(game_name) > 100:
        raise InvalidInputError("Invalid input. Game name is too long.")

    if not re.match("^[a-zA-Z0-9\s]+$", game_name):
        raise InvalidInputError("Invalid input. Game name contains invalid characters.")

    return game_name

def check_api_key():
    """
    Checks if the RAWG API key is set.

    Raises:
    MissingAPIKeyError: If the API key is not set.
    """
    if not API_KEY:
        raise MissingAPIKeyError("API key not found. Please set the RAWG_API_KEY environment variable.")

def get_game_info(game_name):
    """
    Fetches information about a game from the RAWG API.

    Parameters:
    game_name (str): The name of the game to search for.

    Returns:
    dict: A dictionary containing the game's information, or None if the game is not found.
    """
    url = f"{BASE_URL}/games"
    params = {
        'key': API_KEY,
        'search': game_name
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.Timeout:
        logging.error("The request timed out while trying to fetch game information.")
        return None
    except requests.ConnectionError:
        logging.error("A network problem occurred while trying to fetch game information.")
        return None
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            logging.error("Game not found (404).")
        else:
            logging.error(f"HTTP error occurred while trying to fetch game information: {e.response.status_code} - {e.response.reason}")
        return None
    except requests.RequestException as e:
        logging.error(f"An unexpected error occurred while trying to fetch game information: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        logging.error(f"JSON decoding error occurred while processing the response: {e}")
        return None

    # Check if the API returned any results
    if 'results' in data and isinstance(data['results'], list) and len(data['results']) > 0:
        game = data['results'][0]
        # Ensure the expected keys are in the game data and validate their types
        if all(key in game for key in ['name', 'released', 'rating']):
            if isinstance(game['name'], str) and isinstance(game['released'], str) and isinstance(game['rating'], (int, float)):
                return {
                    'name': game['name'],
                    'released': game['released'],
                    'rating': game['rating'],
                }
            else:
                logging.error("Unexpected data types in API response for game information.")
                return None
        else:
            logging.error("Unexpected data format in API response for game information.")
            return None
    else:
        logging.warning("No results found for the game.")
        return None

def display_game_info(game_info):
    """
    Displays information about a game.

    Parameters:
    game_info (dict): A dictionary containing the game's information.
    """
    if game_info:
        logging.info(f"Name: {game_info['name']}")
        logging.info(f"Released: {game_info['released']}")
        logging.info(f"Rating: {game_info['rating']}")
    else:
        logging.warning("No game information to display.")

def main():
    """
    Main function to run the script.
    Prompts the user to enter the name of a game and displays its information.
    """
    try:
        check_api_key()
    except MissingAPIKeyError as e:
        logging.error(f"API key error: {e}")
        sys.exit(1)

    try:
        game_name = input("Enter the name of the game: ")
        sanitized_game_name = sanitize_game_name(game_name)
        game_info = get_game_info(sanitized_game_name)
        display_game_info(game_info)
    except InvalidInputError as e:
        logging.error(f"Input validation error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
