"""Modern encryption for CryptoLab: AES-256-GCM and RSA-OAEP."""

import base64
import binascii
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Modern:
    @staticmethod
    def _from_base64(value):
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error):
            raise ValueError("Invalid Base64 text or key.") from None

    @staticmethod
    def _aes_key(key):
        key_bytes = Modern._from_base64(key)
        if len(key_bytes) != 32:
            raise ValueError("AES-256 requires a 32-byte Base64-encoded key.")
        return key_bytes

    @staticmethod
    def generate_aes_key():
        key = AESGCM.generate_key(bit_length=256)
        return base64.b64encode(key).decode("ascii")

    @staticmethod
    def aes_encrypt(text, key):
        nonce = secrets.token_bytes(12)
        ciphertext = AESGCM(Modern._aes_key(key)).encrypt(
            nonce, text.encode("utf-8"), None
        )
        return base64.b64encode(nonce + ciphertext).decode("ascii")

    @staticmethod
    def aes_decrypt(text, key):
        data = Modern._from_base64(text)
        if len(data) < 28:
            raise ValueError("AES ciphertext is incomplete.")
        try:
            plaintext = AESGCM(Modern._aes_key(key)).decrypt(
                data[:12], data[12:], None
            )
        except InvalidTag:
            raise ValueError("Wrong AES key or damaged ciphertext.") from None
        return plaintext.decode("utf-8")

    @staticmethod
    def generate_rsa_keys(password, key_size=3072):
        if not isinstance(password, str) or len(password) < 8:
            raise ValueError("Use a private-key password of at least 8 characters.")
        if key_size not in (2048, 3072, 4096):
            raise ValueError("RSA key size must be 2048, 3072, or 4096 bits.")

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size
        )
        public_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
        private_pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(password.encode("utf-8")),
        ).decode("utf-8")
        return public_pem, private_pem

    @staticmethod
    def rsa_encrypt(text, public_key_pem):
        try:
            key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Invalid RSA public key.") from None
        if not isinstance(key, rsa.RSAPublicKey):
            raise ValueError("A valid RSA public key is required.")

        message = text.encode("utf-8")
        limit = key.key_size // 8 - 66  # SHA-256 OAEP overhead
        if len(message) > limit:
            raise ValueError("Message is too long for RSA; use AES for longer text.")
        encrypted = key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode("ascii")

    @staticmethod
    def rsa_decrypt(text, private_key_pem, password):
        try:
            key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=password.encode("utf-8"),
            )
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Invalid RSA private key or password.") from None
        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValueError("A valid RSA private key is required.")

        try:
            decrypted = key.decrypt(
                Modern._from_base64(text),
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        except ValueError:
            raise ValueError("RSA ciphertext or key is incorrect.") from None
        return decrypted.decode("utf-8")

    @staticmethod
    def encrypt(algorithm, text, key):
        name = algorithm.strip().upper().replace("_", "-")
        if name in ("AES", "AES-GCM", "AES-256-GCM"):
            return Modern.aes_encrypt(text, key)
        if name in ("RSA", "RSA-OAEP"):
            return Modern.rsa_encrypt(text, key)
        raise ValueError(f"Unknown modern algorithm: {algorithm}")

    @staticmethod
    def decrypt(algorithm, text, key, password=""):
        name = algorithm.strip().upper().replace("_", "-")
        if name in ("AES", "AES-GCM", "AES-256-GCM"):
            return Modern.aes_decrypt(text, key)
        if name in ("RSA", "RSA-OAEP"):
            return Modern.rsa_decrypt(text, key, password)
        raise ValueError(f"Unknown modern algorithm: {algorithm}")
