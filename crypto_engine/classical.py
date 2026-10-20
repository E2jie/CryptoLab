"""Classical cipher helpers for CryptoLab.

Educational ciphers only; not suitable for protecting sensitive data.
"""

from math import gcd
from string import ascii_uppercase

from pycipher import (
    Affine,
    Atbash,
    Autokey,
    Caesar,
    ColTrans,
    Playfair,
    Railfence,
    SimpleSubstitution,
    Vigenere,
)
from sympy import Matrix


def _letters(text):
    """Use the English A-Z alphabet, as in the course exercises."""
    return "".join(char for char in text.upper() if char in ascii_uppercase)


def _keyword(key):
    """Check that a keyword consists only of English letters."""
    if not isinstance(key, str) or not key or any(c not in ascii_uppercase for c in key.upper()):
        raise ValueError("Enter a keyword containing only English letters (A-Z).")
    return key.upper()


def _integer(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer.")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be an integer.") from None


def _playfair_square(keyword):
    """Turn a keyword into the 25-letter Playfair key square (I/J merged)."""
    sequence = _keyword(keyword).replace("J", "I") + ascii_uppercase.replace("J", "")
    return "".join(dict.fromkeys(sequence))


def _playfair_prepare(text):
    """Insert filler X between repeated letters, and pad odd-length text."""
    text = _letters(text).replace("J", "I")
    pairs = []
    i = 0
    while i < len(text):
        first = text[i]
        second = text[i + 1] if i + 1 < len(text) else ""
        if not second or first == second:
            pairs.append(first + ("Q" if first == "X" else "X"))
            i += 1
        else:
            pairs.append(first + second)
            i += 2
    return "".join(pairs)


def _hill(text, key_matrix, decrypt=False):
    """Hill cipher with 2x2 or 3x3 numerical matrices, modulo 26."""
    if key_matrix is None:
        raise ValueError("Hill cipher requires a 2x2 or 3x3 matrix.")
    try:
        matrix = Matrix(key_matrix)
    except (TypeError, ValueError):
        raise ValueError("Provide a numerical key matrix.") from None

    if matrix.rows != matrix.cols or matrix.rows not in (2, 3):
        raise ValueError("Hill cipher supports only 2x2 and 3x3 matrices.")
    if any(value.is_integer is not True for value in matrix):
        raise ValueError("All Hill matrix values must be integers.")
    if gcd(int(matrix.det()), 26) != 1:
        raise ValueError("Invalid Hill key: its determinant has no inverse modulo 26.")

    size = matrix.rows
    text = _letters(text)
    if decrypt:
        if len(text) % size:
            raise ValueError("Ciphertext length must be a multiple of the matrix size.")
        matrix = matrix.inv_mod(26)
    else:
        text += "X" * (-len(text) % size)

    result = ""
    for i in range(0, len(text), size):
        vector = Matrix([ord(char) - 65 for char in text[i:i + size]])
        result += "".join(chr(int(number) % 26 + 65) for number in matrix * vector)
    return result


class Classical:
    """One interface for the classical cipher algorithms used by the GUI."""

    ALGORITHMS = (
        "Caesar", "Additive", "Multiplicative", "Affine", "Atbash",
        "Monoalphabetic", "Vigenere", "Autokey", "Playfair", "Hill",
        "Rail Fence", "Row", "Columnar", "Double Transposition",
    )

    def encrypt(self, algorithm, text, key=None, a=None, b=None, key2=None, matrix=None):
        return self._run(algorithm, text, False, key, a, b, key2, matrix)

    def decrypt(self, algorithm, text, key=None, a=None, b=None, key2=None, matrix=None):
        return self._run(algorithm, text, True, key, a, b, key2, matrix)

    @staticmethod
    def _run(algorithm, text, decrypt, key, a, b, key2, matrix):
        name = algorithm.lower().replace("_", " ").replace("-", " ").strip()
        text = _letters(text)

        if name == "caesar":
            cipher = Caesar(3 if key is None else _integer(key, "Key"))
        elif name == "additive":
            cipher = Caesar(_integer(key, "Key"))
        elif name == "multiplicative":
            number = _integer(key, "Key")
            if gcd(number, 26) != 1:
                raise ValueError("Multiplicative key must be coprime with 26.")
            cipher = Affine(number, 0)
        elif name == "affine":
            first = _integer(a, "a")
            second = _integer(b, "b")
            if gcd(first, 26) != 1:
                raise ValueError("Affine key 'a' must be coprime with 26.")
            cipher = Affine(first, second)
        elif name == "atbash":
            cipher = Atbash()
        elif name in ("monoalphabetic", "monoalphabetic substitution"):
            substitution = _keyword(key)
            if len(substitution) != 26 or len(set(substitution)) != 26:
                raise ValueError("Substitution key must contain all 26 letters exactly once.")
            cipher = SimpleSubstitution(substitution)
        elif name == "vigenere":
            cipher = Vigenere(_keyword(key))
        elif name == "autokey":
            cipher = Autokey(_keyword(key))
        elif name == "playfair":
            cipher = Playfair(_playfair_square(key))
            if not decrypt:
                text = _playfair_prepare(text)
            elif len(text) % 2:
                raise ValueError("Playfair ciphertext must have an even number of letters.")
        elif name == "hill":
            return _hill(text, matrix if matrix is not None else key, decrypt)
        elif name in ("rail fence", "railfence"):
            rails = _integer(key, "Rails")
            if rails < 2:
                raise ValueError("Rail Fence needs at least 2 rails.")
            cipher = Railfence(rails)
        elif name in ("row", "row transposition"):
            width = _integer(key, "Columns")
            if not 2 <= width <= 26:
                raise ValueError("Row transposition needs 2 to 26 columns.")
            cipher = ColTrans(ascii_uppercase[:width])
        elif name in ("columnar", "columnar transposition"):
            cipher = ColTrans(_keyword(key))
        elif name in ("double transposition", "double columnar"):
            first = ColTrans(_keyword(key))
            second = ColTrans(_keyword(key2))
            if decrypt:
                return first.decipher(second.decipher(text))
            return second.encipher(first.encipher(text))
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return cipher.decipher(text) if decrypt else cipher.encipher(text)


if __name__ == "__main__":
    crypto = Classical()
    encrypted = crypto.encrypt("Caesar", "HELLO", key=3)
    print("Encrypted:", encrypted)
    print("Decrypted:", crypto.decrypt("Caesar", encrypted, key=3))
