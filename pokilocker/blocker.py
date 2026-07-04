"""
Hosts 文件阻断器 - 通过修改 Windows hosts 文件实现网站锁定
需要管理员权限运行
"""
import os
import sys
import ctypes
import tempfile

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
MARKER_BEGIN = "# === PokiLocker Block Begin ==="
MARKER_END = "# === PokiLocker Block End ==="
REDIRECT_IP = "127.0.0.1"


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """以管理员权限重新运行程序"""
    if sys.argv:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    return True


def read_hosts():
    """读取 hosts 文件内容"""
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        return None


def write_hosts(content):
    """写入 hosts 文件（通过临时文件 + 替换方式解决权限问题）"""
    try:
        # 尝试直接写入
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except PermissionError:
        # 备选：写入临时文件，提示用户手动替换
        tmp = os.path.join(tempfile.gettempdir(), "hosts_pokilocker")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        return False


def get_pokilocker_block(content):
    """提取 PokiLocker 阻断区域的内容"""
    lines = content.splitlines()
    in_block = False
    block_lines = []
    for line in lines:
        if MARKER_BEGIN in line:
            in_block = True
            continue
        if MARKER_END in line:
            in_block = False
            continue
        if in_block:
            block_lines.append(line.strip())
    return block_lines


def remove_pokilocker_block(content):
    """从 hosts 内容中移除 PokiLocker 阻断区域"""
    lines = content.splitlines()
    result = []
    skip = False
    for line in lines:
        if MARKER_BEGIN in line:
            skip = True
            continue
        if MARKER_END in line:
            skip = False
            continue
        if not skip:
            result.append(line)
    return "\n".join(result)


def build_block_section(sites):
    """构建阻断区域内容"""
    lines = [MARKER_BEGIN]
    for site in sites:
        lines.append(f"{REDIRECT_IP} {site}")
        # 同时添加 www 前缀版本
        if not site.startswith("www."):
            lines.append(f"{REDIRECT_IP} www.{site}")
    lines.append(MARKER_END)
    return "\n".join(lines)


def apply_blocking(config_manager):
    """
    根据配置应用网站阻断
    返回: (success: bool, message: str)
    """
    if not is_admin():
        return False, "需要管理员权限才能修改 hosts 文件。\n请以管理员身份重新运行程序。"

    content = read_hosts()
    if content is None:
        return False, f"无法读取 hosts 文件: {HOSTS_PATH}\n请检查权限。"

    # 移除旧的阻断区域
    content = remove_pokilocker_block(content)

    # 收集需要阻断的站点
    all_blocked = []

    if config_manager.get("enable_game_block", False):
        all_blocked.extend(config_manager.get_blocked_game_sites())

    if config_manager.get("enable_video_block", False):
        all_blocked.extend(config_manager.get_blocked_video_sites())

    if all_blocked:
        block_section = build_block_section(all_blocked)
        content = content.rstrip("\n") + "\n\n" + block_section + "\n"

    success = write_hosts(content)
    if success:
        # 刷新 DNS 缓存
        os.system("ipconfig /flushdns > nul 2>&1")
        return True, f"已更新阻断规则，共阻断 {len(all_blocked)} 个站点。"
    else:
        return False, "写入 hosts 文件失败，请检查权限。"


def clear_all_blocking():
    """
    清除所有阻断规则
    返回: (success: bool, message: str)
    """
    if not is_admin():
        return False, "需要管理员权限。请以管理员身份重新运行。"

    content = read_hosts()
    if content is None:
        return False, f"无法读取 hosts 文件。"

    content = remove_pokilocker_block(content)

    success = write_hosts(content)
    if success:
        os.system("ipconfig /flushdns > nul 2>&1")
        return True, "已清除所有阻断规则。"
    return False, "写入 hosts 文件失败。"
