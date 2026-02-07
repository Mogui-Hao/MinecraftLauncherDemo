import os
import time
from pathlib import Path
from threading import Thread

import requests
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QHBoxLayout
from qfluentwidgets import (SingleDirectionScrollArea, FluentIcon as FIF,
                            Pivot, ToolButton, LineEdit, ProgressBar, BodyLabel)

from .component.card import Card
from .logic import fileSha1


class BaseVersionPage(QWidget):
    def __init__(self, parent=None, _type: str = "release"):
        super().__init__(parent=parent)
        self.setObjectName(_type.capitalize() + "VersionPage")
        self._type = _type
        self._count = 0
        _p = self.parent().parent()
        self.d = self.parent().downloadVersion
        self._v = getattr(_p, f"{self._type[0].lower()}{self._type[1:]}Version")
        getattr(_p, f"update{_type.capitalize()}").connect(self.updateData)     # 更想数据时重新绘制
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        self.scrollArea = SingleDirectionScrollArea()
        self.scrollArea.verticalScrollBar().valueChanged.connect(lambda value: self.on_scroll(value))
        self.scrollArea.setStyleSheet("background-color: rgba(255, 255, 255, 0)")

        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)

        self.refresh_content()

        self.scrollArea.setWidget(self.contentWidget)
        self.scrollArea.setWidgetResizable(True)
        mainLayout.addWidget(self.scrollArea)
        self.setLayout(mainLayout)

    def on_scroll(self, value):
        """滚动事件处理"""
        # 判断是否滚动到底部（留20%缓冲区域）
        scroll_height = self.scrollArea.verticalScrollBar().maximum()
        if value > scroll_height * 0.9 and len(self._v) - self._count:
            for _ in self._v[self._count:self._count+5]:
                self._count += 1
                card = Card(FIF.GAME, _["id"], _["releaseTime"].replace("-", "/").replace("T", " ").replace("+00:00", ""), _["url"], self.d)
                self.contentLayout.addWidget(card)

    def updateData(self, data):
        self._v = data
        self.refresh_content()

    def refresh_content(self):
        """根据数据状态重新渲染内容"""
        while self.contentLayout.count() > 0:
            item = self.contentLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not self._v:
            # 显示占位卡片
            placeholder = Card(FIF.GAME, "0", "1999/12/31 23:59")
            self.contentLayout.addWidget(placeholder)
        else:
            # 渲染前15条数据
            for item in self._v[:15]:
                self._count += 1
                card = Card(
                    FIF.GAME,
                    item["id"],
                    item["releaseTime"].replace("-", "/").replace("T", " ").replace("+00:00", ""),
                    item["url"],
                    self.d
                )
                self.contentLayout.addWidget(card)

class DownloadInfoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DownloadInfoPage")

        self.initUI()

    def initUI(self):
        self.mainLayout = QVBoxLayout()

        # 文件下载进度
        self.downloadFileLayout = QVBoxLayout()
        # 文字
        self.downloadFileTextLayout = QHBoxLayout()
        self.downloadFileInfoText = BodyLabel(f"下载进度")
        self.downloadFilePercentText = BodyLabel(f"版本文件下载(1/4)")
        self.downloadFileTextLayout.addWidget(self.downloadFileInfoText)
        self.downloadFileTextLayout.addStretch()
        self.downloadFileTextLayout.addWidget(self.downloadFilePercentText)
        # 进度条
        self.downloadFileBar = ProgressBar()
        self.downloadFileBar.setRange(0, 384)
        self.downloadFileBar.setValue(180)
        self.downloadFileLayout.addLayout(self.downloadFileTextLayout)
        self.downloadFileLayout.addWidget(self.downloadFileBar)

        # 文件总数
        self.totalFileLayout = QVBoxLayout()
        # 文字
        self.totalFileTextLayout = QHBoxLayout()
        self.totalFileInfoText = BodyLabel(f"文件总数")
        self.totalFilePercentText = BodyLabel(f"{180/384*100:.2f}% (180/384)")
        self.totalFileTextLayout.addWidget(self.totalFileInfoText)
        self.totalFileTextLayout.addStretch()
        self.totalFileTextLayout.addWidget(self.totalFilePercentText)
        # 进度条
        totalFileBar = ProgressBar()
        totalFileBar.setRange(0, 384)
        totalFileBar.setValue(180)
        self.totalFileLayout.addLayout(self.totalFileTextLayout)
        self.totalFileLayout.addWidget(totalFileBar)

        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.downloadFileLayout)
        self.mainLayout.addLayout(self.totalFileLayout)

        self.setLayout(self.mainLayout)

class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DownloadPage")

        self.initUI()

    def initUI(self):
        self.mainPivot = Pivot()

        self.stackedWidget = QStackedWidget(self)
        self.downloadInfoPage = DownloadInfoPage(self)

        self.addSubInterface(BaseVersionPage(self, "release"), "正式版")
        self.addSubInterface(BaseVersionPage(self, "snapshot"), "预览版")
        # self.addSubInterface(BaseVersionPage(self, "ancient"), "远古版")
        # self.addSubInterface(BaseVersionPage(self, "aprFool"), "愚人节版")

        mainLayout = QVBoxLayout()
        headLayout = QHBoxLayout()

        downloadInfoButton = ToolButton(FIF.DOWNLOAD)
        downloadInfoButton.clicked.connect(lambda: {self.stackedWidget.setCurrentWidget(self.downloadInfoPage), setattr(self.mainPivot, "_currentRouteKey", None), self.mainPivot.repaint()})

        searchEdit = LineEdit()
        searchEdit.setPlaceholderText("搜索版本...")
        searchEdit.setClearButtonEnabled(True)
        searchEdit.setFocusPolicy(Qt.StrongFocus)

        self.stackedWidget.addWidget(self.downloadInfoPage)
        self.mainPivot._currentRouteKey = "ReleaseVersionPage"
        headLayout.addStretch(2)
        headLayout.addWidget(self.mainPivot, 0, Qt.AlignHCenter)
        headLayout.addStretch(1)
        headLayout.addWidget(downloadInfoButton)
        headLayout.addWidget(searchEdit)
        headLayout.addSpacing(10)

        mainLayout.addLayout(headLayout)
        mainLayout.addWidget(self.stackedWidget)

        self.setLayout(mainLayout)

    def addSubInterface(self, widget: QWidget, text: str):
        self.stackedWidget.addWidget(widget)
        self.mainPivot.addItem(
            routeKey=widget.objectName(),
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def downloadVersion(self, ver, url: str):
        baseDir = Path(os.getcwd()) / ".minecraft"
        versionDir = baseDir / "versions" / ver
        assetsDir = baseDir / "assets"
        librariesDir = baseDir / "libraries"

        versionDir.mkdir(parents=True, exist_ok=True)
        assetsDir.mkdir(parents=True, exist_ok=True)
        librariesDir.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录结构: {ver}")

    def downloadFile(self, url: str, path: Path, sha1: str = None):
        headResp = None

        if path.exists():
            if sha1 and fileSha1(path) == sha1: return True
            try:
                headResp = requests.head(url, timeout=10) if headResp is None else headResp
                if headResp.status_code == 200:
                    remote_size = int(headResp.headers.get('Content-Length', 0))
                    if path.stat().st_size == remote_size:
                        return True
            except Exception:
                ...

        for attempt in range(3):  # 三次重试
            try:
                headResp = requests.head(url, timeout=10) if headResp is None else headResp
                if headResp.status_code != 200: raise Exception
                with requests.get(url, stream=True, timeout=10) as resp: ...
            except Exception:
                ...

