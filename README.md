# CryptoLab

**An educational desktop application for exploring classical and modern cryptography.**

![CryptoLab banner](assets/images/banner.png)

CryptoLab is a Python desktop application built with **PySide6**. It brings encryption, decryption, brute-force cryptanalysis, and hashing into one dark-themed graphical interface. The project is designed for learning and demonstrating cryptographic concepts.

## Features

### Cipher Studio
- Encrypt and decrypt text with classical algorithms: Caesar, Additive, Multiplicative, Affine, Atbash, Monoalphabetic Substitution, Vigenère, Autokey, Playfair, Hill, Rail Fence, Row Transposition, Columnar Transposition, and Double Transposition.
- Demonstrate modern encryption using **AES-GCM** and **RSA-OAEP**.
- Generate AES keys and RSA key pairs through the interface.
- Copy results and reuse ciphertext as input for decryption.

### Cryptanalysis
- Perform brute-force attacks against **Caesar/Additive**, **Affine**, and **Rail Fence** ciphers.
- View possible plaintexts alongside their candidate keys.
- Filter results to find meaningful messages.

### Hashing
- Generate text and file hashes using **SHA-256**, **SHA-512**, **SHA3-256**, **MD5**, and **SHA-1**.
- Verify text hashes to demonstrate data integrity.
- Generate and verify **HMAC** signatures.
- Demonstrate salted password hashing and verification using **PBKDF2-HMAC-SHA256**.

### Desktop Interface
- Dark cybersecurity-inspired theme with icons and a dashboard.
- Four sections: **Dashboard**, **Cipher Studio**, **Cryptanalysis**, and **Hashing**.

## Technologies

- **Python** — application logic
- **PySide6** — graphical user interface
- **pycipher** — classical cipher implementations
- **SymPy** — Hill cipher matrix mathematics
- **cryptography** — AES-GCM and RSA-OAEP
- Python standard library (`hashlib`, `hmac`, `secrets`) — hashing and key generation utilities

## Installation and Running

1. Install Python and download or clone this repository.
2. Open a terminal in the `CryptoLab` project folder.
3. On Windows, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Alternatively, if you already have an active Python environment with the dependencies installed:

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Quick Example

**Encryption:** In Cipher Studio, select Caesar, enter `HELLO`, and use key `3` to produce `KHOOR`.

**Cryptanalysis:** Enter `KHOOR` in the Cryptanalysis page, select Caesar/Additive, and run brute force. The candidates include `HELLO` with key `3`.

**Hashing:** In the Hashing page, enter a message, select SHA-256, and generate a digest. Change the message and verify that the hash no longer matches.

## Project Structure

```text
CryptoLab/
├── main.py
├── gui/
│   ├── main_window.py
│   ├── cipher_studio.py
│   ├── cryptanalysis.py
│   └── hashing.py
├── crypto_engine/
│   ├── classical.py
│   ├── modern.py
│   └── hashing.py
├── analysis/
│   └── brute_force.py
├── assets/
│   ├── icons/
│   ├── images/
│   └── styles/
├── tests/
│   └── test_ciphers.py
└── requirements.txt
```

## Running Tests

From the project directory:

```powershell
python -m unittest discover -s tests -v
```

## Educational and Security Notes

- **Classical ciphers are not secure for real-world communication.** They are included for educational demonstrations.
- Classical cipher input is generally normalized to uppercase English letters (A–Z); spaces and punctuation may be removed, and some algorithms add padding.
- **Hashing is not encryption:** a cryptographic hash is a one-way digest, not something you decrypt.
- **MD5 and SHA-1 are insecure against collisions** and are included only to illustrate older algorithms.
- Modern encryption features use the `cryptography` library, but this project is a learning tool rather than an audited security product.
- Never commit actual private keys, passwords, or other secrets to this repository.
