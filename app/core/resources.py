import sys
from pathlib import Path


def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base, *parts))
    root = Path(__file__).resolve().parents[2]
    return str(root.joinpath(*parts))


def asset_path(name):
    return resource_path("app", "assets", name)


def icon_path():
    for name in ("icon.png", "icon.svg", "icon.ico"):
        path = Path(asset_path(name))
        if path.exists():
            return str(path)
    return asset_path("icon.png")
