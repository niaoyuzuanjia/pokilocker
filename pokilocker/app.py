"""
pokilocker 应用入口 — WinUI3 风格
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from qfluentwidgets import setTheme, Theme, setThemeColor

from pokilocker.config import ConfigManager
from pokilocker.main_window import MainWindow


def main():
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    app = QApplication(sys.argv)
    app.setApplicationName("pokilocker")
    app.setOrganizationName("pokilocker")

    # Segoe UI Variable — WinUI3 默认开源字体
    font = QFont("Segoe UI Variable", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # WinUI3 Fluent 主题
    setTheme(Theme.LIGHT)
    setThemeColor("#0078D4")

    config = ConfigManager()
    config.load()

    window = MainWindow(config)
    window.apply_on_startup()

    if config.get("start_minimized", False):
        window.hide()
        if not config.get("stealth_mode", False):
            window.show_startup_notification()
    else:
        window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
