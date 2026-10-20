
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from gui.main_window import CryptoLabWindow


def main():
    app = QApplication(sys.argv)

    # Project folder
    base_path = Path(__file__).resolve().parent

    # Load dark theme
    style_path = base_path / "assets" / "styles" / "dark.qss"

    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))

    # Load application icon
    icon_path = base_path / "assets" / "icons" / "app_icon.ico"

    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Start CryptoLab
    window = CryptoLabWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
