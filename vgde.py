import os
import requests

# Retrieve the RAWG API key from environment variables
API_KEY = os.getenv('RAWG_API_KEY')
BASE_URL = 'https://api.rawg.io/api'

def get_game_info(game_name):
    """
    Fetches information about a game from the RAWG API.

    Parameters:
    game_name (str): The name of the game to search for.

    Returns:
    dict: A dictionary containing the game's information, or None if the game is not found.
    """
    if not API_KEY:
        print("API key not found. Please set the RAWG_API_KEY environment variable.")
        return None

    url = f"{BASE_URL}/games"
    params = {
        'key': API_KEY,
        'search': game_name
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Network error occurred: {e}")
        return None
    
    try:
        data = response.json()
    except ValueError as e:
        print(f"JSON decoding error: {e}")
        return None

    # Check if the API returned any results
    if 'results' in data and isinstance(data['results'], list) and len(data['results']) > 0:
        game = data['results'][0]
        # Ensure the expected keys are in the game data
        if all(key in game for key in ['name', 'released', 'rating']):
            return {
                'name': game['name'],
                'released': game['released'],
                'rating': game['rating'],
            }
        else:
            print("Unexpected data format in API response.")
            return None
    else:
        print("No results found for the game.")
        return None

def display_game_info(game_info):
    """
    Displays information about a game.

    Parameters:
    game_info (dict): A dictionary containing the game's information.
    """
    if game_info:
        print(f"Name: {game_info['name']}")
        print(f"Released: {game_info['released']}")
        print(f"Rating: {game_info['rating']}")
    else:
        print("No game information to display.")

def main():
    """
    Main function to run the script.
    Prompts the user to enter the name of a game and displays its information.
    """
    game_name = input("Enter the name of the game: ")
    game_info = get_game_info(game_name)
    display_game_info(game_info)

if __name__ == "__main__":
    main()
