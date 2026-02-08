from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from qfluentwidgets import OptionsSettingCard, FluentIcon as FIF, PushSettingCard, ComboBoxSettingCard, \
    SettingCardGroup, SettingCard, FluentIconBase, SpinBox, ConfigItem, SingleDirectionScrollArea

from config import cfg


class SpinBoxSettingCard(SettingCard):
    def __init__(self, configItem: ConfigItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, range=(0, 10), default=3, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.spinBox = SpinBox()
        self.spinBox.setRange(*range)
        self.hBoxLayout.addWidget(self.spinBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.spinBox.setValue(default)

        self.spinBox.valueChanged.connect(self.setValue)

    def setValue(self, value):
        if not isinstance(value, int): return
        self.spinBox.setValue(value)
        cfg.set(self.configItem, value)

class PathSettingCard(PushSettingCard):
    def __init__(self, configItem: ConfigItem, text, icon: Union[str, QIcon, FluentIconBase], title, url, parent=None):
        super().__init__(text, icon, title, url, parent)
        self.configItem = configItem

        self.clicked.connect(self.click)

    def click(self):
        self.setValue(QFileDialog.getExistingDirectory(
            self,
            "选择目录",
            "",
            QFileDialog.ShowDirsOnly  # 仅显示目录
        ))

    def setValue(self, value: str):
        if not isinstance(value, str): return
        self.contentLabel.setText(value)
        cfg.set(self.configItem, value)


class SettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingPage")

        self.initUI()

    def initUI(self):
        themeOptions = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用主题",
            texts=["浅色", "深色", "跟随系统设置"]
        )
        # themeOptions.optionChanged.connect(lambda v: setTheme(v))

        tempPath = PathSettingCard(
            cfg.tempPath,
            "选择文件夹",
            FIF.DOCUMENT,
            "缓存目录",
            cfg.tempPath.value
        )

        minecraftPath = PathSettingCard(
            cfg.minecraftPath,
            "选择文件夹",
            FIF.FOLDER,
            "Minecraft 目录",
            cfg.minecraftPath.value
        )

        originCombo = ComboBoxSettingCard(
            cfg.versionsOrigin,
            FIF.DOWNLOAD,
            "版本列表源",
            "修改源可能获取版本更快",
            ["官方源", "镜像源 (BMCLAPI)"]
        )

        downloadTimeout = SpinBoxSettingCard(
            cfg.downloadTimeout,
            FIF.DATE_TIME,
            "超时时间",
            "设置下载无响应多少秒超时",
            (1, 10),
            cfg.downloadTimeout.value
        )

        downloadCount = SpinBoxSettingCard(
            cfg.downloadCount,
            FIF.SYNC,
            "重复次数",
            "下载错误时, 最大重复次数",
            (0, 10),
            cfg.downloadCount.value
        )

        downloadTask = SpinBoxSettingCard(
            cfg.downloadTask,
            FIF.APPLICATION,
            "线程",
            "下载最大线程",
            (1, 128),
            cfg.downloadTask.value
        )

        individuation = SettingCardGroup("个性化")
        individuation.addSettingCard(themeOptions)
        individuation.setDisabled(True)
        individuation.setVisible(False)

        temp = SettingCardGroup("缓存")
        temp.addSettingCard(tempPath)

        game = SettingCardGroup("游戏")
        game.addSettingCard(minecraftPath)

        download = SettingCardGroup("下载")
        download.addSettingCard(originCombo)
        download.addSettingCard(downloadTimeout)
        download.addSettingCard(downloadCount)
        download.addSettingCard(downloadTask)

        scrollArea = SingleDirectionScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("background-color: transparent")
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)
        contentLayout.addWidget(individuation)
        contentLayout.addWidget(temp)
        contentLayout.addWidget(game)
        contentLayout.addWidget(download)
        contentLayout.addStretch(1)

        scrollArea.setWidget(contentWidget)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(scrollArea)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(mainLayout)

