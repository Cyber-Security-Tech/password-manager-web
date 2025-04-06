import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()
fernet_key = os.getenv('FERNET_KEY').encode()
fernet = Fernet(fernet_key)

def encrypt_password(plain_text_password):
    """Encrypt a plain password string."""
    return fernet.encrypt(plain_text_password.encode()).decode()

def decrypt_password(encrypted_password):
    """Decrypt an encrypted password string."""
    return fernet.decrypt(encrypted_password.encode()).decode()