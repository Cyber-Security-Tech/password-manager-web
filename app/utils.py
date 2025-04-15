import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the encryption key from environment and initialize Fernet
fernet_key = os.getenv('FERNET_KEY')
if not fernet_key:
    raise ValueError("FERNET_KEY is missing in the .env file.")

fernet = Fernet(fernet_key.encode())

def encrypt_password(plain_text_password: str) -> str:
    """
    Encrypts a plain-text password using Fernet symmetric encryption.

    Args:
        plain_text_password (str): The password to encrypt.

    Returns:
        str: The encrypted password (base64 encoded).
    """
    return fernet.encrypt(plain_text_password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypts a previously encrypted password.

    Args:
        encrypted_password (str): The encrypted password to decrypt.

    Returns:
        str: The original plain-text password.
    """
    return fernet.decrypt(encrypted_password.encode()).decode()
