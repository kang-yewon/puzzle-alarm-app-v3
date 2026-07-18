"""
Audio playback abstraction layer using Kivy's SoundLoader or Android Background Service.
"""

import threading
import os
import time
from kivy.core.audio import SoundLoader
from kivy.utils import platform

_playing = False
_sound = None
_loop_thread = None
_stop_event = threading.Event()
_current_sound_path = ""


def get_ringing_flag_path() -> str:
    from kivy.app import App
    app = App.get_running_app()
    if app and app.user_data_dir:
        return os.path.join(app.user_data_dir, ".ringing")
    # fallback
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        if service:
            return os.path.join(service.getApplicationContext().getFilesDir().getAbsolutePath(), "app", ".ringing")
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), ".ringing")


def create_ringing_flag():
    try:
        path = get_ringing_flag_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("ringing")
    except Exception as e:
        print(f"Failed to create ringing flag: {e}")


def delete_ringing_flag():
    try:
        path = get_ringing_flag_path()
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Failed to delete ringing flag: {e}")


def start_alarm_service():
    if platform == 'android':
        try:
            from jnius import autoclass
            from android import mActivity
            context = mActivity.getApplicationContext()
            service_class = autoclass('org.kangyewon.puzzlealarm.ServiceAlarm')
            intent = autoclass('android.content.Intent')(context, service_class)
            
            # Put extras for foreground service notification
            intent.putExtra('smallIcon', context.getApplicationInfo().icon)
            intent.putExtra('contentTitle', 'Puzzle Alarm')
            intent.putExtra('contentText', 'Background alarm monitor is running')
            
            # Use startForegroundService on Android 8.0+
            Build = autoclass('android.os.Build$VERSION')
            if Build.SDK_INT >= 26:
                context.startForegroundService(intent)
            else:
                context.startService(intent)
            print("Foreground AlarmService started successfully.")
        except Exception as e:
            print(f"Failed to start Foreground AlarmService: {e}")


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

    # On Android, the background service plays sound and handles volume
    if platform == 'android':
        create_ringing_flag()
        return

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
    
    if platform == 'android':
        delete_ringing_flag()
        _playing = False
        return

    if _sound:
        try:
            _sound.stop()
        except Exception:
            pass
    else:
        _stop_event.set()
    _playing = False


def resume_alarm() -> None:
    global _playing, _sound, _loop_thread, _stop_event, _current_sound_path
    if not _playing:
        play_alarm(_current_sound_path)
        return

    if platform == 'android':
        create_ringing_flag()
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
    
    if platform == 'android':
        delete_ringing_flag()
        return

    _stop_event.set()
    if _sound:
        try:
            _sound.stop()
            _sound.unload()
        except Exception:
            pass
        _sound = None
    _loop_thread = None
