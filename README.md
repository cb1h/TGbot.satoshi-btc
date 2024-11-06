# TGbot-for-btc-transaction.satoshi

Bot uses API from blockcypher.com  
Docs: https://www.blockcypher.com/dev/#introduction

U will need Token from blockcypher.com (just register, thats free)
U will need Token from your TG Bot (use BotFather for create bots)
U will need to create encryption_key. Use file create_key.py for creating this key.

This is a Telegram bot for managing Bitcoin transactions. The bot allows users to generate new Bitcoin addresses, check balances, and send cryptocurrency.

## Features

- **Start**: Start working with the bot.
- **Check Balance**: Check the balance of a specified Bitcoin address.
- **Generate Address**: Generate a new Bitcoin address.
- **Send Cryptocurrency**: Send cryptocurrency from one address to another.

## Requirements

- Python 3.7+
- `python-telegram-bot`
- `python-dotenv`
- `requests`
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

4. Create a `.env` file in the root directory of the project and add your tokens:

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

2. Interact with the bot using the following commands:
    - `/start` - Start working with the bot.
    - `/balance <address>` - Check the balance of a specified Bitcoin address.
    - `/generate_address` - Generate a new Bitcoin address.
    - `/send <from_address> <to_address> <amount>` - Send cryptocurrency from one address to another.

## Test Mode

For Test Mode of the bot, use `bcy/test` in API URLs instead of `btc/main` and check https://www.blockcypher.com/dev/#testing.  
With tests, you can fund your test address and send money to another test address, check balances.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.