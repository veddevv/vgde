import logging
import os
import re
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Optional, Dict, Any

import requests

# Constants
MAX_GAME_NAME_LENGTH = 100
GAME_NAME_PATTERN = r"^[a-zA-Z0-9\s\-\.',:!&]+$"  # More permissive pattern
DEFAULT_REQUEST_TIMEOUT = 10
BASE_URL = 'https://api.rawg.io/api'
GAMES_ENDPOINT = '/games'
DEVELOPER_MODE = os.getenv('DEVELOPER_MODE', 'false').lower() in ('true', '1', 't')

# Handle non-integer REQUEST_TIMEOUT values gracefully
try:
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT))
except ValueError:
    REQUEST_TIMEOUT = DEFAULT_REQUEST_TIMEOUT


def configure_logging() -> logging.Logger:
    """Configure logging for the script based on developer mode."""
    logger = logging.getLogger(__name__)

    if DEVELOPER_MODE:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    else:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# Configure logging
logger = configure_logging()

# Retrieve the RAWG API key from environment variables
API_KEY = os.getenv('RAWG_API_KEY')


class MissingAPIKeyError(Exception):
    """Custom exception for missing API key."""
    pass


class InvalidInputError(Exception):
    """Custom exception for invalid user input."""
    pass


def validate_game_name(game_name: str) -> str:
    """
    Validates the game name.

    Args:
        game_name (str): The name of the game to validate.

    Returns:
        str: The validated game name.

    Raises:
        InvalidInputError: If the game name is invalid.
    """
    if not game_name or game_name.strip() == "":
        raise InvalidInputError("Game name cannot be empty.")

    if len(game_name) > MAX_GAME_NAME_LENGTH:
        raise InvalidInputError(f"Game name is too long (max {MAX_GAME_NAME_LENGTH} characters).")

    if not re.match(GAME_NAME_PATTERN, game_name):
        raise InvalidInputError("Game name contains invalid characters.")

    return game_name.strip()


def check_api_key() -> None:
    """
    Checks if the RAWG API key is set.

    Raises:
        MissingAPIKeyError: If the API key is not found.
    """
    if not API_KEY or API_KEY.strip() == "":
        raise MissingAPIKeyError("API key not found. Please set the RAWG_API_KEY environment variable.")


def fetch_game_data(game_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches game data from the RAWG API and returns the first result.

    Args:
        game_name (str): The name of the game to fetch data for.

    Returns:
        Optional[Dict[str, Any]]: The fetched game data or None if not found.
    """
    url = f"{BASE_URL}{GAMES_ENDPOINT}"
    params = {'key': API_KEY, 'search': game_name}

    try:
        if DEVELOPER_MODE:
            logger.debug(f"Fetching data from: {url} with params: {params}")

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            return data['results'][0]
        else:
            logger.warning(f"No results found for game '{game_name}'.")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
    except requests.exceptions.ConnectionError:
        logger.error("Network connection error. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.reason}")
        if DEVELOPER_MODE:
            logger.debug(f"Response content: {e.response.content}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
    except ValueError as e:
        logger.error(f"Error parsing response: {str(e)}")
    return None


def parse_game_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the game information from the API response.

    Args:
        data (Dict[str, Any]): The raw game data from the API.

    Returns:
        Dict[str, Any]: The parsed game information with missing fields set to None.
    """
    required_keys = ['name', 'released', 'rating', 'description', 'background_image']
    game_info = {}

    for key in required_keys:
        game_info[key] = data.get(key)

    return game_info


def display_game_info(game_info: Dict[str, Any]) -> None:
    """
    Displays information about a game.

    Args:
        game_info (Dict[str, Any]): The game information to display.
    """
    if not game_info:
        logger.warning("No game information to display.")
        return

    print("\n" + "=" * 50)
    print(f"Game: {game_info['name']}")
    print("=" * 50)

    if game_info['released']:
        print(f"Released: {game_info['released']}")
    else:
        print("Released: Unknown")

    if game_info['rating']:
        print(f"Rating: {game_info['rating']}/5")
    else:
        print("Rating: Not rated")

    if game_info['description']:
        # Strip HTML tags for cleaner console output
        description = re.sub(r'<[^>]+>', '', game_info['description'])
        print("\nDescription:")
        print(description[:300] + ("..." if len(description) > 300 else ""))

    if game_info['background_image']:
        print(f"\nBackground Image: {game_info['background_image']}")


def main() -> Optional[Dict[str, Any]]:
    """
    Main function to run the script.
    Allows user to search for a game either via command-line arguments or interactive prompt.

    Returns:
        Optional[Dict[str, Any]]: The game information or None if an error occurred.
    """
    parser = ArgumentParser(
        description="Fetch game information from RAWG API.",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('game_name', nargs='?', type=str, help="The name of the game to search for")
    args = parser.parse_args()

    try:
        check_api_key()
    except MissingAPIKeyError as e:
        logger.error(str(e))
        return None

    game_name = args.game_name
    if not game_name:
        # Interactive mode if no command-line argument is provided
        try:
            game_name = input("Enter the name of the game: ")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return None

    try:
        sanitized_game_name = validate_game_name(game_name)
        if DEVELOPER_MODE:
            logger.debug(f"Searching for game: '{sanitized_game_name}'")

        raw_data = fetch_game_data(sanitized_game_name)
        if raw_data:
            game_info = parse_game_info(raw_data)
            display_game_info(game_info)
            return game_info
        else:
            print(f"No game found matching '{sanitized_game_name}'.")
            return None

    except InvalidInputError as e:
        logger.error(str(e))
    except Exception as e:
        if DEVELOPER_MODE:
            logger.exception("An unexpected error occurred")
        else:
            logger.error(f"An error occurred: {str(e)}")

    return None


if __name__ == "__main__":
    main()
