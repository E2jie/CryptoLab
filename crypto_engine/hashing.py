"""Hashing and message integrity utilities for CryptoLab."""

import hashlib
import hmac
import secrets


class Hashing:
    ALGORITHMS = ("md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512")
    HMAC_ALGORITHMS = ("sha256", "sha512", "sha3_256", "sha3_512")
    PASSWORD_ITERATIONS = 600_000

    @staticmethod
    def hash_text(text: str, algorithm: str = "sha256") -> str:
        algorithm = algorithm.lower()
        if algorithm not in Hashing.ALGORITHMS:
            raise ValueError("Unsupported hashing algorithm")
        return hashlib.new(algorithm, text.encode("utf-8")).hexdigest()

    @staticmethod
    def md5(text: str) -> str:
        return Hashing.hash_text(text, "md5")

    @staticmethod
    def sha1(text: str) -> str:
        return Hashing.hash_text(text, "sha1")

    @staticmethod
    def sha256(text: str) -> str:
        return Hashing.hash_text(text, "sha256")

    @staticmethod
    def sha512(text: str) -> str:
        return Hashing.hash_text(text, "sha512")

    @staticmethod
    def sha3_256(text: str) -> str:
        return Hashing.hash_text(text, "sha3_256")

    @staticmethod
    def sha3_512(text: str) -> str:
        return Hashing.hash_text(text, "sha3_512")

    @staticmethod
    def verify_hash(text: str, expected_hash: str, algorithm: str = "sha256") -> bool:
        actual = Hashing.hash_text(text, algorithm)
        return hmac.compare_digest(actual, expected_hash.strip().lower())

    @staticmethod
    def hash_file(file_path: str, algorithm: str = "sha256") -> str:
        algorithm = algorithm.lower()
        if algorithm not in Hashing.ALGORITHMS:
            raise ValueError("Unsupported hashing algorithm")
        digest = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def generate_key(size: int = 32) -> str:
        if size < 16:
            raise ValueError("Key must be at least 16 bytes")
        return secrets.token_hex(size)

    @staticmethod
    def generate_hmac(text: str, key: str, algorithm: str = "sha256") -> str:
        algorithm = algorithm.lower()
        if algorithm not in Hashing.HMAC_ALGORITHMS:
            raise ValueError("Unsupported HMAC algorithm")
        try:
            key_bytes = bytes.fromhex(key)
        except ValueError as error:
            raise ValueError("HMAC key must be a hexadecimal string") from error
        if len(key_bytes) < 16:
            raise ValueError("HMAC key must contain at least 16 bytes")
        return hmac.new(key_bytes, text.encode("utf-8"), digestmod=algorithm).hexdigest()

    @staticmethod
    def verify_hmac(text: str, key: str, signature: str, algorithm: str = "sha256") -> bool:
        expected = Hashing.generate_hmac(text, key, algorithm)
        return hmac.compare_digest(expected, signature.strip().lower())

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, Hashing.PASSWORD_ITERATIONS
        )
        return f"pbkdf2_sha256${Hashing.PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, saved_hash: str) -> bool:
        try:
            name, count, salt_hex, digest_hex = saved_hash.split("$")
            iterations = int(count)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            if (
                name != "pbkdf2_sha256"
                or not 100_000 <= iterations <= 2_000_000
                or len(salt) != 16
                or len(expected) != 32
            ):
                return False
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, iterations
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError, AttributeError):
            return False
