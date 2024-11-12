import os
import asyncio
import json
import signal
import binascii

from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from cryptography.fernet import Fernet
from ecdsa import SigningKey, SECP256k1
import aiohttp
import nest_asyncio

# Allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Get token
token = os.getenv('TELEGRAM_BOT_TOKEN')
blockcypher_token = os.getenv('BLOCKCYPHER_API_TOKEN')
encryption_key = os.getenv('ENCRYPTION_KEY')

if not token or not blockcypher_token or not encryption_key:
    raise ValueError("One or more environment variables are not set")

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
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance?token={blockcypher_token}') as response:
                response.raise_for_status()
                data = await response.json()
                balance = data.get('balance', 0)
                await update.message.reply_text(f"Your balance: {balance} satoshis")
    except aiohttp.ClientError as e:
        await update.message.reply_text("Error retrieving balance.")
        print(f"Error: {e}")

# Function to generate a new address
async def generate_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://api.blockcypher.com/v1/btc/main/addrs?token={blockcypher_token}') as response:
                response.raise_for_status()
                data = await response.json()
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

    except aiohttp.ClientError as e:
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
        encrypted_private_key = None
        for item in keys:
            if from_address in item:
                encrypted_private_key = item[from_address]
                break

        if not encrypted_private_key:
            await update.message.reply_text("Error: Private key for this address not found.")
            return

        private_key = decrypt_private_key(encrypted_private_key)
        
        # Create an unsigned transaction
        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://api.blockcypher.com/v1/btc/main/txs/new?token={blockcypher_token}', json={
                "inputs": [{"addresses": [from_address]}],
                "outputs": [{"addresses": [to_address], "value": amount}]
            }) as response:
                response.raise_for_status()
                tx_data = await response.json()

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
                async with session.post(f'https://api.blockcypher.com/v1/btc/main/txs/send?token={blockcypher_token}', json=tx_data) as send_response:
                    send_response.raise_for_status()
                    send_data = await send_response.json()

                    if "errors" in send_data:
                        await update.message.reply_text("Error sending transaction.")
                    else:
                        await update.message.reply_text(f"Transaction sent: {send_data.get('tx', {}).get('hash')}")

    except aiohttp.ClientError as e:
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
