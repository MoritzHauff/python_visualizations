"""
Encrypt and decrypt files using the 'cryptography' module and ways to handle key/passwords.

reference:
https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
https://security.stackexchange.com/questions/17421/how-to-store-salt
"""

import os
import json
import base64
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


logger = logging.getLogger(__name__)


def _get_salt(path_salt: str | Path):
    """If available read the previous salt, otherwise generate a new one and save it."""
    if not isinstance(path_salt, Path):
        path_salt = Path(path_salt)

    if path_salt.is_file():
        logger.debug(f"Reading salt from: {path_salt.absolute()}")
        with open(path_salt, "rb") as f:
            salt = f.read()
    else:
        salt = os.urandom(16)
        logger.debug(f"Saving salt to: {path_salt.absolute()}")
        with open(path_salt, "wb") as f:
            f.write(salt)
    return salt


def get_key(password: str, path_salt: str | Path):
    """Convert the password to a Fernet key. If available use the previous salt otherwise create a new one."""

    salt = _get_salt(path_salt)

    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=1,
        lanes=4,
        memory_cost=2**21
    )
    password_bytestr = password.encode()
    key = base64.urlsafe_b64encode(kdf.derive(password_bytestr))
    return key


def write_encrypted(path_file: str | Path, key, data) -> None:
    """Write the data encrypted with key to disk.

    Every call to Fernet.encrypt() produces a different ciphertext, because Fernet includes:
    - a random 128‑bit IV (for AES‑128 in CBC mode)
    - a timestamp
    - HMAC authentication tag
    
    So even if:
    - the password is identical
    - the salt file is reused
    - the derived key is identical
    - the JSON content is identical
    …the encrypted output must differ.
    
    This is a security feature called semantic security.
    """
    logger.debug(f"Write encrypted file to: {path_file}")

    fernet = Fernet(key)
    token = fernet.encrypt(data)
    with open(path_file, "wb") as f:
        f.write(token)


def read_encrypted(path_file: str | Path, key):
    """Read and decrypt the data of an encrypted file."""
    logger.debug(f"Read encrypted file from: {path_file}")

    fernet = Fernet(key)
    with open(path_file, "rb") as f:
        token = f.read()
    data = fernet.decrypt(token)
    return data

def write_encrypted_json(path_file: str | Path, key, data: dict) -> None:
    """Write a JSON serializable object (dict) encrypted to disk."""
    data_bytes = json.dumps(data).encode()
    write_encrypted(path_file, key, data_bytes)


def read_encrypted_json(path_file: str | Path, key) -> dict:
    """Read and decrypt the data of an encrypted json file and return the corresponding dict."""
    data_bytes = read_encrypted(path_file, key)
    data = json.loads(data_bytes.decode())
    return data

# TODO add a context manager to use like this: with EncryptedFile.open(path, "r") as f: f.read()
# TODO and use a IOBytestrem object

