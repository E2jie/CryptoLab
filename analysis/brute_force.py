"""Simple classical cipher brute-force tools for CryptoLab."""

from math import gcd

from crypto_engine.classical import Classical


class BruteForce:
    def __init__(self):
        self.crypto = Classical()

    @staticmethod
    def _clean(text):
        if not isinstance(text, str):
            raise ValueError("Ciphertext must be a string.")
        cleaned = "".join(c for c in text.upper() if "A" <= c <= "Z")
        if not cleaned:
            raise ValueError("Enter ciphertext containing English letters (A-Z).")
        return cleaned

    def caesar(self, ciphertext):
        text = self._clean(ciphertext)
        results = []

        for key in range(26):
            plaintext = self.crypto.decrypt("Caesar", text, key=key)
            results.append({"key": key, "plaintext": plaintext})

        return results

    def affine(self, ciphertext):
        text = self._clean(ciphertext)
        results = []

        for a in range(1, 26):
            if gcd(a, 26) != 1:
                continue
            for b in range(26):
                plaintext = self.crypto.decrypt("Affine", text, a=a, b=b)
                results.append({"key": f"a={a}, b={b}", "plaintext": plaintext})

        return results

    def rail_fence(self, ciphertext, max_rails=10):
        text = self._clean(ciphertext)
        if not isinstance(max_rails, int) or max_rails < 2:
            raise ValueError("max_rails must be an integer of at least 2.")

        results = []
        for rails in range(2, min(max_rails, len(text)) + 1):
            plaintext = self.crypto.decrypt("Rail Fence", text, key=rails)
            results.append({"key": rails, "plaintext": plaintext})

        return results

    def attack(self, algorithm, ciphertext, max_rails=10):
        name = algorithm.lower().strip()

        if name in ("caesar", "additive"):
            return self.caesar(ciphertext)
        if name == "affine":
            return self.affine(ciphertext)
        if name in ("rail fence", "railfence"):
            return self.rail_fence(ciphertext, max_rails)

        raise ValueError(f"Unsupported brute-force algorithm: {algorithm}")


if __name__ == "__main__":
    attack = BruteForce()
    for candidate in attack.caesar("KHOOR"):
        print(candidate)
