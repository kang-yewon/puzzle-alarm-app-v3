"""
Persistent storage using JSON.
Abstracted so a mobile port can swap in SQLite or platform key-value store.
"""

import json
import os
from .models import AlarmSettings, PuzzleType


def get_settings_file_path() -> str:
    # Try resolving via android service context first (if running inside background service)
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        if service:
            context = service.getApplicationContext()
            files_dir = context.getFilesDir().getAbsolutePath()
            return os.path.join(files_dir, "app", ".puzzle_alarm_settings.json")
    except Exception:
        pass

    from kivy.app import App
    app = App.get_running_app()
    if app and app.user_data_dir:
        return os.path.join(app.user_data_dir, ".puzzle_alarm_settings.json")
    return os.path.join(os.path.expanduser("~"), ".puzzle_alarm_settings.json")


def save_settings(settings: AlarmSettings) -> None:
    data = {
        "hour": settings.hour,
        "minute": settings.minute,
        "is_am": settings.is_am,
        "enabled": settings.enabled,
        "puzzle_type": settings.puzzle_type.value,
        "puzzle_count": settings.puzzle_count,
        "sound_path": settings.sound_path,
    }
    with open(get_settings_file_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_settings() -> AlarmSettings:
    path = get_settings_file_path()
    if not os.path.exists(path):
        return AlarmSettings()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AlarmSettings(
            hour=data.get("hour", 7),
            minute=data.get("minute", 0),
            is_am=data.get("is_am", True),
            enabled=data.get("enabled", True),
            puzzle_type=PuzzleType(data.get("puzzle_type", "math")),
            puzzle_count=data.get("puzzle_count", 3),
            sound_path=data.get("sound_path", ""),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return AlarmSettings()
