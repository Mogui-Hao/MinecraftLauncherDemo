import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Thread

import requests
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QHBoxLayout, QLabel, QSizePolicy
from qfluentwidgets import (SingleDirectionScrollArea, FluentIcon as FIF,
                            Pivot, ToolButton, LineEdit, ProgressBar, BodyLabel)

from config import cfg, Url
from .component.card import Card
from .logic import fileSha1


class BaseVersionPage(QWidget):
    def __init__(self, parent=None, _type: str = "release"):
        super().__init__(parent=parent)
        self.setObjectName(_type.capitalize() + "VersionPage")
        self._type = _type
        self._count = 0
        _p = self.parent().parent()
        _d = self.parent().downloadVersion
        self.d = lambda url, ver: Thread(target=_d, args=(url, ver)).start()
        self._v = getattr(_p, f"{self._type[0].lower()}{self._type[1:]}Version")
        getattr(_p, f"update{_type.capitalize()}").connect(self.updateData)     # 更想数据时重新绘制
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        self.scrollArea = SingleDirectionScrollArea()
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.on_scroll)
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
    totalFile = Signal(int)
    addFile = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DownloadInfoPage")
        self.file = 0
        self.totalFile.connect(self._totalFile)
        self.addFile.connect(self._addFile)

        self.initUI()

    def _addFile(self):
        self.file += 1
        total = self.totalFileBar.maximum()
        self.totalFilePercentText.setText(f"{self.file/total*100:.2f}% ({self.file}/{total})")
        self.totalFileBar.setValue(self.file)

    def _totalFile(self, total: int):
        self.totalFilePercentText.setText(f"{self.file/max(1, total)*100:.2f}% ({self.file}/{max(1, total)})")
        self.totalFileBar.setRange(0, total)
        self.totalFileBar.setValue(0)

    def initUI(self):
        self.mainLayout = QVBoxLayout()

        # 下载信息
        self.scrollArea = SingleDirectionScrollArea()
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.scrollArea.setStyleSheet("background-color: transparent")
        self.scrollArea.setWidgetResizable(True)
        self.contentLayout.addStretch()
        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

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
        self.downloadFileBar.setValue(0)
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
        self.totalFileBar = ProgressBar()
        self.totalFileBar.setRange(0, 384)
        self.totalFileBar.setValue(0)
        self.totalFileLayout.addLayout(self.totalFileTextLayout)
        self.totalFileLayout.addWidget(self.totalFileBar)

        # self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.downloadFileLayout)
        self.mainLayout.addLayout(self.totalFileLayout)

        self.setLayout(self.mainLayout)

