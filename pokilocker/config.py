"""
配置管理模块 - 负责配置文件的读写
"""
import os
import json
from pathlib import Path

DEFAULT_CONFIG_NAME = "pokilocker_config.json"


def get_default_config_dir():
    """获取默认配置文件目录（用户文档目录下的 pokilocker 文件夹）"""
    docs = os.path.join(os.path.expanduser("~"), "Documents", "PokiLocker")
    return docs


def get_default_config_path():
    """获取默认配置文件完整路径"""
    return os.path.join(get_default_config_dir(), DEFAULT_CONFIG_NAME)


DEFAULT_CONFIG = {
    "config_dir": get_default_config_dir(),
    "config_file": get_default_config_path(),
    "auto_start": False,
    "start_minimized": False,
    "stealth_mode": False,
    "blocked_games": {},
    "blocked_videos": {},
    "custom_games": {},
    "custom_videos": {},
    "enable_game_block": False,
    "enable_video_block": False,
}

# 预置网站列表
GAME_SITES = {
    "4399.com": "4399小游戏",
    "poki.com": "poki",
    "7k7k.com": "7K7K小游戏",
    "17173.com": "17173游戏门户",
    "3dmgame.com": "3DM游戏网",
    "gamersky.com": "游民星空",
    "store.steampowered.com": "Steam商店",
    "www.epicgames.com": "Epic Games",
    "play.163.com": "网易游戏",
    "qq.com/game": "腾讯游戏",
    "xiaoyouxi.com": "小游戏网",
    "y8.com": "Y8小游戏",
    "kongregate.com": "Kongregate",
    "miniclip.com": "Miniclip",
    "addictinggames.com": "Addicting Games",
    "armorgames.com": "Armor Games",
}

VIDEO_SITES = {
    "www.iqiyi.com": "爱奇艺",
    "v.qq.com": "腾讯视频",
    "www.youku.com": "优酷",
    "www.mgtv.com": "芒果TV",
    "tv.sohu.com": "搜狐视频",
    "www.douyin.com": "抖音",
    "www.kuaishou.com": "快手",
    "www.acfun.cn": "AcFun",
    "www.youtube.com": "YouTube",
    "www.netflix.com": "Netflix",
    "v.youku.com": "优酷视频",
    "www.twitch.tv": "Twitch",
}


class ConfigManager:
    """配置文件管理器"""

    def __init__(self, config_path=None):
        if config_path:
            self.config_path = config_path
            self.config_dir = os.path.dirname(config_path)
        else:
            self.config_path = get_default_config_path()
            self.config_dir = get_default_config_dir()

        self.data = dict(DEFAULT_CONFIG)
        self.data["config_dir"] = self.config_dir
        self.data["config_file"] = self.config_path
        # 初始化站点开关
        for site in GAME_SITES:
            self.data["blocked_games"][site] = False
        for site in VIDEO_SITES:
            self.data["blocked_videos"][site] = False

    def load(self):
        """从文件加载配置，文件不存在则创建默认配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # 合并配置（保证新字段存在）
                self._merge_config(loaded)
            except (json.JSONDecodeError, IOError):
                pass
        else:
            self.save()

    def _merge_config(self, loaded):
        """合并加载的配置，确保所有字段都存在"""
        for key in DEFAULT_CONFIG:
            if key in loaded:
                self.data[key] = loaded[key]
        # 确保站点字典键齐全
        for site in GAME_SITES:
            if site not in self.data["blocked_games"]:
                self.data["blocked_games"][site] = False
        for site in VIDEO_SITES:
            if site not in self.data["blocked_videos"]:
                self.data["blocked_videos"][site] = False
        # 确保自定义站点字典存在
        if "custom_games" not in self.data:
            self.data["custom_games"] = {}
        if "custom_videos" not in self.data:
            self.data["custom_videos"] = {}

    def save(self):
        """保存配置到文件"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def is_game_blocked(self, site):
        return self.data["blocked_games"].get(site, False)

    def is_video_blocked(self, site):
        return self.data["blocked_videos"].get(site, False)

    def set_game_block(self, site, blocked):
        self.data["blocked_games"][site] = blocked

    def set_video_block(self, site, blocked):
        self.data["blocked_videos"][site] = blocked

    def get_blocked_game_sites(self):
        """获取所有被禁用的游戏站点列表"""
        return [s for s, v in self.data["blocked_games"].items() if v]

    def get_blocked_video_sites(self):
        """获取所有被禁用的视频站点列表"""
        return [s for s, v in self.data["blocked_videos"].items() if v]

    def add_custom_game(self, domain, name):
        self.data["custom_games"][domain] = name

    def remove_custom_game(self, domain):
        self.data["custom_games"].pop(domain, None)
        self.data["blocked_games"].pop(domain, None)

    def add_custom_video(self, domain, name):
        self.data["custom_videos"][domain] = name

    def remove_custom_video(self, domain):
        self.data["custom_videos"].pop(domain, None)
        self.data["blocked_videos"].pop(domain, None)

    def get_custom_games(self):
        return dict(self.data["custom_games"])

    def get_custom_videos(self):
        return dict(self.data["custom_videos"])
