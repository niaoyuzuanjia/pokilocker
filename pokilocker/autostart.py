"""
Windows 开机自启动管理
通过注册表 HKCU\Software\Microsoft\Windows\CurrentVersion\Run 实现
"""
import sys
import os
import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "PokiLocker"


def get_exe_path():
    """获取当前运行的可执行文件或脚本路径"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    return sys.executable


def get_start_command():
    """获取开机启动的完整命令行"""
    exe = get_exe_path()
    script = os.path.abspath(sys.argv[0]) if not getattr(sys, 'frozen', False) else ""
    if script and script.endswith(".py"):
        return f'"{exe}" "{script}"'
    return f'"{exe}"'


def is_auto_start_enabled():
    """检查是否已设置开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def enable_auto_start():
    """启用开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        cmd = get_start_command()
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False


def disable_auto_start():
    """禁用开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False