class DownloadPage(QWidget):
    addInfoToDownload = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DownloadPage")
        self.addInfoToDownload.connect(self._addInfoToDownload)

        self.initUI()

    def initUI(self):
        self.mainPivot = Pivot()

        self.stackedWidget = QStackedWidget(self)
        self.downloadInfoPage = DownloadInfoPage(self)
        # self.downloadInfoPage.contentLayout.addWidget(BodyLabel("AAA"))

        self.addSubInterface(BaseVersionPage(self, "release"), "正式版")
        self.addSubInterface(BaseVersionPage(self, "snapshot"), "预览版")
        self.addSubInterface(BaseVersionPage(self, "old"), "远古版")
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
        baseDir = Path(cfg.minecraftPath.value)
        versionDir = baseDir / "versions" / ver
        assetsDir = baseDir / "assets"
        librariesDir = baseDir / "libraries"

        self.addInfoToDownload.emit(f"📁 创建目录结构: {ver}")
        versionDir.mkdir(parents=True, exist_ok=True)
        assetsDir.mkdir(parents=True, exist_ok=True)
        librariesDir.mkdir(parents=True, exist_ok=True)

        self.addInfoToDownload.emit(f"⬇️ 下载版本JSON文件: {url}")
        self.downloadInfoPage.totalFile.emit(1)
        self.downloadFile(url, versionDir / f"{ver}.json", url.split("/")[-2])
        with open(versionDir / f"{ver}.json", "r", encoding="utf-8") as f:
            verData = json.load(f)
        self.downloadInfoPage.addFile.emit()

        _client = verData['downloads']['client']
        self.downloadInfoPage.totalFile.emit(1)
        self.addInfoToDownload.emit(f"⬇️ 下载客户端JAR: {ver}.jar")
        self.downloadFile(_client["url"], versionDir / f"{ver}.jar", _client["sha1"])
        self.downloadInfoPage.addFile.emit()

        assetIndex = verData["assetIndex"]
        assetIndexPath = assetsDir / "indexes" / f"{assetIndex['id']}.json"
        assetIndexPath.parent.mkdir(parents=True, exist_ok=True)
        self.downloadInfoPage.totalFile.emit(1)
        self.addInfoToDownload.emit(f"⬇️ 下载资源索引: {assetIndex['url']}")
        self.downloadFile(assetIndex['url'], assetIndexPath, assetIndex["sha1"])
        self.downloadInfoPage.addFile.emit()

        self.addInfoToDownload.emit(f"⬇️ 开始下载资源文件")
        with open(assetIndexPath, "r", encoding="utf-8") as f:
            assetIndexData: dict = json.load(f)["objects"]
        self.downloadInfoPage.totalFile.emit(len(assetIndexData))

        with ThreadPoolExecutor(max_workers=cfg.downloadTask.value) as executor:
            futures = []
            for _, data in assetIndexData.items():
                path = Path(data["hash"][:2]) / data["hash"]
                futures.append(executor.submit(
                    self.downloadFile,
                    cfg.versionsOrigin.value.value.Assets / path,
                    assetsDir / "objects" / path,
                    data["hash"],
                    False
                ))

            for future in as_completed(futures):
                if not future.result()[0]:
                    self.addInfoToDownload.emit(f"❌ 下载文件 {future.result()[1]} 时发生错误")
                self.downloadInfoPage.addFile.emit()

        self.addInfoToDownload.emit(f"✅ 资源文件下载完成")


    def downloadFile(self, url: Url, path: Path, sha1: str = None, su: bool = True):
        headResp = None
        url = Url(url)
        if isinstance(path, str): path = Path(path)

        if path.exists():
            if sha1 and fileSha1(path) == sha1:
                if su: self.addInfoToDownload.emit(f"   ✓ 下载完成: {path.name}")
                return True, path.name
            try:
                headResp = requests.head(url, timeout=cfg.downloadTimeout.value) if headResp is None else headResp
                if headResp.status_code == 200:
                    remote_size = int(headResp.headers.get('Content-Length', 0))
                    if path.stat().st_size == remote_size:
                        if su: self.addInfoToDownload.emit(f"   ✓ 下载完成: {path.name}")
                        return True, path.name
            except Exception: ...
        path.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(cfg.downloadCount.value):  # 重试
            try:
                headResp = requests.head(url, timeout=cfg.downloadTimeout.value) if headResp is None else headResp
                if headResp.status_code != 200: raise ValueError("网络错误")
                with requests.get(url, stream=True, timeout=cfg.downloadTimeout.value) as resp:
                    resp.raise_for_status()
                    with open(path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=26_2144):    # 512KB (8192 * 32)
                            if chunk: f.write(chunk)
                if sha1:
                    if sha1 != fileSha1(path): raise ValueError("SHA1 值不匹配")
                if su: self.addInfoToDownload.emit(f"   ✓ 下载完成: {path.name}")
                return True, path.name
            except Exception as e:
                print(e)
        return False, path.name

    def _addInfoToDownload(self, info: str, label: QLabel = BodyLabel):
        self.downloadInfoPage.contentLayout.insertWidget(self.downloadInfoPage.contentLayout.count() - 1, label(info))
        print(info)
