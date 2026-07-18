"""
Abstract base for all puzzle types.
Each puzzle is a self-contained Kivy BoxLayout.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from typing import Callable


def hex_to_kivy(h: str) -> tuple[float, float, float, float]:
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)

COLORS = {
    "bg": hex_to_kivy("#FFF0F5"),
    "primary": hex_to_kivy("#B96EFF"),
    "primary_dark": hex_to_kivy("#9B4FE8"),
    "surface": hex_to_kivy("#FFFFFF"),
    "text": hex_to_kivy("#2D2D2D"),
    "text_secondary": hex_to_kivy("#888888"),
    "input_bg": hex_to_kivy("#F8F0FF"),
    "border": hex_to_kivy("#E8D5FF"),
    "success": hex_to_kivy("#4CAF50"),
    "error": hex_to_kivy("#FF5252"),
    "timer_warning": hex_to_kivy("#FF9800"),
}

MAX_WRONG = 3

# Globally registered font name for English characters
FONT_NAME = 'Roboto'


class BasePuzzle(BoxLayout):
    """
    One puzzle instance. on_success is called when the user solves it.
    on_max_fails is called when the user answers wrong MAX_WRONG times.
    """

    def __init__(
        self,
        on_success: Callable[[], None],
        on_max_fails: Callable[[], None] | None = None,
        controller = None,
        **kwargs
    ) -> None:
        kwargs.setdefault('orientation', 'vertical')
        super().__init__(**kwargs)
        self.on_success = on_success
        self.on_max_fails = on_max_fails
        self.controller = controller
        self._wrong_count = 0
        self._max_fails_reached = False
        
        # Background color
        with self.canvas.before:
            Color(*COLORS["bg"])
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        self._build_ui()

    def _update_rect(self, instance, value):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _record_wrong(self) -> None:
        """Call from a subclass when the user submits a wrong answer."""
        if self._max_fails_reached:
            return
        self._wrong_count += 1
        if self._wrong_count >= MAX_WRONG:
            self._max_fails_reached = True
            if self.on_max_fails:
                self.on_max_fails()

    def _build_ui(self) -> None:
        """Render puzzle-specific widgets."""
        raise NotImplementedError


    def notify_activity(self) -> None:
        """Called by parent on any user interaction to reset idle timer."""
        # This will be overridden or called by the parent puzzle screen.
        pass
