"""
主窗口 — WinUI3 风格，网格布局
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSystemTrayIcon, QMenu, QAction,
    QTabWidget, QGridLayout, QLineEdit, QInputDialog, QPushButton,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    SwitchButton, PrimaryPushButton, PushButton, MessageBox,
)
import sys

from pokilocker.config import GAME_SITES, VIDEO_SITES
from pokilocker.blocker import apply_blocking, clear_all_blocking, is_admin
from pokilocker.settings_dialog import SettingsDialog
from pokilocker.about_dialog import AboutDialog

COLS = 4


class SiteCard(QWidget):

    def __init__(self, site_key, site_name, checked=False, parent=None,
                 is_custom=False, on_delete=None):
        super().__init__(parent)
        self.site_key = site_key
        self.site_name = site_name

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 删除按钮（仅自定义站点显示）
        if is_custom:
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(20, 20)
            del_btn.setToolTip(f"移除 {site_name}")
            del_btn.clicked.connect(lambda: on_delete and on_delete(site_key))
            dl = QHBoxLayout()
            dl.setContentsMargins(0, 0, 0, 0)
            dl.addStretch()
            dl.addWidget(del_btn)
            layout.addLayout(dl)

        self.toggle = SwitchButton()
        self.toggle.setOnText("")
        self.toggle.setOffText("")
        self.toggle.setChecked(checked)
        self.toggle.checkedChanged.connect(self._on_toggle)

        self.name_label = QLabel(site_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.url_label = QLabel(site_key)
        self.url_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.toggle, 0, Qt.AlignCenter)
        layout.addWidget(self.name_label)
        layout.addWidget(self.url_label)
        self.setLayout(layout)

    def _on_toggle(self, checked):
        pass

    def is_checked(self):
        return self.toggle.isChecked()

    def set_checked(self, checked):
        self.toggle.setChecked(checked)


class MainWindow(QMainWindow):

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.game_cards = {}
        self.video_cards = {}
        self.custom_game_cards = {}
        self.custom_video_cards = {}
        self._init_ui()
        self._load_config_state()

    def _init_ui(self):
        self.setWindowTitle("pokilocker")
        self.setMinimumSize(750, 560)
        self.resize(820, 640)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(14)

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel("pokilocker")
        title.setFont(QFont("Segoe UI Variable", 22, QFont.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()

        btn1 = PushButton("+ 自定义游戏")
        btn1.clicked.connect(lambda: self._add_custom("games"))
        title_layout.addWidget(btn1)

        btn2 = PushButton("+ 自定义视频")
        btn2.clicked.connect(lambda: self._add_custom("videos"))
        title_layout.addWidget(btn2)

        main_layout.addLayout(title_layout)

        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.addTab(
            self._create_site_tab("games", GAME_SITES, self.game_cards, self.custom_game_cards),
            "游戏网站")
        self.tab_widget.addTab(
            self._create_site_tab("videos", VIDEO_SITES, self.video_cards, self.custom_video_cards),
            "视频网站")
        main_layout.addWidget(self.tab_widget)

        # 底部
        bottom_layout = QHBoxLayout()
        self.admin_label = QLabel()
        self._update_admin_label()
        bottom_layout.addWidget(self.admin_label)
        bottom_layout.addStretch()

        self.apply_btn = PrimaryPushButton("应用规则")
        self.apply_btn.clicked.connect(self._apply_rules)
        bottom_layout.addWidget(self.apply_btn)

        self.clear_btn = PushButton("清除所有规则")
        self.clear_btn.clicked.connect(self._clear_rules)
        bottom_layout.addWidget(self.clear_btn)

        main_layout.addLayout(bottom_layout)

        # 菜单栏
        menubar = self.menuBar()
        menu = menubar.addMenu("菜单")
        a = QAction("设置...", self)
        a.triggered.connect(self._open_settings)
        menu.addAction(a)
        a2 = QAction("关于", self)
        a2.triggered.connect(self._open_about)
        menu.addAction(a2)

        central.setLayout(main_layout)

        if not self.config.get("stealth_mode", False):
            self._setup_tray()
        else:
            self.tray_icon = None

    def _on_tab_changed(self, idx):
        pass

    def _create_site_tab(self, category, presets, card_dict, custom_dict):
        w = QWidget()
        outer = QVBoxLayout()
        outer.setContentsMargins(8, 12, 8, 12)
        outer.setSpacing(10)

        # 总开关
        header = QHBoxLayout()
        master_label = QLabel("全部启用/禁用")
        master_label.setFont(QFont("Segoe UI Variable", 11, QFont.Bold))
        master = SwitchButton()
        master.setOnText("")
        master.setOffText("")
        if category == "games":
            master.checkedChanged.connect(self._on_master_game_toggle)
        else:
            master.checkedChanged.connect(self._on_master_video_toggle)
        header.addWidget(master_label)
        header.addWidget(master)
        header.addStretch()
        count = len(presets)
        header.addWidget(QLabel(f"共 {count} 个"))
        outer.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        outer.addWidget(line)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        sc = QWidget()
        gl = QGridLayout()
        gl.setSpacing(8)
        gl.setContentsMargins(4, 8, 4, 8)
        gl.setColumnStretch(0, 1)
        gl.setColumnStretch(1, 1)
        gl.setColumnStretch(2, 1)
        gl.setColumnStretch(3, 1)

        items = list(presets.items())
        for i, (key, name) in enumerate(items):
            card = SiteCard(key, name)
            card_dict[key] = card
            gl.addWidget(card, i // COLS, i % COLS)

        ci = len(items)
        for key, name in custom_dict.items():
            card = SiteCard(key, name, is_custom=True,
                           on_delete=self._make_delete_handler(category, key))
            card_dict[key] = card
            gl.addWidget(card, ci // COLS, ci % COLS)
            ci += 1

        sc.setLayout(gl)
        scroll.setWidget(sc)
        outer.addWidget(scroll)
        w.setLayout(outer)
        return w

    def _rebuild_custom_tab(self, category):
        if category == "games":
            card_dict = self.custom_game_cards
            presets = GAME_SITES
            master_toggle = self._on_master_game_toggle
        else:
            card_dict = self.custom_video_cards
            presets = VIDEO_SITES
            master_toggle = self._on_master_video_toggle

        idx = 0 if category == "games" else 1
        content = self._create_site_tab(category, presets,
                                         self.game_cards if category == "games" else self.video_cards,
                                         card_dict)
        self.tab_widget.removeTab(idx)
        self.tab_widget.insertTab(idx, content,
                                  "游戏网站" if category == "games" else "视频网站")
        self.tab_widget.setCurrentIndex(idx)

    def _add_custom(self, category):
        name, ok1 = QInputDialog.getText(self, "添加自定义网站",
                                         "请输入网站名称（如：B站）")
        if not ok1 or not name.strip():
            return
        domain, ok2 = QInputDialog.getText(self, "添加自定义网站",
                                           "请输入域名（如：bilibili.com）")
        if not ok2 or not domain.strip():
            return
        domain = domain.strip().lower()
        name = name.strip()
        if category == "games":
            self.config.add_custom_game(domain, name)
            self.custom_game_cards = {k: v for k, v in
                                      self.config.get_custom_games().items()}
        else:
            self.config.add_custom_video(domain, name)
            self.custom_video_cards = {k: v for k, v in
                                       self.config.get_custom_videos().items()}
        self._rebuild_custom_tab(category)

    def _make_delete_handler(self, category, domain):
        return lambda d: self._delete_custom(category, d)

    def _delete_custom(self, category, domain):
        if category == "games":
            self.config.remove_custom_game(domain)
            self.custom_game_cards.pop(domain, None)
            self.game_cards.pop(domain, None)
        else:
            self.config.remove_custom_video(domain)
            self.custom_video_cards.pop(domain, None)
            self.video_cards.pop(domain, None)
        self._rebuild_custom_tab(category)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(
            self.style().SP_ComputerIcon))
        self.tray_icon.setToolTip("pokilocker")
        m = QMenu()
        m.addAction("显示", self.show_and_raise)
        m.addSeparator()
        m.addAction("退出", self._quit_app)
        self.tray_icon.setContextMenu(m)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_raise()

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if self.config.get("stealth_mode", False):
            self._quit_app()
        else:
            event.ignore()
            self.hide()
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "pokilocker", "已最小化到托盘",
                    QSystemTrayIcon.Information, 2000)

    def _quit_app(self):
        if self.tray_icon:
            self.tray_icon.hide()
        sys.exit(0)

    def _update_admin_label(self):
        self.admin_label.setText(
            "管理员模式" if is_admin() else "非管理员模式")

    def _on_master_game_toggle(self, checked):
        for r in self.game_cards.values():
            r.set_checked(checked)

    def _on_master_video_toggle(self, checked):
        for r in self.video_cards.values():
            r.set_checked(checked)

    def _load_config_state(self):
        for k, r in self.game_cards.items():
            r.set_checked(self.config.is_game_blocked(k))
        for k, r in self.video_cards.items():
            r.set_checked(self.config.is_video_blocked(k))
        self.custom_game_cards = {}
        for k, v in self.config.get_custom_games().items():
            self.custom_game_cards[k] = v
            self.game_cards[k] = SiteCard(k, v, self.config.is_game_blocked(k),
                                          is_custom=True,
                                          on_delete=self._make_delete_handler("games", k))
        self.custom_video_cards = {}
        for k, v in self.config.get_custom_videos().items():
            self.custom_video_cards[k] = v
            self.video_cards[k] = SiteCard(k, v, self.config.is_video_blocked(k),
                                           is_custom=True,
                                           on_delete=self._make_delete_handler("videos", k))

    def _sync_config_from_ui(self):
        for k in list(self.game_cards.keys()):
            self.config.set_game_block(k, self.game_cards[k].is_checked())
        for k in list(self.video_cards.keys()):
            self.config.set_video_block(k, self.video_cards[k].is_checked())
        self.config.set("enable_game_block",
                        any(r.is_checked() for r in self.game_cards.values()))
        self.config.set("enable_video_block",
                        any(r.is_checked() for r in self.video_cards.values()))

    def _apply_rules(self):
        self._sync_config_from_ui()
        self.config.save()
        if not is_admin():
            w = MessageBox("权限不足",
                           "修改 hosts 文件需要管理员权限。\n请右键以管理员身份运行。", self)
            w.cancelButton.hide()
            w.exec()
            return
        success, msg = apply_blocking(self.config)
        w = MessageBox("成功" if success else "失败", msg, self)
        w.cancelButton.hide()
        w.exec()

    def _clear_rules(self):
        w = MessageBox("确认清除",
                       "确定要清除所有网站阻断规则吗？", self)
        if not w.exec():
            return
        if not is_admin():
            w = MessageBox("权限不足", "需要管理员权限才能修改 hosts 文件。", self)
            w.cancelButton.hide()
            w.exec()
            return
        success, msg = clear_all_blocking()
        if success:
            for r in self.game_cards.values():
                r.set_checked(False)
            for r in self.video_cards.values():
                r.set_checked(False)
            self._sync_config_from_ui()
            self.config.save()
        w = MessageBox("成功" if success else "失败", msg, self)
        w.cancelButton.hide()
        w.exec()

    def _open_settings(self):
        d = SettingsDialog(self.config, self)
        d.exec_()

    def _open_about(self):
        d = AboutDialog(self)
        d.exec_()

    def apply_on_startup(self):
        if is_admin():
            self._sync_config_from_ui()
            self.config.save()
            apply_blocking(self.config)

    def show_startup_notification(self):
        if self.tray_icon:
            self.tray_icon.showMessage(
                "pokilocker", "已在后台运行。",
                QSystemTrayIcon.Information, 3000)
