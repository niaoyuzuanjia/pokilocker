# PokiLocker

为了防止同学使用班级电脑玩poki小游戏，故开发此项目，这是一个网站访问管理工具，通过修改系统 hosts 禁用文件实现游戏和视频网站的访问。

## 功能

- **禁用游戏网站**：预置 16 个热门游戏网站，支持一键启用/禁用
- **禁用视频网站**：预置 12 个视频网站，支持一键启用/禁用
- **自定义网站**：添加/删除自定义网站域名进行阻断
- **网格布局**：每行 4 个站点卡片，界面清晰
- **隐秘模式**：不显示托盘图标，关闭即退出
- **开机自启动**：支持设置开机自动运行

## 技术栈

- Python 3.11
- PyQt5
- qfluentwidgets

## 使用

1. 右键以**管理员身份**运行
2. 在主界面选择需要禁用的网站
3. 点击「应用规则」生效

## 注意

- 修改 hosts 文件需要管理员权限
- 配置文件保存在 `Documents/PokiLocker/`

## 打包

```bash
python pokilocker/build_exe.py
```
##软件界面
<img width="1027" height="839" alt="image" src="https://github.com/user-attachments/assets/727ffc98-6e54-41ae-a6bc-d4d58372723c" />
主界面
<img width="1027" height="839" alt="image" src="https://github.com/user-attachments/assets/4c072010-5484-4740-9fe1-d25787d9fd54" />
对话框
<img width="602" height="489" alt="image" src="https://github.com/user-attachments/assets/95338b5c-9259-461c-8cf7-9810dfb0f693" />
设置


