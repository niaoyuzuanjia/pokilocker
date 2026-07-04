"""
关于 — WinUI3 风格
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import PushButton
import pokilocker


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 pokilocker")
        self.setFixedSize(380, 280)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 24, 30, 20)

        name = QLabel("pokilocker")
        name.setFont(QFont("Segoe UI Variable", 20, QFont.Bold))
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        ver = QLabel(f"v{pokilocker.__version__}")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        desc = QLabel(
            "Windows 网站访问管理工具\n"
            "made by 鸟语砖家\n"
            "一切开德都是反对派，纸老虎")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = PushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)
