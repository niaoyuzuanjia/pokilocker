"""
设置 — 标准 PyQt5 控件
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QFileDialog, QGroupBox, QMessageBox,
)
from PyQt5.QtCore import Qt
from pokilocker.autostart import (
    is_auto_start_enabled, enable_auto_start, disable_auto_start,
)


class SettingsDialog(QDialog):

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("pokilocker 设置")
        self.setMinimumSize(420, 280)
        self.resize(480, 360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(20, 16, 20, 16)

        # 配置文件
        cfg_group = QGroupBox("配置文件保存位置")
        cgl = QVBoxLayout()
        pl = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        pl.addWidget(self.path_edit)
        b = QPushButton("浏览...")
        b.setFixedWidth(70)
        b.clicked.connect(self._browse_dir)
        pl.addWidget(b)
        cgl.addLayout(pl)
        cgl.addWidget(QLabel("选择保存目录，重启后生效。"))
        cfg_group.setLayout(cgl)
        layout.addWidget(cfg_group)

        # 启动行为
        auto_group = QGroupBox("启动行为")
        agl = QVBoxLayout()
        self.auto_check = QCheckBox("开机自动启动 pokilocker")
        agl.addWidget(self.auto_check)
        self.stealth_check = QCheckBox("隐秘模式（不显示托盘，关闭即退出）")
        agl.addWidget(self.stealth_check)
        agl.addWidget(QLabel("启用自动启动后，登录 Windows 时自动加载规则。"))
        auto_group.setLayout(agl)
        layout.addWidget(auto_group)

        layout.addStretch()

        bl = QHBoxLayout()
        bl.addStretch()
        cb = QPushButton("关闭")
        cb.clicked.connect(self.accept)
        bl.addWidget(cb)
        ab = QPushButton("应用")
        ab.clicked.connect(self._apply)
        bl.addWidget(ab)
        layout.addLayout(bl)

        self.setLayout(layout)

    def _load(self):
        self.path_edit.setText(self.config.get("config_dir", ""))
        self.auto_check.setChecked(is_auto_start_enabled())
        self.stealth_check.setChecked(self.config.get("stealth_mode", False))

    def _browse_dir(self):
        cur = self.config.get("config_dir", "")
        if not cur:
            from pokilocker.config import get_default_config_dir
            cur = get_default_config_dir()
        f = QFileDialog.getExistingDirectory(self, "选择目录", cur)
        if f:
            self.path_edit.setText(f)

    def _apply(self):
        nd = self.path_edit.text().strip()
        if nd and nd != self.config.get("config_dir", ""):
            self.config.set("config_dir", nd)
            self.config.config_dir = nd
            self.config.config_path = os.path.join(nd, "pokilocker_config.json")
            self.config.set("config_file", self.config.config_path)
            self.config.save()
            QMessageBox.information(self, "提示", f"目录已更新:\n{nd}\n重启后生效。")

        want = self.auto_check.isChecked()
        cur = is_auto_start_enabled()
        if want and not cur:
            ok = enable_auto_start()
            QMessageBox.information(self, "提示",
                                    "已启用开机自启动。" if ok else "设置失败，请检查权限。")
        elif not want and cur:
            disable_auto_start()
            QMessageBox.information(self, "提示", "已禁用开机自启动。")

        self.config.set("stealth_mode", self.stealth_check.isChecked())
        self.config.save()
