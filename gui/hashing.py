"""Hashing page for CryptoLab."""

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from crypto_engine.hashing import Hashing


ICON_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


class HashingPage(QWidget):
    """Generate and verify hashes, HMACs, and password hashes."""

    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(12)

        title = QLabel("HASHING")
        title.setObjectName("heading")
        layout.addWidget(title)
        info = QLabel("Generate hashes and check whether text or a message has changed.")
        info.setWordWrap(True)
        layout.addWidget(info)

        self._section(layout, "1. Text and file hashing")
        layout.addWidget(QLabel("Text"))
        self.text = QPlainTextEdit("Hello CryptoLab")
        self.text.setFixedHeight(90)
        layout.addWidget(self.text)

        row = QHBoxLayout()
        self.algorithm = QComboBox()
        for name, value in (
            ("SHA-256", "sha256"),
            ("SHA-512", "sha512"),
            ("SHA3-256", "sha3_256"),
            ("MD5 (legacy, insecure)", "md5"),
            ("SHA-1 (legacy, insecure)", "sha1"),
        ):
            self.algorithm.addItem(name, value)
        row.addWidget(self.algorithm, 2)
        self.hash_button = self._button("Hash Text", "hashing.svg")
        self.file_button = QPushButton("Hash File...")
        row.addWidget(self.hash_button)
        row.addWidget(self.file_button)
        layout.addLayout(row)

        self.output = QLineEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Hash result")
        layout.addWidget(self.output)

        row = QHBoxLayout()
        self.expected = QLineEdit()
        self.expected.setPlaceholderText("Paste expected text hash")
        row.addWidget(self.expected, 1)
        self.verify_button = QPushButton("Verify Text Hash")
        self.copy_button = self._button("Copy Hash", "copy.svg")
        row.addWidget(self.verify_button)
        row.addWidget(self.copy_button)
        layout.addLayout(row)

        self._section(layout, "2. HMAC authentication")
        layout.addWidget(QLabel("HMAC uses the text above and a secret key."))
        row = QHBoxLayout()
        self.hmac_key = QLineEdit()
        self.hmac_key.setPlaceholderText("Hexadecimal secret key")
        row.addWidget(self.hmac_key, 1)
        self.key_button = self._button("Generate Key", "key.svg")
        row.addWidget(self.key_button)
        layout.addLayout(row)

        row = QHBoxLayout()
        self.hmac_output = QLineEdit()
        self.hmac_output.setReadOnly(True)
        self.hmac_output.setPlaceholderText("Generated HMAC-SHA256")
        row.addWidget(self.hmac_output, 1)
        self.hmac_button = QPushButton("Generate HMAC")
        row.addWidget(self.hmac_button)
        layout.addLayout(row)

        row = QHBoxLayout()
        self.expected_hmac = QLineEdit()
        self.expected_hmac.setPlaceholderText("Paste HMAC to verify")
        row.addWidget(self.expected_hmac, 1)
        self.verify_hmac_button = QPushButton("Verify HMAC")
        row.addWidget(self.verify_hmac_button)
        layout.addLayout(row)

        self._section(layout, "3. Password hashing")
        row = QHBoxLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter a password")
        row.addWidget(self.password, 1)
        self.password_button = QPushButton("Hash Password")
        self.verify_password_button = QPushButton("Verify Password")
        row.addWidget(self.password_button)
        row.addWidget(self.verify_password_button)
        layout.addLayout(row)

        self.password_output = QLineEdit()
        self.password_output.setPlaceholderText("PBKDF2 saved password hash")
        layout.addWidget(self.password_output)

        self.status = QLabel("MD5 and SHA-1 are included only for educational comparison.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

        scroll.setWidget(body)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.hash_button.clicked.connect(self.hash_text)
        self.file_button.clicked.connect(self.hash_file)
        self.verify_button.clicked.connect(self.verify_hash)
        self.copy_button.clicked.connect(self.copy_hash)
        self.key_button.clicked.connect(self.generate_key)
        self.hmac_button.clicked.connect(self.generate_hmac)
        self.verify_hmac_button.clicked.connect(self.verify_hmac)
        self.password_button.clicked.connect(self.hash_password)
        self.verify_password_button.clicked.connect(self.verify_password)

    @staticmethod
    def _section(layout, text):
        label = QLabel(text)
        label.setStyleSheet("color: #69D4FF; font-weight: bold; font-size: 16px;")
        layout.addWidget(label)

    @staticmethod
    def _button(text, icon_name):
        button = QPushButton(text)
        icon = ICON_DIR / icon_name
        if icon.is_file():
            button.setIcon(QIcon(str(icon)))
            button.setIconSize(QSize(18, 18))
        return button

    def _error(self, message):
        QMessageBox.warning(self, "Operation failed", str(message))

    def hash_text(self):
        self.output.setText(Hashing.hash_text(self.text.toPlainText(), self.algorithm.currentData()))
        self.status.setText("Text hash generated. You can copy or verify it.")

    def hash_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choose a file")
        if not filename:
            return
        try:
            self.output.setText(Hashing.hash_file(filename, self.algorithm.currentData()))
            self.status.setText(f"File hash generated: {Path(filename).name}")
        except (ValueError, OSError) as error:
            self._error(error)

    def verify_hash(self):
        if not self.expected.text().strip():
            self._error("Paste an expected text hash first.")
            return
        matches = Hashing.verify_hash(
            self.text.toPlainText(), self.expected.text(), self.algorithm.currentData()
        )
        self.status.setText("Text hash matches." if matches else "Text hash does NOT match.")

    def copy_hash(self):
        QApplication.clipboard().setText(self.output.text())
        self.status.setText("Hash copied to clipboard.")

    def generate_key(self):
        self.hmac_key.setText(Hashing.generate_key())
        self.status.setText("HMAC secret key generated. Keep it private.")

    def generate_hmac(self):
        try:
            digest = Hashing.generate_hmac(self.text.toPlainText(), self.hmac_key.text(), "sha256")
            self.hmac_output.setText(digest)
            self.status.setText("HMAC-SHA256 generated.")
        except ValueError as error:
            self._error(error)

    def verify_hmac(self):
        if not self.expected_hmac.text().strip():
            self._error("Paste an HMAC to verify first.")
            return
        try:
            matches = Hashing.verify_hmac(
                self.text.toPlainText(), self.hmac_key.text(), self.expected_hmac.text(), "sha256"
            )
            self.status.setText("HMAC matches." if matches else "HMAC does NOT match.")
        except ValueError as error:
            self._error(error)

    def hash_password(self):
        if not self.password.text():
            self._error("Enter a password first.")
            return
        self.password_output.setText(Hashing.hash_password(self.password.text()))
        self.status.setText("Salted PBKDF2 password hash generated.")

    def verify_password(self):
        if not self.password_output.text().strip():
            self._error("Generate or paste a saved password hash first.")
            return
        matches = Hashing.verify_password(self.password.text(), self.password_output.text())
        self.status.setText("Password matches." if matches else "Password does NOT match.")
