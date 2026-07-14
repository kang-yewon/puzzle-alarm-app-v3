"""
Background alarm checker.
Runs in a daemon thread; fires a callback when the alarm time is reached.
Keep this logic UI-independent for mobile portability.
"""

import threading
import time
from datetime import datetime
from typing import Callable
from .models import AlarmSettings


class AlarmManager:
    def __init__(self, on_alarm_trigger: Callable[[], None]) -> None:
        self._callback = on_alarm_trigger
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._fired_minute: tuple[int, int, int] | None = None  # (hour24, minute, day) last fired
        self._settings: AlarmSettings | None = None

    def start(self, settings: AlarmSettings) -> None:
        self._settings = settings
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def update_settings(self, settings: AlarmSettings) -> None:
        self._settings = settings
        self._fired_minute = None  # allow re-fire if settings changed

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            settings = self._settings
            if settings and settings.enabled:
                now = datetime.now()
                alarm_h24 = settings.hour_24()
                if (
                    now.hour == alarm_h24
                    and now.minute == settings.minute
                    and self._fired_minute != (alarm_h24, settings.minute, now.day)
                ):
                    self._fired_minute = (alarm_h24, settings.minute, now.day)
                    self._callback()
            self._stop_event.wait(10)  # check every 10 seconds
