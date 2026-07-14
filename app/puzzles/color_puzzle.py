"""
Color distinction puzzle: find the one slightly-different tile in a grid.
"""

import random
import colorsys
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Line

from .base_puzzle import BasePuzzle, COLORS, FONT_NAME


_BASE_HUES = [
    (0.92, "핑크"),
    (0.60, "파랑"),
    (0.33, "초록"),
    (0.08, "주황"),
    (0.70, "보라"),
    (0.50, "하늘"),
    (0.00, "빨강"),
    (0.14, "노랑"),
]

_GRID_COLS = 4
_GRID_ROWS = 4


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[float, float, float, float]:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return (r, g, b, 1.0)


def _generate_puzzle():
    hue, name = random.choice(_BASE_HUES)
    sat = random.uniform(0.50, 0.70)
    val = random.uniform(0.78, 0.90)

    mode = random.choice(["hue", "val", "sat"])
    if mode == "hue":
        delta = random.choice([-1, 1]) * random.uniform(0.007, 0.014)
        odd_color = _hsv_to_rgb(hue + delta, sat, val)
    elif mode == "val":
        delta = random.choice([-1, 1]) * random.uniform(0.025, 0.045)
        odd_color = _hsv_to_rgb(hue, sat, val + delta)
    else:
        delta = random.choice([-1, 1]) * random.uniform(0.04, 0.08)
        odd_color = _hsv_to_rgb(hue, sat + delta, val)

    base_color = _hsv_to_rgb(hue, sat, val)
    odd_row = random.randint(0, _GRID_ROWS - 1)
    odd_col = random.randint(0, _GRID_COLS - 1)
    return base_color, odd_color, odd_row, odd_col, name


class ColorPuzzle(BasePuzzle):
    def _build_ui(self) -> None:
        self._base_color, self._odd_color, self._odd_row, self._odd_col, name = _generate_puzzle()
        self._answered = False

        self.padding = [20, 10, 20, 10]
        self.spacing = 10

        desc = Label(
            text="다른 색 하나를 찾아 터치하세요.",
            font_name=FONT_NAME,
            font_size='16sp',
            bold=True,
            color=COLORS["text"],
            size_hint_y=None,
            height='40dp'
        )
        self.add_widget(desc)

        # 4x4 Grid of Buttons
        self._grid = GridLayout(cols=_GRID_COLS, spacing=5, size_hint=(1, 0.7))
        self._buttons = []

        for r in range(_GRID_ROWS):
            row_btns = []
            for col in range(_GRID_COLS):
                is_odd = (r == self._odd_row and col == self._odd_col)
                color = self._odd_color if is_odd else self._base_color
                
                # We need to capture r and col using default arguments in lambda
                btn = Button(
                    background_normal='',
                    background_color=color,
                )
                btn.bind(on_release=lambda instance, row=r, c=col: self._on_tile_click(row, c, instance))
                self._grid.add_widget(btn)
                row_btns.append(btn)
            self._buttons.append(row_btns)

        self.add_widget(self._grid)

        self._feedback = Label(
            text="",
            font_name=FONT_NAME,
            font_size='12sp',
            color=COLORS["error"],
            size_hint_y=None,
            height='30dp'
        )
        self.add_widget(self._feedback)

    def _on_tile_click(self, row: int, col: int, button: Button) -> None:
        if self._answered:
            return
        self.notify_activity()

        if row == self._odd_row and col == self._odd_col:
            self._answered = True
            
            # Highlight correct button with a white outline
            with button.canvas.after:
                Color(1, 1, 1, 1)
                Line(rectangle=(button.x + 2, button.y + 2, button.width - 4, button.height - 4), width=2)
                
            self._feedback.text = "정답!"
            self._feedback.color = COLORS["success"]
            Clock.schedule_once(lambda dt: self.on_success(), 0.5)
        else:
            self._feedback.text = "틀렸어요. 다시 찾아보세요."
            self._feedback.color = COLORS["error"]
            self._record_wrong()
