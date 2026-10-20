"""Cryptanalysis page: demonstrate brute-force attacks on classical ciphers."""

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from analysis.brute_force import BruteForce


ICON_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


class CryptanalysisPage(QWidget):
    """Show candidate plaintexts by trying all keys for simple ciphers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = BruteForce()
        self.candidates = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(12)

        title = QLabel("CRYPTANALYSIS")
        title.setObjectName("heading")
        layout.addWidget(title)
        subtitle = QLabel("Try every possible key for selected classical ciphers.")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        settings = QHBoxLayout()
        settings.addWidget(QLabel("Algorithm"))
        self.algorithm = QComboBox()
        self.algorithm.addItems(["Caesar / Additive", "Affine", "Rail Fence"])
        settings.addWidget(self.algorithm, 1)
        settings.addWidget(QLabel("Max rails"))
        self.max_rails = QSpinBox()
        self.max_rails.setRange(2, 20)
        self.max_rails.setValue(8)
        self.max_rails.setEnabled(False)
        self.max_rails.setStyleSheet(
            "QSpinBox { background: #162238; color: #F5F9FF; "
            "border: 1px solid #344862; border-radius: 7px; padding: 6px; }"
        )
        settings.addWidget(self.max_rails)
        layout.addLayout(settings)

        layout.addWidget(QLabel("Ciphertext"))
        self.ciphertext = QPlainTextEdit("KHOOR")
        self.ciphertext.setPlaceholderText("Enter ciphertext to attack...")
        self.ciphertext.setFixedHeight(100)
        layout.addWidget(self.ciphertext)

        self.attack_button = QPushButton("Run Brute Force")
        icon = ICON_DIR / "cryptanalysis.svg"
        if icon.is_file():
            self.attack_button.setIcon(QIcon(str(icon)))
            self.attack_button.setIconSize(QSize(19, 19))
        layout.addWidget(self.attack_button)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Filter candidates"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by key or text, e.g. HELLO")
        search_row.addWidget(self.search, 1)
        layout.addLayout(search_row)

        self.results = QTableWidget(0, 2)
        self.results.setHorizontalHeaderLabels(["Key", "Possible plaintext"])
        self.results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results.setAlternatingRowColors(True)
        self.results.verticalHeader().setVisible(False)
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.setStyleSheet("""
            QTableWidget {
                background: #162238; alternate-background-color: #1B2A43;
                color: #EAF0FA; border: 1px solid #344862;
                gridline-color: #344862;
            }
            QTableWidget::item:selected { background: #176B9E; }
            QHeaderView::section {
                background: #203B59; color: #EAF0FA;
                border: 1px solid #344862; padding: 8px;
            }
        """)
        layout.addWidget(self.results, 1)

        self.copy_button = QPushButton("Copy Selected Plaintext")
        layout.addWidget(self.copy_button)

        self.status = QLabel("Example: KHOOR with Caesar has plaintext HELLO at key 3.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.algorithm.currentTextChanged.connect(self.update_algorithm)
        self.attack_button.clicked.connect(self.run_attack)
        self.search.textChanged.connect(self.filter_results)
        self.copy_button.clicked.connect(self.copy_selected)

    def update_algorithm(self, name):
        self.max_rails.setEnabled(name == "Rail Fence")
        self.results.setRowCount(0)
        self.candidates = []
        self.status.setText("Enter ciphertext and select Run Brute Force.")

    def run_attack(self):
        name = self.algorithm.currentText()
        algorithm = "Caesar" if name == "Caesar / Additive" else name
        try:
            candidates = self.engine.attack(
                algorithm,
                self.ciphertext.toPlainText(),
                max_rails=self.max_rails.value(),
            )
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self, "Attack failed", str(error))
            return

        self.candidates = candidates
        self.results.setRowCount(len(candidates))
        for row, candidate in enumerate(candidates):
            self.results.setItem(row, 0, QTableWidgetItem(str(candidate["key"])))
            self.results.setItem(row, 1, QTableWidgetItem(candidate["plaintext"]))
        self.filter_results()

    def filter_results(self, *_):
        query = self.search.text().strip().upper()
        visible = 0
        for row, candidate in enumerate(self.candidates):
            match = query in str(candidate["key"]).upper() or query in candidate["plaintext"].upper()
            self.results.setRowHidden(row, not match)
            if match:
                visible += 1
        self.status.setText(
            f"Showing {visible} of {len(self.candidates)} candidates. "
            "Brute force lists possibilities; you choose the meaningful plaintext."
        )

    def copy_selected(self):
        row = self.results.currentRow()
        if row < 0 or self.results.isRowHidden(row):
            QMessageBox.information(self, "Select a result", "Choose a plaintext row first.")
            return
        item = self.results.item(row, 1)
        if item is not None:
            QApplication.clipboard().setText(item.text())
            self.status.setText("Selected plaintext copied to clipboard.")
