import logging
import os
import re
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Optional, Dict, Any
import requests
import html
from html.parser import HTMLParser

# Constants
MAX_GAME_NAME_LENGTH = 100
# Fixed ReDoS vulnerability - removed nested quantifiers
GAME_NAME_PATTERN = r"^[a-zA-Z0-9\s\-\.',:!&]{1,100}$"
DEFAULT_REQUEST_TIMEOUT = 10
BASE_URL = 'https://api.rawg.io/api'
GAMES_ENDPOINT = '/games'
DEVELOPER_MODE = os.getenv('DEVELOPER_MODE', 'false').lower() in ('true', '1', 't')

# Enhanced timeout validation with bounds checking
try:
    timeout_value = int(os.getenv('REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT))
    # Ensure reasonable timeout bounds (1-300 seconds)
    REQUEST_TIMEOUT = max(1, min(300, timeout_value))
except (ValueError, TypeError):
    REQUEST_TIMEOUT = DEFAULT_REQUEST_TIMEOUT


def configure_logging() -> logging.Logger:
    """Configure logging for the script based on developer mode."""
    logger = logging.getLogger(__name__)
    
    # Clear any existing handlers to prevent duplicates
    if logger.handlers:
        logger.handlers.clear()

    if DEVELOPER_MODE:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
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


class RateLimitError(Exception):
    """Custom exception for API rate limiting."""
    pass


class MLStripper(HTMLParser):
    """HTML Parser for stripping tags while preserving structure."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def handle_entityref(self, name):
        self.text.append(f"&{name};")

    def handle_charref(self, name):
        self.text.append(f"&#{name};")

    def get_data(self):
        return ''.join(self.text)

def strip_html_tags(html_text: str) -> str:
    """
    Strip HTML tags while preserving structure and entities.
    
    Args:
        html_text (str): HTML text to strip
        
    Returns:
        str: Clean text with preserved structure
    """
    if not html_text:
        return ""
    
    # Limit input size to prevent memory exhaustion
    if len(html_text) > 50000:  # 50KB limit
        html_text = html_text[:50000]
    
    try:
        s = MLStripper()
        s.feed(html_text)
        result = html.unescape(s.get_data()).strip()
        # Additional length check after processing
        return result[:5000] if len(result) > 5000 else result
    except Exception as e:
        logger.warning(f"HTML parsing failed: {e}")
        return html_text  # Return original text if parsing fails

def validate_game_name(game_name: str) -> str:
    """
    Validates and sanitizes the game name.

    Args:
        game_name (str): The name of the game to validate.

    Returns:
        str: The validated and sanitized game name.

    Raises:
        InvalidInputError: If the game name is invalid.
    """
    if not isinstance(game_name, str):
        raise InvalidInputError("Game name must be a string.")

    # Remove leading/trailing whitespace and normalize internal spaces
    game_name = ' '.join(game_name.split())

    if not game_name:
        raise InvalidInputError("Game name cannot be empty.")

    if len(game_name) > MAX_GAME_NAME_LENGTH:
        raise InvalidInputError(f"Game name is too long (max {MAX_GAME_NAME_LENGTH} characters).")

    # Replace smart quotes and other special characters with standard ones
    replacements = {
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u2013': '-',  # en dash
        '\u2014': '-'   # em dash
    }
    for old, new in replacements.items():
        game_name = game_name.replace(old, new)

    if not re.match(GAME_NAME_PATTERN, game_name):
        raise InvalidInputError(
            "Game name contains invalid characters. Only letters, numbers, spaces, "
            "and the following special characters are allowed: - . ' , : ! &"
        )

    return game_name


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

    Raises:
        RateLimitError: If the API rate limit is exceeded.
    """
    url = f"{BASE_URL}{GAMES_ENDPOINT}"
    params = {'key': API_KEY, 'search': game_name}

    try:
        if DEVELOPER_MODE:
            # Fixed: Don't log API key - use safe params for logging
            safe_params = {k: v if k != 'key' else '[REDACTED]' for k, v in params.items()}
            logger.debug(f"Fetching data from: {url} with params: {safe_params}")

        response = requests.get(
            url, 
            params=params, 
            timeout=REQUEST_TIMEOUT,
            stream=True  # Enable streaming for size checking
        )
        
        # Check content length before downloading
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10_000_000:  # 10MB limit
            raise ValueError("Response too large")
        
        if response.status_code == 429:  # Too Many Requests
            retry_after = response.headers.get('Retry-After', '60')
            raise RateLimitError(f"API rate limit exceeded. Try again in {retry_after} seconds.")
            
        response.raise_for_status()
        
        # Read with size limit
        content = response.content
        if len(content) > 10_000_000:
            raise ValueError("Response content too large")
        
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            if DEVELOPER_MODE:
                # Fixed: Safe content logging with encoding handling
                try:
                    content_preview = response.content[:200].decode('utf-8', errors='ignore')
                    logger.debug(f"Response content: {content_preview}")
                except Exception:
                    logger.debug("Could not decode response content")
            return None

        if not isinstance(data, dict):
            logger.error("Unexpected API response format")
            return None

        if 'results' in data and isinstance(data['results'], list):
            if len(data['results']) > 0:
                return data['results'][0]
            else:
                logger.warning(f"No results found for game '{game_name}'.")
                return None
        else:
            logger.error("Unexpected API response structure")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
    except requests.exceptions.ConnectionError:
        logger.error("Network connection error. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        # Enhanced error context
        if e.response.status_code == 403:
            logger.error("API access forbidden. Check your API key permissions.")
        elif e.response.status_code == 404:
            logger.error("API endpoint not found. The service may be unavailable.")
        else:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.reason}")
        
        if DEVELOPER_MODE and hasattr(e, 'response'):
            try:
                content_preview = e.response.content[:200].decode('utf-8', errors='ignore')
                logger.debug(f"Response content: {content_preview}")
            except Exception:
                logger.debug("Could not decode error response content")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
    except ValueError as e:
        logger.error(f"Data validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if DEVELOPER_MODE:
            logger.exception("Detailed error information:")
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
        description = strip_html_tags(game_info['description'])
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
    parser.add_argument('--debug', action='store_true', help="Enable debug mode for this run")
    args = parser.parse_args()

    # Fixed: Use local variable instead of modifying global
    debug_mode = DEVELOPER_MODE or args.debug
    if debug_mode:
        # Reconfigure logger for this session
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled for this run")

    try:
        check_api_key()
    except MissingAPIKeyError as e:
        logger.error(str(e))
        logger.info("To set your API key, run: export RAWG_API_KEY='your-api-key-here'")
        return None

    game_name = args.game_name
    if not game_name:
        # Interactive mode if no command-line argument is provided
        try:
            game_name = input("Enter the name of the game: ")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            return None
        except Exception as e:
            logger.error(f"Error reading input: {str(e)}")
            return None

    try:
        sanitized_game_name = validate_game_name(game_name)
        if debug_mode:
            logger.debug(f"Searching for game: '{sanitized_game_name}'")

        raw_data = fetch_game_data(sanitized_game_name)
        if raw_data:
            game_info = parse_game_info(raw_data)
            display_game_info(game_info)
            return game_info
        else:
            suggestions = [
                "Check if the game name is spelled correctly",
                "Try using the official game title",
                "Remove any special characters or symbols",
                "Try a shorter or more specific name"
            ]
            print(f"\nNo game found matching '{sanitized_game_name}'.")
            print("\nSuggestions:")
            for suggestion in suggestions:
                print(f"- {suggestion}")
            return None

    except InvalidInputError as e:
        logger.error(str(e))
    except RateLimitError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        if debug_mode:
            logger.exception("An unexpected error occurred")
        else:
            logger.error(f"An error occurred: {str(e)}")
            logger.info("Run with --debug flag for more information")

    return None


if __name__ == "__main__":
    main()
