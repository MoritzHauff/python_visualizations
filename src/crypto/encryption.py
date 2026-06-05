"""
Encrypt and decrypt files using the 'cryptography' module and ways to handle key/passwords.

reference: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
"""

import os
import base64
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def _get_salt(path_salt: str | Path):
    """If available read the previous salt, otherwise generate a new one and save it."""
    if not isinstance(path_salt, Path):
        path_salt = Path(path_salt)

    if path_salt.is_file():
        logging.debug(f"Reading salt from: {path_salt.absolute()}")
        with open(path_salt, "rb") as f:
            salt = f.read()
    else:
        salt = os.urandom(16)
        logging.debug(f"Saving salt to: {path_salt.absolute()}")
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


def write_encrypted(path_file: str | Path, key, content) -> None:
    """Write the content encrypted with key to disk."""

    fernet = Fernet(key)
    token = fernet.encrypt(content)
    with open(path_file, "wb") as f:
        f.write(token)

def read_encrypted(path_file: str | Path, key):
    """Read and decrypt the content of an encrypted file."""

    fernet = Fernet(key)
    with open(path_file, "rb") as f:
        token = f.read()
    content = fernet.decrypt(token)
    return content


# TODO add a context manager to use like this: with EncryptedFile.open(path, "r") as f: f.read()
# TODO and use a IOBytestrem object

