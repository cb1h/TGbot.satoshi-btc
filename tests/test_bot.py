import os
import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, Bot
from telegram.ext import ContextTypes
from main import start, check_balance, generate_address, send_crypto

# Mock environment
os.environ['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN', 'test_token')
os.environ['BLOCKCYPHER_API_TOKEN'] = os.getenv('BLOCKCYPHER_API_TOKEN', 'test_blockcypher_token')
os.environ['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY', 'test_encryption_key')

@pytest.fixture
def bot():
    return Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

@pytest.fixture
def update():
    return Update(update_id=1, message=AsyncMock())

@pytest.fixture
def context():
    return ContextTypes.DEFAULT_TYPE

@patch('main.Update.message.reply_text', new_callable=AsyncMock)
async def test_start_command(mock_reply_text, bot, update, context):
    await start(update, context)
    mock_reply_text.assert_called_with("Welcome! Choose a command from the menu.")

@patch('main.Update.message.reply_text', new_callable=AsyncMock)
async def test_check_balance_command(mock_reply_text, bot, update, context):
    context.args = ['test_address']
    await check_balance(update, context)
    assert mock_reply_text.called

@patch('main.Update.message.reply_text', new_callable=AsyncMock)
async def test_generate_address_command(mock_reply_text, bot, update, context):
    await generate_address(update, context)
    assert mock_reply_text.called

@patch('main.Update.message.reply_text', new_callable=AsyncMock)
async def test_send_crypto_command(mock_reply_text, bot, update, context):
    context.args = ['from_address', 'to_address', '1000']
    await send_crypto(update, context)
    assert mock_reply_text.called