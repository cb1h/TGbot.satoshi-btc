import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import nest_asyncio
from cryptography.fernet import Fernet
import signal
import json
from ecdsa import SigningKey, SECP256k1
import binascii

# Allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Get token
token = os.getenv('TELEGRAM_BOT_TOKEN')
blockcypher_token = os.getenv('BLOCKCYPHER_API_TOKEN')
encryption_key = os.getenv('ENCRYPTION_KEY')

# Initialize encryption
cipher_suite = Fernet(encryption_key.encode())

# Function to encrypt the private key
def encrypt_private_key(private_key: str) -> str:
    return cipher_suite.encrypt(private_key.encode()).decode()

# Function to decrypt the private key
def decrypt_private_key(encrypted_key: str) -> str:
    return cipher_suite.decrypt(encrypted_key.encode()).decode()

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Choose a command from the menu.")

# Function to check balance
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Please specify an address.")
        return
    address = context.args[0]
    try:
        response = requests.get(f'https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance?token={blockcypher_token}')
        response.raise_for_status()
        data = response.json()
        balance = data.get('balance', 0)
        await update.message.reply_text(f"Your balance: {balance} satoshis")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Error retrieving balance.")
        print(f"Error: {e}")

# Function to generate a new address
async def generate_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.post(f'https://api.blockcypher.com/v1/btc/main/addrs?token={blockcypher_token}')
        response.raise_for_status()
        data = response.json()
        address = data.get('address')
        private_key = data.get('private')
        encrypted_private_key = encrypt_private_key(private_key)
        
        # Load existing keys from file
        try:
            with open("keys.json", "r") as file:
                keys = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            keys = []

        # Add new key
        keys.append({address: encrypted_private_key})

        # Save updated keys to file
        with open("keys.json", "w") as file:
            json.dump(keys, file, indent=4)

        await update.message.reply_text(f"Your new address: {address}")
        print(f"Saved encrypted key for {address}: {encrypted_private_key}")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Error creating address.")
        print(f"Error: {e}")

# Function to send cryptocurrency
async def send_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /send <from_address> <to_address> <amount>")
        return
    from_address, to_address, amount = context.args[0], context.args[1], int(context.args[2])

    # Load encrypted private key for the sender
    try:
        with open("keys.json", "r") as file:
            keys = json.load(file)
        encrypted_private_key = next((item[from_address] for item in keys if from_address in item), None)

        if not encrypted_private_key:
            await update.message.reply_text("Error: Private key for this address not found.")
            return

        private_key = decrypt_private_key(encrypted_private_key)
        
        # Create an unsigned transaction
        response = requests.post(f'https://api.blockcypher.com/v1/btc/main/txs/new?token={blockcypher_token}', json={
            "inputs": [{"addresses": [from_address]}],
            "outputs": [{"addresses": [to_address], "value": amount}]
        })
        response.raise_for_status()
        tx_data = response.json()

        if "errors" in tx_data:
            await update.message.reply_text("Error creating transaction.")
            return

        # Sign the transaction
        sk = SigningKey.from_string(binascii.unhexlify(private_key), curve=SECP256k1)
        tosign = tx_data["tosign"]
        signatures = [binascii.hexlify(sk.sign(binascii.unhexlify(t))).decode() for t in tosign]
        tx_data["signatures"] = signatures
        tx_data["pubkeys"] = [sk.verifying_key.to_string("compressed").hex()]

        # Send the signed transaction
        send_response = requests.post(f'https://api.blockcypher.com/v1/btc/main/txs/send?token={blockcypher_token}', json=tx_data)
        send_response.raise_for_status()
        send_data = send_response.json()

        if "errors" in send_data:
            await update.message.reply_text("Error sending transaction.")
        else:
            await update.message.reply_text(f"Transaction sent: {send_data.get('tx', {}).get('hash')}")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Error sending transaction.")
        print(f"Error: {e}")

async def main() -> None:
    application = ApplicationBuilder().token(token).build()

    # Create menu commands
    commands = [
        BotCommand("start", "Start working with the bot"),
        BotCommand("balance", "Check balance"),
        BotCommand("generate_address", "Generate new address"),
        BotCommand("send", "Send cryptocurrency")
    ]

    await application.bot.set_my_commands(commands)

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", check_balance))
    application.add_handler(CommandHandler("generate_address", generate_address))
    application.add_handler(CommandHandler("send", send_crypto))

    # Function to gracefully stop the bot
    def stop_bot(signum, frame):
        application.stop()
        print("Bot stopped")

    # Register SIGINT signal handler
    signal.signal(signal.SIGINT, stop_bot)

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
