from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "app_config.json")


def resolve_path(path_value: str) -> str:
    if os.path.isabs(path_value):
        return path_value
    return os.path.normpath(os.path.join(PROJECT_ROOT, path_value))


@lru_cache(maxsize=1)
def load_project_config(path: str | None = None) -> Dict[str, Any]:
    config_path = path or os.environ.get("APP_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def reload_project_config() -> None:
    load_project_config.cache_clear()


def get_project_config() -> Dict[str, Any]:
    return load_project_config()


def get_window_config() -> Dict[str, int]:
    cfg = get_project_config().get("window", {})
    return {
        "width": int(cfg.get("width", 1100)),
        "height": int(cfg.get("height", 620)),
        "show_width": int(cfg.get("show_width", 600)),
        "show_height": int(cfg.get("show_height", 480)),
    }


def get_detection_config() -> Dict[str, Any]:
    cfg = get_project_config().get("detection", {})
    return {
        "model_path": str(cfg.get("model_path", "yolov8n.pt")),
        "task": str(cfg.get("task", "detect")),
        "conf": float(cfg.get("conf", 0.25)),
        "iou": float(cfg.get("iou", 0.7)),
        "device": str(cfg.get("device", "auto")),
        "warmup_shape": cfg.get("warmup_shape", [48, 48, 3]),
    }


def get_db_config() -> Dict[str, Any]:
    return get_project_config().get("database", {})


def get_db_engine() -> str:
    return str(get_db_config().get("engine", "sqlite")).strip().lower()


def get_sqlite_path() -> str:
    sqlite_path = str(get_db_config().get("sqlite_path", "./data/app.db"))
    return resolve_path(sqlite_path)


def get_mysql_config() -> Dict[str, Any]:
    mysql_cfg = get_db_config().get("mysql", {})
    return {
        "host": mysql_cfg.get("host", "127.0.0.1"),
        "port": int(mysql_cfg.get("port", 3306)),
        "user": mysql_cfg.get("user", "root"),
        "password": mysql_cfg.get("password", ""),
        "database": mysql_cfg.get("database", "yolo_app"),
        "charset": mysql_cfg.get("charset", "utf8mb4"),
        "autocommit": False,
    }


def get_class_names(lang: str = "zh") -> List[str]:
    cfg = get_project_config()
    if lang.lower() == "en":
        return list(cfg.get("class_names_en", []))
    return list(cfg.get("class_names_zh", []))


def get_class_name(idx: int, lang: str = "zh") -> str:
    names = get_class_names(lang=lang)
    if 0 <= idx < len(names):
        return str(names[idx])
    return f"class_{idx}"


def init_database() -> str | None:
    from . import database

    return database.init_database()
