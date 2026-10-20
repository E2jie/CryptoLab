
import unittest

from crypto_engine.classical import Classical


class TestCiphers(unittest.TestCase):

    def setUp(self):
        self.crypto = Classical()

    def test_caesar(self):
        encrypted = self.crypto.encrypt("Caesar", "HELLO", key=3)
        self.assertEqual(encrypted, "KHOOR")
        self.assertEqual(
            self.crypto.decrypt("Caesar", encrypted, key=3),
            "HELLO"
        )

    def test_additive(self):
        encrypted = self.crypto.encrypt("Additive", "DOG", key=5)
        self.assertEqual(encrypted, "ITL")

    def test_multiplicative(self):
        encrypted = self.crypto.encrypt("Multiplicative", "CAT", key=7)
        self.assertEqual(encrypted, "OAD")

    def test_affine(self):
        encrypted = self.crypto.encrypt("Affine", "CAT", a=5, b=8)
        self.assertEqual(encrypted, "SIZ")
        self.assertEqual(
            self.crypto.decrypt("Affine", encrypted, a=5, b=8),
            "CAT"
        )

    def test_vigenere(self):
        encrypted = self.crypto.encrypt("Vigenere", "HELLO", key="KEY")
        self.assertEqual(encrypted, "RIJVS")

    def test_hill(self):
        matrix = [[3, 3], [2, 5]]
        encrypted = self.crypto.encrypt("Hill", "HI", matrix=matrix)
        self.assertEqual(encrypted, "TC")

    def test_invalid_affine_key(self):
        with self.assertRaises(ValueError):
            self.crypto.encrypt("Affine", "HELLO", a=6, b=5)

    def test_invalid_hill_key(self):
        with self.assertRaises(ValueError):
            self.crypto.encrypt(
                "Hill", "HELLO",
                matrix=[[2, 4], [3, 6]]
            )


if __name__ == "__main__":
    unittest.main()
