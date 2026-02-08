import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from qfluentwidgets import ConfigItem, QConfig, OptionsConfigItem, OptionsValidator, ConfigSerializer, EnumSerializer

class Url:
    def __init__(self, url: str | Path):
        if isinstance(url, str):
            self.url = url
        elif isinstance(url, Path):
            self.url = str(url)
        elif isinstance(url, Url):
            self.url = url.url
        else:
            raise TypeError

    def __str__(self):
        return self.url

    def __divmod__(self, other):
        return Url(self.url + f"/{other}")

    def __truediv__(self, other):
        return Url(self.url + f"/{other}")

    __repr__ = __str__

@dataclass(slots=True)
class UrlOrigin:
    Versions: Url
    Assets: Url
    Library: Url

class UrlOriginSerializer(ConfigSerializer):
    def __init__(self, enumClass):
        self.enumClass = enumClass

    def serialize(self, value: Enum):
        return value.name

    def deserialize(self, value):
        return self.enumClass[value]

class Config(QConfig):
    class VersionsOrigin(Enum):
        Official = UrlOrigin(
            Url("https://piston-meta.mojang.com"),
            Url("https://resources.download.minecraft.net"),
            Url("https://libraries.minecraft.net")
        )
        BmclApi = UrlOrigin(
            Url("https://bmclapi2.bangbang93.com"),
            Url("https://bmclapi2.bangbang93.com/assets"),
            Url("https://bmclapi2.bangbang93.com/maven")
        )

    tempPath = ConfigItem("Temp", "TempPath", tempfile.gettempdir(), restart=False)

    minecraftPath = ConfigItem("Minecraft", "MinecraftPath", os.path.join(os.getcwd(), ".minecraft"), restart=False)

    versionsOrigin = OptionsConfigItem(
        "Version", "VersionOrigin", VersionsOrigin.Official, OptionsValidator(VersionsOrigin), UrlOriginSerializer(VersionsOrigin)
    )
    # EnumSerializer

    downloadTimeout = ConfigItem("Download", "DownloadTimeout", 10, restart=False)
    downloadCount = ConfigItem("Download", "DownloadCount", 3, restart=False)
    downloadTask = ConfigItem("Download", "DownloadTask", 16, restart=False)

cfg = Config()
