"""Main window and sidebar navigation for CryptoLab."""

from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

from gui.cipher_studio import CipherStudio
from gui.cryptanalysis import CryptanalysisPage
from gui.hashing import HashingPage


PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_DIR = PROJECT_DIR / "assets" / "icons"
BANNER_FILE = PROJECT_DIR / "assets" / "images" / "banner.png"


class BannerLabel(QLabel):
    """Keep the dashboard banner proportional when the window is resized."""

    def __init__(self, image_path):
        super().__init__()
        self.image = QPixmap(str(image_path))
        self.setFixedHeight(200)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def resizeEvent(self, event):
        if not self.image.isNull():
            self.setPixmap(self.image.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        super().resizeEvent(event)


class CryptoLabWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptoLab - Cryptography & Security Suite")
        self.resize(1150, 750)
        self.setMinimumSize(850, 550)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 28, 16, 20)
        side_layout.setSpacing(12)

        brand = QLabel("CRYPTOLAB")
        brand.setObjectName("brand")
        side_layout.addWidget(brand)
        side_layout.addWidget(QLabel("SECURITY SUITE"))
        side_layout.addSpacing(25)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard())
        self.pages.addWidget(CipherStudio())
        self.pages.addWidget(CryptanalysisPage())
        self.pages.addWidget(HashingPage())

        navigation = [
            ("Dashboard", "dashboard.svg"),
            ("Cipher Studio", "cipher.svg"),
            ("Cryptanalysis", "cryptanalysis.svg"),
            ("Hashing", "hashing.svg"),
        ]

        self.nav_buttons = []
        for index, (name, icon_name) in enumerate(navigation):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            icon_path = ICON_DIR / icon_name
            if icon_path.exists():
                button.setIcon(QIcon(str(icon_path)))
                button.setIconSize(QSize(20, 20))
            button.clicked.connect(
                lambda checked=False, page=index: self.open_page(page)
            )
            side_layout.addWidget(button)
            self.nav_buttons.append(button)

        side_layout.addStretch()
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)

        # The global dark.qss stylesheet is loaded by main.py.
        self.open_page(0)

    def open_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def dashboard(self):
        page = QWidget()
        page.setObjectName("homePage")
        content = QVBoxLayout(page)
        content.setContentsMargins(45, 35, 45, 35)
        content.setSpacing(15)

        if BANNER_FILE.exists():
            content.addWidget(BannerLabel(BANNER_FILE))

        title = QLabel("Welcome to CryptoLab")
        title.setObjectName("pageTitle")
        message = QLabel(
            "Explore classical and modern encryption in one desktop application."
        )
        message.setObjectName("pageText")
        message.setWordWrap(True)

        start = QPushButton("Open Cipher Studio")
        start.setObjectName("openStudio")
        start.setFixedWidth(230)
        start.clicked.connect(lambda: self.open_page(1))

        content.addWidget(title)
        content.addWidget(message)
        content.addSpacing(15)
        content.addWidget(start)
        content.addStretch()
        return page

    @staticmethod
    def placeholder(title, message):
        page = QWidget()
        page.setObjectName("placeholderPage")
        content = QVBoxLayout(page)
        content.setContentsMargins(45, 45, 45, 45)
        content.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        info = QLabel(message)
        info.setObjectName("pageText")
        info.setWordWrap(True)
        content.addWidget(heading)
        content.addWidget(info)
        content.addStretch()
        return page


MainWindow = CryptoLabWindow
