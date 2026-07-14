"""
Audio playback abstraction layer using Kivy's SoundLoader.
"""

import threading
import os
import time
from kivy.core.audio import SoundLoader

_playing = False
_sound = None
_loop_thread = None
_stop_event = threading.Event()
_current_sound_path = ""


def _beep_loop(stop_event: threading.Event) -> None:
    import sys
    while not stop_event.is_set():
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(880, 400)
            else:
                print("\a", end="", flush=True)
        except Exception:
            pass
        stop_event.wait(0.8)


def play_alarm(sound_path: str = "") -> None:
    global _playing, _sound, _loop_thread, _stop_event, _current_sound_path
    if _playing:
        return
    _playing = True
    _stop_event.clear()
    _current_sound_path = sound_path

    # Try loading user-provided file using Kivy's SoundLoader
    if sound_path and os.path.isfile(sound_path):
        try:
            _sound = SoundLoader.load(sound_path)
            if _sound:
                _sound.loop = True
                _sound.play()
                return
        except Exception as e:
            print(f"Error loading Kivy sound: {e}")

    # Fallback beep loop
    _loop_thread = threading.Thread(target=_beep_loop, args=(_stop_event,), daemon=True)
    _loop_thread.start()


def pause_alarm() -> None:
    global _playing, _sound, _loop_thread, _stop_event
    if not _playing:
        return
    if _sound:
        try:
            _sound.stop()
        except Exception:
            pass
    else:
        _stop_event.set()


def resume_alarm() -> None:
    global _playing, _sound, _loop_thread, _stop_event, _current_sound_path
    if not _playing:
        play_alarm(_current_sound_path)
        return
    if _sound:
        try:
            _sound.play()
        except Exception:
            pass
    else:
        _stop_event.clear()
        _loop_thread = threading.Thread(target=_beep_loop, args=(_stop_event,), daemon=True)
        _loop_thread.start()


def stop_alarm() -> None:
    global _playing, _sound, _loop_thread, _stop_event
    _playing = False
    _stop_event.set()
    if _sound:
        try:
            _sound.stop()
            _sound.unload()
        except Exception:
            pass
        _sound = None
    _loop_thread = None
