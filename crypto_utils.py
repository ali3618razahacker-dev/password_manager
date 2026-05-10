import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import bcrypt

class CryptoManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a master password for storage."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifies a master password against its hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives an encryption key from the master password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        """Encrypts data using Fernet (AES-128-CBC)."""
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(token: str, key: bytes) -> str:
        """Decrypts data using Fernet."""
        f = Fernet(key)
        try:
            return f.decrypt(token.encode()).decode()
        except Exception:
            return ""

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a random salt for key derivation."""
        return os.urandom(16)
