"""
AppController: owns the main window, all screens, alarm manager, and navigation.
Acts as the application's single source of truth.
"""

from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from typing import Literal

from .models import AlarmSettings
from . import storage, audio_manager
from .alarm_manager import AlarmManager

ScreenName = Literal["home", "settings", "ringing", "puzzle", "complete", "sound"]

WINDOW_W = 360
WINDOW_H = 720


class AppController:
    def __init__(self) -> None:
        self._setup_window()
        self.settings: AlarmSettings = storage.load_settings()
        self._build_screens()
        self._alarm_manager = AlarmManager(on_alarm_trigger=self._on_alarm_trigger)
        self._alarm_manager.start(self.settings)
        
        # Synchronize native Android AlarmManager precise wakeup schedule on app launch
        from kivy.utils import platform
        if platform == 'android':
            try:
                import os
                from .audio_manager import get_ringing_flag_path, schedule_android_alarm, cancel_android_alarm
                
                # Check if alarm is currently supposed to be ringing (.ringing flag exists)
                if os.path.exists(get_ringing_flag_path()):
                    self.show_screen("ringing")
                    return
                    
                # Otherwise, ensure exact alarm is scheduled
                if self.settings.enabled:
                    schedule_android_alarm(self.settings.hour, self.settings.minute, self.settings.is_am)
                else:
                    cancel_android_alarm()
            except Exception as e:
                print(f"Android startup alarm sync error: {e}")
                
        self.show_screen("home")

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        Window.title = "Puzzle Alarm"
        from kivy.utils import platform
        if platform != 'android':
            Window.size = (WINDOW_W, WINDOW_H)
        else:
            # Set window flags on Android to turn screen on and show over lockscreen
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                if activity:
                    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                    window = activity.getWindow()
                    window.addFlags(
                        WindowManager.FLAG_SHOW_WHEN_LOCKED |
                        WindowManager.FLAG_TURN_SCREEN_ON |
                        WindowManager.FLAG_KEEP_SCREEN_ON |
                        WindowManager.FLAG_DISMISS_KEYGUARD
                    )
                    print("Android lockscreen overlay and wake flags added successfully.")
            except Exception as e:
                print(f"Failed to add Android window flags: {e}")
        Window.bind(on_request_close=self._on_close)

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _build_screens(self) -> None:
        from .screens.home_screen import HomeScreen
        from .screens.settings_screen import SettingsScreen
        from .screens.alarm_ringing_screen import AlarmRingingScreen
        from .screens.puzzle_screen import PuzzleScreen
        from .screens.complete_screen import CompleteScreen
        from .screens.sound_settings_screen import SoundSettingsScreen

        self.screen_manager = ScreenManager(transition=FadeTransition())

        self._screens: dict[ScreenName, object] = {
            "home": HomeScreen(name="home", controller=self),
            "settings": SettingsScreen(name="settings", controller=self),
            "ringing": AlarmRingingScreen(name="ringing", controller=self),
            "puzzle": PuzzleScreen(name="puzzle", controller=self),
            "complete": CompleteScreen(name="complete", controller=self),
            "sound": SoundSettingsScreen(name="sound", controller=self),
        }

        for screen in self._screens.values():
            self.screen_manager.add_widget(screen)

        self._current: ScreenName | None = None

    def show_screen(self, name: ScreenName) -> None:
        self.screen_manager.current = name
        screen = self._screens[name]
        screen.on_show()
        self._current = name

    # ------------------------------------------------------------------
    # Alarm events (called from background thread via Clock)
    # ------------------------------------------------------------------

    def _on_alarm_trigger(self) -> None:
        # Schedule on Kivy's main thread loop
        Clock.schedule_once(lambda dt: self._alarm_fire(), 0)

    def _alarm_fire(self) -> None:
        audio_manager.play_alarm(self.settings.sound_path)
        self.show_screen("ringing")

    def on_puzzles_complete(self) -> None:
        audio_manager.stop_alarm()
        self.show_screen("home")

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------

    def save_settings(self) -> None:
        storage.save_settings(self.settings)
        self._alarm_manager.update_settings(self.settings)
        
        # Schedule or cancel native Android AlarmManager exact wakeup
        from kivy.utils import platform
        if platform == 'android':
            try:
                from .audio_manager import schedule_android_alarm, cancel_android_alarm
                if self.settings.enabled:
                    schedule_android_alarm(self.settings.hour, self.settings.minute, self.settings.is_am)
                else:
                    cancel_android_alarm()
            except Exception as e:
                print(f"Android save settings alarm sync error: {e}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _on_close(self, *args) -> bool:
        self._alarm_manager.stop()
        audio_manager.stop_alarm()
        # Return False to tell Kivy that it's okay to close the window
        return False

    # ------------------------------------------------------------------
    # Dev helper: trigger alarm immediately (for testing)
    # ------------------------------------------------------------------

    def debug_trigger_alarm(self) -> None:
        self._alarm_fire()
