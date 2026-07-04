"""
PokiLocker - Windows 10 网站访问管理工具

通过修改系统 hosts 文件实现游戏和视频网站的访问阻断。
需要管理员权限才能应用规则。

启动方式：python main.py
"""
import sys
import os

# 确保当前目录在搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pokilocker.app import main

if __name__ == "__main__":
    main()
