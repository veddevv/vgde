import requests

# Replace 'your_rawg_api_key_here' with your actual RAWG API key
API_KEY = 'your_rawg_api_key_here'
BASE_URL = 'https://api.rawg.io/api'

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
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
 
    # Check if the API returned any results
    if 'results' in data and len(data['results']) > 0:
        game = data['results'][0]
        return {
            'name': game['name'],
            'released': game['released'],
            'rating': game['rating'],
            'background_image': game['background_image'],
            'description': game['description_raw'] if 'description_raw' in game else 'No description available.'
        }
    else:
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
        print(f"Description: {game_info['description']}")
        print(f"Background Image: {game_info['background_image']}")
    else:
        print("Game not found.")

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