"""Cipher Studio page for CryptoLab (PySide6)."""

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QVBoxLayout,
    QWidget,
)

from crypto_engine.classical import Classical
from crypto_engine.modern import Modern


ICON_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


class CipherStudio(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.classical = Classical()
        self.modern = Modern()
        self.setObjectName("cipherStudio")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        content = QVBoxLayout(body)
        content.setContentsMargins(26, 22, 26, 22)
        content.setSpacing(12)

        heading = QLabel("CIPHER STUDIO")
        heading.setObjectName("heading")
        content.addWidget(heading)
        content.addWidget(QLabel("Choose an algorithm, enter text, and encrypt or decrypt."))

        self.algorithm = QComboBox()
        self.algorithm.addItems(list(Classical.ALGORITHMS) + ["AES-GCM", "RSA-OAEP"])
        content.addWidget(QLabel("Algorithm"))
        content.addWidget(self.algorithm)

        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText("Enter plaintext to encrypt, or ciphertext to decrypt...")
        self.input_text.setFixedHeight(105)
        content.addWidget(QLabel("Input"))
        content.addWidget(self.input_text)

        self.key_input = QLineEdit()
        self.key_row = self._field(content, "Key", self.key_input)

        self.generate_aes_button = QPushButton("Generate AES Key")
        content.addWidget(self.generate_aes_button)

        self.a_input = QLineEdit("5")
        self.a_row = self._field(content, "Affine key a", self.a_input)
        self.b_input = QLineEdit("8")
        self.b_row = self._field(content, "Affine key b", self.b_input)

        self.key2_input = QLineEdit("KEY")
        self.key2_row = self._field(content, "Second keyword", self.key2_input)

        self.matrix_input = QLineEdit("3,3;2,5")
        self.matrix_row = self._field(content, "Hill matrix (rows separated by ;)", self.matrix_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("At least 8 characters when generating RSA keys")
        self.password_row = self._field(content, "RSA private-key password", self.password_input)

        self.generate_rsa_button = QPushButton("Generate RSA Key Pair")
        content.addWidget(self.generate_rsa_button)

        self.public_key = QPlainTextEdit()
        self.public_key.setPlaceholderText("Paste RSA public key (PEM)")
        self.public_key.setFixedHeight(94)
        self.public_row = self._field(content, "RSA public key", self.public_key, vertical=True)

        self.private_key = QPlainTextEdit()
        self.private_key.setPlaceholderText("Paste RSA private key (PEM)")
        self.private_key.setFixedHeight(94)
        self.private_row = self._field(content, "RSA private key — do not share", self.private_key, vertical=True)

        buttons = QHBoxLayout()
        self.encrypt_button = QPushButton("Encrypt")
        self.decrypt_button = QPushButton("Decrypt")
        self.swap_button = QPushButton("Use Output as Input")
        for button in (self.encrypt_button, self.decrypt_button, self.swap_button):
            buttons.addWidget(button)
        content.addLayout(buttons)

        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFixedHeight(115)
        content.addWidget(QLabel("Output"))
        content.addWidget(self.output_text)

        extras = QHBoxLayout()
        self.copy_button = QPushButton("Copy Output")
        self.clear_button = QPushButton("Clear Text")
        extras.addWidget(self.copy_button)
        extras.addWidget(self.clear_button)
        content.addLayout(extras)

        for button, icon_name in (
            (self.encrypt_button, "encrypt.svg"),
            (self.decrypt_button, "decrypt.svg"),
            (self.generate_aes_button, "key.svg"),
            (self.generate_rsa_button, "key.svg"),
            (self.copy_button, "copy.svg"),
            (self.clear_button, "clear.svg"),
        ):
            self._add_icon(button, icon_name)

        self.status = QLabel("Classical ciphers use A-Z only and may add padding.")
        self.status.setWordWrap(True)
        content.addWidget(self.status)
        content.addStretch()

        scroll.setWidget(body)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Colors and widget styling come from assets/styles/dark.qss via main.py.

        self.algorithm.currentTextChanged.connect(self.update_fields)
        self.encrypt_button.clicked.connect(lambda: self.process(False))
        self.decrypt_button.clicked.connect(lambda: self.process(True))
        self.generate_aes_button.clicked.connect(self.generate_aes_key)
        self.generate_rsa_button.clicked.connect(self.generate_rsa_keys)
        self.swap_button.clicked.connect(self.use_output)
        self.copy_button.clicked.connect(self.copy_output)
        self.clear_button.clicked.connect(self.clear_text)
        self.update_fields()

    @staticmethod
    def _add_icon(button, icon_name):
        path = ICON_DIR / icon_name
        if path.is_file():
            button.setIcon(QIcon(str(path)))
            button.setIconSize(QSize(19, 19))

    @staticmethod
    def _field(layout, label, editor, vertical=False):
        row = QWidget()
        line = QVBoxLayout(row) if vertical else QHBoxLayout(row)
        line.setContentsMargins(0, 0, 0, 0)
        line.addWidget(QLabel(label))
        line.addWidget(editor)
        layout.addWidget(row)
        return row

    def update_fields(self, *_):
        name = self.algorithm.currentText()
        is_rsa = name == "RSA-OAEP"
        is_aes = name == "AES-GCM"
        self.key_row.setVisible(name not in ("Atbash", "Affine", "Hill", "RSA-OAEP"))
        self.a_row.setVisible(name == "Affine")
        self.b_row.setVisible(name == "Affine")
        self.matrix_row.setVisible(name == "Hill")
        self.key2_row.setVisible(name == "Double Transposition")
        self.password_row.setVisible(is_rsa)
        self.public_row.setVisible(is_rsa)
        self.private_row.setVisible(is_rsa)
        self.generate_aes_button.setVisible(is_aes)
        self.generate_rsa_button.setVisible(is_rsa)

        examples = {
            "Caesar": "3", "Additive": "5", "Multiplicative": "5",
            "Monoalphabetic": "QWERTYUIOPASDFGHJKLZXCVBNM",
            "Vigenere": "KEY", "Autokey": "KEY", "Playfair": "MONARCHY",
            "Rail Fence": "2", "Row": "4", "Columnar": "ZEBRA",
            "Double Transposition": "ZEBRA", "AES-GCM": "",
        }
        self.key_input.setText(examples.get(name, ""))
        self.output_text.clear()
        self.status.setText(
            "AES-GCM preserves text, including spaces" if is_aes else
            "RSA-OAEP is intended for short messages; keep the private key secret." if is_rsa else
            "Classical ciphers use uppercase A-Z"
        )

    def _classical_options(self, name):
        if name == "Affine":
            return {"a": int(self.a_input.text()), "b": int(self.b_input.text())}
        if name == "Hill":
            rows = self.matrix_input.text().split(";")
            matrix = [[int(value.strip()) for value in row.split(",")] for row in rows]
            return {"matrix": matrix}
        key = self.key_input.text()
        if name == "Double Transposition":
            return {"key": key, "key2": self.key2_input.text()}
        if name in ("Caesar", "Additive", "Multiplicative", "Rail Fence", "Row"):
            return {"key": int(key)}
        return {"key": key}

    def process(self, decrypt=False):
        name = self.algorithm.currentText()
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Missing text", "Enter text first.")
            return
        try:
            if name == "AES-GCM":
                method = self.modern.aes_decrypt if decrypt else self.modern.aes_encrypt
                result = method(text, self.key_input.text().strip())
            elif name == "RSA-OAEP":
                if decrypt:
                    result = self.modern.rsa_decrypt(
                        text, self.private_key.toPlainText(), self.password_input.text()
                    )
                else:
                    result = self.modern.rsa_encrypt(text, self.public_key.toPlainText())
            else:
                method = self.classical.decrypt if decrypt else self.classical.encrypt
                result = method(name, text, **self._classical_options(name))
            self.output_text.setPlainText(result)
            self.status.setText("Decryption completed." if decrypt else "Encryption completed.")
        except Exception as error:
            QMessageBox.warning(self, "Operation failed", str(error))

    def generate_aes_key(self):
        self.key_input.setText(self.modern.generate_aes_key())
        self.status.setText("New AES key generated. Save it securely to decrypt later.")

    def generate_rsa_keys(self):
        try:
            public, private = self.modern.generate_rsa_keys(self.password_input.text())
            self.public_key.setPlainText(public)
            self.private_key.setPlainText(private)
            self.status.setText("RSA keys generated. Keep the private key and password secret.")
        except ValueError as error:
            QMessageBox.warning(self, "Key generation failed", str(error))

    def use_output(self):
        self.input_text.setPlainText(self.output_text.toPlainText())

    def copy_output(self):
        QApplication.clipboard().setText(self.output_text.toPlainText())

    def clear_text(self):
        self.input_text.clear()
        self.output_text.clear()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = CipherStudio()
    window.resize(900, 730)
    window.show()
    sys.exit(app.exec())
