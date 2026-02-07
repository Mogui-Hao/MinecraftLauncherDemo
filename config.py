from enum import Enum

from qfluentwidgets import ConfigItem, QConfig, OptionsConfigItem, OptionsValidator, EnumSerializer, ConfigValidator


class IntegerConfigValidator(ConfigValidator):
    def __init__(self):
        ...

class IntegerConfigItem(ConfigItem):
    def __init__(self, group, name, default: int, restart=False):
        super().__init__(group, name, default, restart=restart)\

    def __str__(self):
        return f'{self.__class__.__name__}[value={self.value.name()}]'

class Config(QConfig):
    class VersionsOrigin(Enum):
        Official = "https://piston-meta.mojang.com/mc/game/version_manifest.json"

    versionsOrigin = OptionsConfigItem(
        "Version", "VersionOrigin", VersionsOrigin.Official, OptionsValidator(VersionsOrigin), EnumSerializer(VersionsOrigin)
    )

    downloadTimeout = ConfigItem("Download", "DownloadTimeout", 3, restart=False)

