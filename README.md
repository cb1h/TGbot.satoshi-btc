# TGbot-for-btc-transaction.satoshi

This repository includes a Telegram bot for managing Bitcoin transactions using BlockCypher's API. **Tests have been added** to improve bot reliability and functionality.

## Getting Started

To use this bot, you'll need:
1. An **encryption key**: Generate it by running the `create_key.py` file.
2. **Tokens**:
   - A Telegram Bot token: Create a bot through BotFather to obtain this token.
   - A BlockCypher API token: Register at [blockcypher.com](https://www.blockcypher.com/) (it's free) and retrieve your API token.

## Features

- **Start**: Begin interacting with the bot.
- **Check Balance**: Retrieve the balance of a specified Bitcoin address.
- **Generate Address**: Create a new Bitcoin address.
- **Send Cryptocurrency**: Transfer cryptocurrency from one address to another.

## Requirements (for BOT, not for tests)

- Python 3.7+
- `python-telegram-bot`
- `python-dotenv`
- `aiohttp`
- `cryptography`
- `ecdsa`
- `nest_asyncio`

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/cbih/TGbot-for-btc-transaction.satoshi.git
    cd TGbot-for-btc-transaction.satoshi
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up your `.env` file in the project root directory and add the following tokens:

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    BLOCKCYPHER_API_TOKEN=your_blockcypher_api_token
    ENCRYPTION_KEY=your_encryption_key
    ```

## Usage

1. Run the bot:

    ```sh
    python main.py
    ```

2. Use these commands to interact with the bot:
    - `/start` - Start working with the bot.
    - `/balance <address>` - Check the balance of a specified Bitcoin address.
    - `/generate_address` - Generate a new Bitcoin address.
    - `/send <from_address> <to_address> <amount>` - Send cryptocurrency from one address to another.

## Test Mode

For test transactions, use `bcy/test` in API URLs instead of `btc/main`. Check [BlockCypher's documentation on testing](https://www.blockcypher.com/dev/#testing) for more details. In test mode, you can fund test addresses, send transactions, and check balances.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes. 
