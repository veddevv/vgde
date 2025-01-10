# vgde

This Python script fetches and displays information about video games using the RAWG API. Simply enter the name of a game, and the script will provide details such as the game's release date, rating, etc.

## Features
- Fetches game information from the RAWG API.
- Displays game name, release date, rating, description, and background image.
- User-friendly prompts for game search.
- Error handling for network issues and invalid input.
- Improved logging configuration for better debugging.
- Graceful handling of non-integer request timeout values.

## Requirements
- Python 3.x
- `requests` library

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/veddevv/vgde.git
    cd vgde
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Set the `RAWG_API_KEY` environment variable with your actual RAWG API key:
    ```sh
    RAWG_API_KEY='your_api_key_here'
    ```

2. Run the script:
    ```sh
    python vgde.py
    ```

3. Enter the name of the game when prompted.

## Developer Mode
- Enable developer mode for extra technical details by setting the `DEVELOPER_MODE` flag to `True` in the script.

## Contributing
- Contributions are welcome! Please fork the repository and submit a pull request.

## License
- This project is licensed under the GPL Version 3.0 License.
