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
  Gracefully handles network issues, invalid input, and missing API key scenarios.
- **Developer Mode**  
  Enable detailed debug logging for troubleshooting and development.
- **Clean Description Display**  
  Removes HTML tags for readable output; truncates lengthy descriptions.
- **Configurable Timeout**  
  Set request timeout duration via environment variables.

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

2. **Run vgde**
    - **Interactive mode**  
      ```sh
      python vgde.py
      ```
    - **Direct mode**  
      ```sh
      python vgde.py "The Witcher 3"
      ```

---

## ⚙️ Configuration

vgde can be customized via the following environment variables:

| Variable          | Required | Description                                                   | Default   |
|-------------------|----------|---------------------------------------------------------------|-----------|
| `RAWG_API_KEY`    | Yes      | Your RAWG API key                                             | —         |
| `DEVELOPER_MODE`  | No       | Set to `true`, `1`, or `t` to enable verbose debug logging    | `false`   |
| `REQUEST_TIMEOUT` | No       | Timeout in seconds for API requests                           | `10`      |

**Example:**

```sh
RAWG_API_KEY='your_key' DEVELOPER_MODE=true REQUEST_TIMEOUT=15 python vgde.py "Portal 2"
```

---

## 📝 Example Output

```
Game: The Witcher 3: Wild Hunt
Released: 2015-05-18
Rating: 4.67 / 5
Description: The Witcher 3: Wild Hunt is a story-driven, open world adventure...
Background Image: https://media.rawg.io/media/games/...
```

---

## 🐞 Troubleshooting

- **Missing API Key:**  
  Make sure you've set your `RAWG_API_KEY` environment variable.
- **No Results Found:**  
  Try a different or more specific game name.
- **Timeouts or Network Errors:**  
  Check your internet connection, or increase `REQUEST_TIMEOUT`.
