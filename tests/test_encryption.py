import os
import pytest
from main import encrypt_private_key, decrypt_private_key

# Mock environment variable
os.environ['ENCRYPTION_KEY'] = 'test_encryption_key'
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def test_encrypt_private_key():
    # Check that the encrypted text does not match the original
    original_text = "my_secret_key"
    encrypted_text = encrypt_private_key(original_text)
    assert encrypted_text != original_text
    assert isinstance(encrypted_text, str), "Encrypted text should be a string"

def test_decrypt_private_key():
    # Check that decryption matches the original
    original_text = "my_secret_key"
    encrypted_text = encrypt_private_key(original_text)
    decrypted_text = decrypt_private_key(encrypted_text)
    assert decrypted_text == original_text, "Decrypted text should match the original"

def test_encryption_key():
    # Check that the encryption key is set
    assert ENCRYPTION_KEY is not None, "ENCRYPTION_KEY is not set"
