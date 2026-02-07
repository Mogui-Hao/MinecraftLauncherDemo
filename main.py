import json
import os
import sys
import tempfile
from threading import Thread

import requests
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, setTheme, Theme, FluentIcon as FIF, NavigationItemPosition

from config import *
from gui import *


class MainWindow(FluentWindow):
    updateRelease = Signal(list)
    updateSnapshot = Signal(list)
    # updateAncient = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinecraftLauncherDemo")
        self.resize(1000, 600)

        self.releaseVersion = []    # 正式版
        self.snapshotVersion = []   # 预览版
        self.ancientVersion = []    # 远古版
        self.aprFoolVersion = []    # 愚人节版

        self.cfg = Config()

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
            with open(tempfile.gettempdir() + "/MinecraftLauncherDemo/version_manifest.json") as f:
                version = json.load(f)
        except:
            version = requests.get(self.cfg.versionsOrigin.value.value).json()
            os.mkdir(tempfile.gettempdir() + "/MinecraftLauncherDemo")
            with open(tempfile.gettempdir() + "/MinecraftLauncherDemo/version_manifest.json", "w", encoding="utf-8") as f:
                json.dump(self.version, f)
        finally:
            if not version: return
            for v in version["versions"]:
                if v["type"] == "snapshot":
                    # i = v["id"]
                    # if not ("-pre" in i or "-snapshot" in i or "-rc" in i or re.match(r'^\d{2}w\d{2}[a-z]$', i)) or "-04-01" in v["releaseTime"]:
                    #     self.aprFoolVersion.append(v)
                    #     continue
                    self.snapshotVersion.append(v)
                elif v["type"] == "release":
                    # if v["id"][0] in "abcr":
                    #     self.ancientVersion.append(v)
                    #     continue
                    self.releaseVersion.append(v)
            self.updateRelease.emit(self.releaseVersion)
            self.updateSnapshot.emit(self.snapshotVersion)
            # self.updateAncient.emit(self.ancientVersion)

    def initFolder(self):
        os.makedirs(os.path.join(os.getcwd(), ".minecraft"), exist_ok=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    # 创建主窗口
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
