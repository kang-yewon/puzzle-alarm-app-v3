"""
Puzzle Alarm App — entry point.
"""

import os
import sys

# Configure window size before loading Kivy core
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase

from app.app_controller import AppController

# Safely register Korean font globally
font_registered = False
for font_path in [
    "C:/Windows/Fonts/malgun.ttf",
    "C:\\Windows\\Fonts\\malgun.ttf",
    "/system/fonts/DroidSansFallback.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
]:
    if os.path.exists(font_path):
        try:
            LabelBase.register(name='NanumGothic', fn_regular=font_path)
            font_registered = True
            break
        except Exception:
            pass

if not font_registered:
    # Use default Roboto font mapping if no Korean font is found
    import kivy
    default_kivy_font = os.path.join(os.path.dirname(kivy.__file__), 'data', 'fonts', 'Roboto-Regular.ttf')
    if os.path.exists(default_kivy_font):
        try:
            LabelBase.register(name='NanumGothic', fn_regular=default_kivy_font)
        except Exception:
            pass


class PuzzleAlarmApp(App):
    def build(self):
        self.title = "퍼즐 알람"
        controller = AppController()
        
        # Handle debug mode
        if "--debug" in sys.argv:
            Clock.schedule_once(lambda dt: controller.debug_trigger_alarm(), 1.0)
            
        return controller.screen_manager


if __name__ == "__main__":
    PuzzleAlarmApp().run()
