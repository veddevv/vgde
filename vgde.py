import os
import requests
import sys
import logging
import re
from argparse import ArgumentParser
from typing import Optional, Dict, Any

# Constants
MAX_GAME_NAME_LENGTH = 100
GAME_NAME_PATTERN = r"^[a-zA-Z0-9\s]+$"
DEFAULT_REQUEST_TIMEOUT = 10
BASE_URL = 'https://api.rawg.io/api'

# Handle non-integer REQUEST_TIMEOUT values gracefully
try:
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT))
except ValueError:
    logging.warning(f"Invalid REQUEST_TIMEOUT value. Using default: {DEFAULT_REQUEST_TIMEOUT}")
    REQUEST_TIMEOUT = DEFAULT_REQUEST_TIMEOUT

# Configure logging for this script
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Retrieve the RAWG API key from environment variables
API_KEY = os.getenv('RAWG_API_KEY')

# Exit if the API key is not set
if not API_KEY:
    logger.error("RAWG API key not found in environment variables.")
    sys.exit(1)

class MissingAPIKeyError(Exception):
    """Custom exception for missing API key."""
    pass

class InvalidInputError(Exception):
    """Custom exception for invalid user input."""
    pass

def validate_game_name(game_name: str) -> str:
    """
    Validates the game name.
    """
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
        logger.error("API key not found. Please set the RAWG_API_KEY environment variable.")
        raise MissingAPIKeyError("API key not found. Please set the RAWG_API_KEY environment variable.")

def fetch_game_data(game_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches game data from the RAWG API and returns the first result.
    """
    game_name = validate_game_name(game_name)
    url = f"{BASE_URL}/games"
    params = {'key': API_KEY, 'search': game_name}

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            return data['results'][0]
        else:
            logger.error(f"No results found for game '{game_name}'.")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"The request timed out while trying to fetch game information for '{game_name}'.")
    except requests.exceptions.ConnectionError:
        logger.error(f"A network problem occurred while trying to fetch game information for '{game_name}'.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred while trying to fetch game information for '{game_name}': {e.response.status_code} - {e.response.reason}")
        logger.error(f"Response content: {e.response.content}")
    except requests.exceptions.RequestException as e:
        logger.error(f"An unexpected error occurred while trying to fetch game information for '{game_name}': {e}")
    except ValueError as e:
        logger.error(f"Error parsing the response JSON for game '{game_name}': {e}")
    return None

def parse_game_info(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parses the game information from the API response.
    """
    required_keys = ['name', 'released', 'rating', 'description', 'background_image']
    
    if all(key in data for key in required_keys):
        return {key: data[key] for key in required_keys}

    logger.error("Unexpected data format in API response for game information.")
    return None

def display_game_info(game_info: Optional[Dict[str, Any]]) -> None:
    """
    Displays information about a game.
    """
    if game_info:
        logger.info(f"Name: {game_info['name']}")
        logger.info(f"Released: {game_info['released']}")
        logger.info(f"Rating: {game_info['rating']}")
        logger.info(f"Description: {game_info['description']}")
        logger.info(f"Background Image URL: {game_info['background_image']}")
    else:
        logger.warning("No game information to display.")

def main() -> Optional[Dict[str, Any]]:
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
        logger.error(f"API key error: {e}")
        sys.exit(1)

    try:
        sanitized_game_name = validate_game_name(args.game_name)
        raw_data = fetch_game_data(sanitized_game_name)
        game_info = parse_game_info(raw_data)
        display_game_info(game_info)
        return game_info
    except InvalidInputError as e:
        logger.error(f"Input validation error: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    return None

if __name__ == "__main__":
    main()
