import hashlib
from pathlib import Path

import requests


def downloadFileConcurrently(tasks: list, taskType: str):
    ...

def fileSha1(path: Path) -> str:
    """计算文件哈希值"""
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while ...:
            data = f.read(65536)    # 64 KB
            if not data: break
            sha1.update(data)
    return sha1.hexdigest()
