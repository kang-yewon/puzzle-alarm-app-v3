"""
Base screen class — thin wrapper around kivy.uix.screenmanager.Screen.
"""

from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app_controller import AppController


def hex_to_kivy(h: str) -> tuple[float, float, float, float]:
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


# Theme Color Tokens (from Tkinter screen modules)
PRIMARY = hex_to_kivy("#B96EFF")
PRIMARY_DARK = hex_to_kivy("#9B4FE8")
TEXT = hex_to_kivy("#2D2D2D")
TEXT_SEC = hex_to_kivy("#888888")
SURFACE = hex_to_kivy("#FFFFFF")
BORDER = hex_to_kivy("#E8D5FF")
INPUT_BG = hex_to_kivy("#F8F0FF")
TOGGLE_ON = hex_to_kivy("#B96EFF")
TOGGLE_OFF = hex_to_kivy("#CCCCCC")

# Global Font name for English character rendering
FONT_NAME = 'Roboto'

BG_COLOR = hex_to_kivy("#FFF0F5")


class BaseScreen(Screen):
    def __init__(self, controller: "AppController", **kwargs) -> None:
        super().__init__(**kwargs)
        self.controller = controller

        # Apply standard LavenderBlush background color `#FFF0F5`
        with self.canvas.before:
            Color(*BG_COLOR)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def on_show(self) -> None:
        """Called every time this screen is navigated to. Override as needed."""
        pass
