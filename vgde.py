import os
import requests
import sys
import logging
import re
from argparse import ArgumentParser
from typing import Optional, Dict

# Constants
MAX_GAME_NAME_LENGTH = 100
GAME_NAME_PATTERN = r"^[a-zA-Z0-9\s]+$"
DEFAULT_REQUEST_TIMEOUT = 10

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve the RAWG API key from environment variables
API_KEY = os.getenv('RAWG_API_KEY')
BASE_URL = 'https://api.rawg.io/api'
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT))

class MissingAPIKeyError(Exception):
    """Custom exception for missing API key."""
    pass

class InvalidInputError(Exception):
    """Custom exception for invalid user input."""
    pass

def sanitize_game_name(game_name: str) -> str:
    """
    Validates and sanitizes the user input.
    """
    if not isinstance(game_name, str):
        raise InvalidInputError("Invalid input. Game name must be a string.")

    game_name = game_name.strip()

    if not game_name:
        raise InvalidInputError("Invalid input. Please enter a non-empty game name.")

    if len(game_name) > MAX_GAME_NAME_LENGTH:
        raise InvalidInputError("Invalid input. Game name is too long.")

    if not re.match(GAME_NAME_PATTERN, game_name):
        raise InvalidInputError("Invalid input. Game name contains invalid characters.")

    return game_name

def check_api_key() -> None:
    """
    Checks if the RAWG API key is set.
    """
    if not API_KEY or API_KEY.strip() == "":
        logging.error("API key not found. Please set the RAWG_API_KEY environment variable.")
        raise MissingAPIKeyError("API key not found. Please set the RAWG_API_KEY environment variable.")

def fetch_game_data(game_name: str) -> Optional[Dict[str, object]]:
    """
    Fetches game data from the RAWG API.
    """
    url = f"{BASE_URL}/games"
    params = {'key': API_KEY, 'search': game_name}

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error(f"The request timed out while trying to fetch game information for '{game_name}'.")
    except requests.exceptions.ConnectionError:
        logging.error(f"A network problem occurred while trying to fetch game information for '{game_name}'.")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred while trying to fetch game information for '{game_name}': {e.response.status_code} - {e.response.reason}")
        logging.error(f"Response content: {e.response.content}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An unexpected error occurred while trying to fetch game information for '{game_name}': {e}")
    except ValueError as e:
        logging.error(f"JSON decoding error occurred while processing the response for '{game_name}': {e}")

    return None

def parse_game_info(data: Dict[str, object]) -> Optional[Dict[str, object]]:
    """
    Parses the game information from the API response.
    """
    if 'results' in data and isinstance(data['results'], list) and data['results']:
        game = data['results'][0]
        if all(key in game for key in ['name', 'released', 'rating']):
            if isinstance(game['name'], str) and isinstance(game['released'], str) and isinstance(game['rating'], (int, float)):
                return {key: game[key] for key in ['name', 'released', 'rating']}
            else:
                logging.error("Unexpected data types in API response for game information.")
        else:
            logging.error("Unexpected data format in API response for game information.")
    else:
        logging.warning("No results found for the game.")

    return None

def display_game_info(game_info: Optional[Dict[str, object]]) -> None:
    """
    Displays information about a game.
    """
    if game_info:
        logging.info(f"Name: {game_info['name']}")
        logging.info(f"Released: {game_info['released']}")
        logging.info(f"Rating: {game_info['rating']}")
    else:
        logging.warning("No game information to display.")

def main() -> Optional[Dict[str, object]]:
    """
    Main function to run the script.
    Prompts the user to enter the name of a game and displays its information.
    """
    parser = ArgumentParser(description="Fetch game information from RAWG API.")
    parser.add_argument('game_name', type=str, help="The name of the game to search for.")
    args = parser.parse_args()

    try:
        check_api_key()
    except MissingAPIKeyError as e:
        logging.error(f"API key error: {e}")
        sys.exit(1)

    try:
        sanitized_game_name = sanitize_game_name(args.game_name)
        raw_data = fetch_game_data(sanitized_game_name)
        game_info = parse_game_info(raw_data)
        display_game_info(game_info)
        return game_info
    except InvalidInputError as e:
        logging.error(f"Input validation error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    return None

if __name__ == "__main__":
    main()
