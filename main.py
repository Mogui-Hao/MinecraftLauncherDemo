import json
import os
import sys
from threading import Thread

import requests
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, FluentIcon as FIF, NavigationItemPosition, setTheme, Theme

from config import cfg
from gui import *


class MainWindow(FluentWindow):
    updateRelease = Signal(list)
    updateSnapshot = Signal(list)
    updateOld = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinecraftLauncherDemo")
        self.resize(1000, 600)

        self.releaseVersion = []    # 正式版
        self.snapshotVersion = []   # 预览版
        self.oldVersion = []    # 远古版
        self.aprFoolVersion = []    # 愚人节版

        Thread(target=self.initVersion).start()
        self.initNavigation()
        self.initFolder()

    def initNavigation(self):
        self.addSubInterface(
            HomePage(self),
            FIF.HOME,
            "主页"
        )

        self.addSubInterface(
            DownloadPage(self),
            FIF.DOWNLOAD,
            "下载"
        )

        self.addSubInterface(
            SettingPage(self),
            FIF.SETTING,
            "设置",
            NavigationItemPosition.BOTTOM
        )

    def initVersion(self):
        version = {}
        try:
            with open(f"{cfg.tempPath.value}/MinecraftLauncherDemo/version_manifest.json") as f:
                version = json.load(f)
        except Exception as e:
            version = requests.get(cfg.versionsOrigin.value.value.Versions / "mc/game/version_manifest.json").json()
            os.makedirs(f"{cfg.tempPath.value}/MinecraftLauncherDemo", exist_ok=True)
            with open(f"{cfg.tempPath.value}/MinecraftLauncherDemo/version_manifest.json", "w", encoding="utf-8") as f:
                json.dump(version, f)
        finally:
            if not version: return
            for v in version["versions"]:
                if v["type"] == "release":
                    self.releaseVersion.append(v)
                elif v["type"] == "old_beta" or v["type"] == "old_alpha":
                    self.oldVersion.append(v)
                else:
                    self.snapshotVersion.append(v)
            self.updateRelease.emit(self.releaseVersion)
            self.updateSnapshot.emit(self.snapshotVersion)
            # self.updateAncient.emit(self.ancientVersion)

    def initFolder(self):
        os.makedirs(cfg.minecraftPath.value, exist_ok=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cfg.load("./config/config.json")
    print(cfg.versionsOrigin.value.value)
    setTheme(Theme.AUTO, save=False)
    # 创建主窗口
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
