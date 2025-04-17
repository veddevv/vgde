# vgde (Video Game Data Explorer)

This Python script fetches and displays information about video games using the RAWG API. Simply enter the name of a game, and the script will provide details such as the game's release date, rating, description, and background image.

## Features
- Fetches game information from the RAWG API
- Displays game name, release date, rating, description, and background image
- Supports both command-line arguments and interactive input mode
- Error handling for network issues, invalid input, and missing API key
- Developer mode for detailed logging and debugging information
- HTML tag stripping for cleaner description display
- Truncation of long descriptions for better readability
- Custom timeout configuration via environment variables

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
    export RAWG_API_KEY='your_api_key_here'
    ```

2. Run the script using either method:
    ```sh
    # Interactive mode
    python vgde.py
    
    # Direct mode with command-line argument
    python vgde.py "The Witcher 3"
    ```

## Configuration Options
The script supports the following environment variables:

- `RAWG_API_KEY` (required): Your RAWG API key
- `DEVELOPER_MODE`: Set to `true`, `1`, or `t` to enable developer mode with detailed logging
- `REQUEST_TIMEOUT`: Set a custom timeout in seconds for API requests (default: 10)

Example with all options:
```sh
RAWG_API_KEY='your_key' DEVELOPER_MODE=true REQUEST_TIMEOUT=15 python vgde.py
