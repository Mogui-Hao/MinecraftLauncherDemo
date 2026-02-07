import os
import tempfile
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import OptionsSettingCard, FluentIcon as FIF, PushSettingCard, ComboBoxSettingCard, \
    SettingCardGroup, SettingCard, FluentIconBase, SpinBox


class SpinBoxSettingCard(SettingCard):
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, range=(0, 10), default=3, parent=None):
        super().__init__(icon, title, content, parent)
        self.spinBox = SpinBox()
        self.spinBox.setRange(*range)
        self.hBoxLayout.addWidget(self.spinBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.spinBox.setValue(default)


class SettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingPage")

        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        cfg = self.parent().cfg
        themeOptions = OptionsSettingCard(
            cfg.themeMode,
            # qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用主题",
            texts=["浅色", "深色", "跟随系统设置"]
        )

        tempPush = PushSettingCard(
            text="选择文件夹",
            icon=FIF.DOWNLOAD,
            title="缓存目录",
            content=tempfile.gettempdir()
        )

        minecraftPush = PushSettingCard(
            text="选择文件夹",
            icon=FIF.FOLDER,
            title="Minecraft 目录",
            content=os.path.join(os.getcwd(), ".minecraft")
        )

        originCombo = ComboBoxSettingCard(
            configItem=cfg.versionsOrigin,
            icon=FIF.DOWNLOAD,
            title="版本列表源",
            texts=["官方源"]
        )

        downloadTimeout = SpinBoxSettingCard(
            icon=FIF.DATE_TIME,
            title="超时时间",
            content="设置下载无响应多少秒超时",
            range=(1, 10),
            default=10
        )

        downloadCount = SpinBoxSettingCard(
            icon=FIF.SYNC,
            title="重复次数",
            content="下载错误时, 最大重复次数",
            default=3
        )

        downloadTask = SpinBoxSettingCard(
            icon=FIF.SYNC,
            title="线程",
            content="下载最大线程",
            range=(1, 128),
            default=16
        )

        individuation = SettingCardGroup("个性化")
        individuation.addSettingCard(themeOptions)

        temp = SettingCardGroup("缓存")
        temp.addSettingCard(tempPush)

        game = SettingCardGroup("游戏")
        game.addSettingCard(minecraftPush)

        download = SettingCardGroup("下载")
        download.addSettingCard(originCombo)
        download.addSettingCard(downloadTimeout)
        download.addSettingCard(downloadCount)
        download.addSettingCard(downloadTask)

        mainLayout.addWidget(individuation)
        mainLayout.addWidget(temp)
        mainLayout.addWidget(game)
        mainLayout.addWidget(download)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
