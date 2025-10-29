# vgde (Video Game Data Explorer)

**vgde** is a Python tool for quickly exploring and fetching information about video games using the [RAWG Video Games Database API](https://rawg.io/apidocs). Enter the name of a game, and vgde provides details such as the release date, rating, description, and more—all right from your terminal.

---

## Features

- **Fetches Live Game Data**  
  Retrieves up-to-date video game information from the RAWG API.
- **Rich Output**  
  Displays game name, release date, rating, description, and a background image URL.
- **Flexible Input**  
  Use interactive prompts or pass the game name directly as a command-line argument.
- **Robust Error Handling**  
  Gracefully handles network issues, SSL errors, invalid input, rate limiting, and missing API key scenarios.
- **Developer Mode**  
  Enable detailed debug logging for troubleshooting and development.
- **Clean Description Display**  
  Removes HTML tags for readable output; truncates lengthy descriptions.
- **Configurable Timeout**  
  Set request timeout duration via environment variables (1-300 seconds).
- **Enhanced Security**  
  - API key validation and sanitization
  - SSL/TLS certificate verification
  - Protection against HTML entity expansion attacks
  - Response size limits to prevent memory exhaustion
  - Secure API key handling (never logged in debug mode)
- **Smart Search Suggestions**  
  Provides helpful suggestions when no game is found.
- **Debug Mode Flag**  
  Run with `--debug` flag for detailed troubleshooting without changing environment variables.

---

## 🛠 Requirements

- Python 3.x
- [`requests`](https://pypi.org/project/requests/) Python library

---

## 🚀 Installation

1. **Clone the repository**
    ```sh
    git clone https://github.com/veddevv/vgde.git
    cd vgde
    ```

2. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

---

## ⚡️ Usage

1. **Set your RAWG API key**  
   Obtain a free API key from [RAWG](https://rawg.io/apidocs) and set it as an environment variable:
    ```sh
    export RAWG_API_KEY='your_api_key_here'
    ```
    
    **Note:** The API key must be between 10-100 characters and will be automatically validated.

2. **Run vgde**
    - **Interactive mode**  
      ```sh
      python vgde.py
      ```
    - **Direct mode**  
      ```sh
      python vgde.py "The Witcher 3"
      ```
    - **Debug mode** (for troubleshooting)  
      ```sh
      python vgde.py "Portal 2" --debug
      ```

---

## ⚙️ Configuration

vgde can be customized via the following environment variables:

| Variable          | Required | Description                                                   | Default   | Valid Range  |
|-------------------|----------|---------------------------------------------------------------|-----------|--------------|
| `RAWG_API_KEY`    | Yes      | Your RAWG API key (10-100 characters)                         | —         | —            |
| `DEVELOPER_MODE`  | No       | Set to `true`, `1`, `t`, `yes`, `y`, `on`, `enable`, or `enabled` to enable verbose debug logging | `false` | — |
| `REQUEST_TIMEOUT` | No       | Timeout in seconds for API requests                           | `10`      | 1-300        |

**Example:**

```sh
RAWG_API_KEY='your_key' DEVELOPER_MODE=true REQUEST_TIMEOUT=15 python vgde.py "Portal 2"
```

### Command-Line Options

- `game_name` (optional positional argument): The name of the game to search for
- `--debug`: Enable debug mode for the current run (overrides `DEVELOPER_MODE` environment variable)

**Example with debug flag:**

```sh
python vgde.py "Cyberpunk 2077" --debug
```

---

## 📝 Example Output

```
==================================================
Game: The Witcher 3: Wild Hunt
==================================================
Released: 2015-05-18
Rating: 4.67/5

Description:
The Witcher 3: Wild Hunt is a story-driven, open world adventure set in a visually stunning fantasy universe full of meaningful choices and impactful consequences...

Background Image: https://media.rawg.io/media/games/...
```

---

## 🔒 Security Features

vgde implements several security measures to protect your system and data:

- **API Key Validation**: Validates API key format and length before use
- **SSL/TLS Verification**: Always verifies SSL certificates for secure connections
- **Input Sanitization**: Game names are validated and sanitized to prevent injection attacks
- **Response Size Limits**: Enforces maximum response sizes (10MB) to prevent memory exhaustion
- **HTML Parsing Protection**: Guards against HTML entity expansion attacks with character limits
- **Timeout Bounds**: Request timeouts are bounded between 1-300 seconds
- **Secure Logging**: API keys are never logged, even in debug mode
- **Error Handling**: Comprehensive error handling for network, SSL, and API errors

---

## 🐞 Troubleshooting

- **Missing API Key:**  
  Make sure you've set your `RAWG_API_KEY` environment variable.
  
- **Invalid API Key:**  
  Ensure your API key is between 10-100 characters. Check for extra spaces or quotes.
  
- **No Results Found:**  
  The tool will provide search suggestions. Try:
  - Checking the spelling of the game name
  - Using the official game title
  - Removing special characters or trademark symbols (™, ®, ©)
  - Using a shorter or more specific name
  
- **Timeouts or Network Errors:**  
  Check your internet connection, or increase `REQUEST_TIMEOUT` (max 300 seconds).
  
- **SSL Certificate Errors:**  
  This may indicate a network security issue. Ensure you're on a trusted network and your system's SSL certificates are up to date.
  
- **Rate Limiting:**  
  If you receive a rate limit error, wait for the specified time before making another request. The RAWG API has rate limits for free tier users.
  
- **Need More Details?**  
  Run vgde with the `--debug` flag to see detailed error messages and diagnostic information:
  ```sh
  python vgde.py "Game Name" --debug
  ```
