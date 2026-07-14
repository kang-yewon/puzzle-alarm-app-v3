"""
Alarm ringing screen: shown when alarm fires.
"""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line

from .base_screen import BaseScreen, hex_to_kivy, PRIMARY, TEXT, TEXT_SEC, FONT_NAME

BTN_PUZZLE = hex_to_kivy("#FF6B9D")
BTN_PUZZLE_DARK = hex_to_kivy("#E85A89")


class ClockWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 160)
        self.step = 0
        self.bind(pos=self.draw, size=self.draw)

    def set_step(self, step):
        self.step = step
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        
        shake = 4 * math.sin(self.step * 0.5)
        cx = self.x + self.width / 2 + shake
        cy = self.y + self.height / 2
        r = 48

        bg_pink = hex_to_kivy("#FFB8DC")
        border_pink = hex_to_kivy("#FF6BAD")
        dark_pink = hex_to_kivy("#FF9CC8")
        text_color = hex_to_kivy("#2D2D2D")
        primary_color = hex_to_kivy("#B96EFF")

        with self.canvas:
            # Bell bumps (behind body)
            Color(*dark_pink)
            Ellipse(pos=(cx - 40 - 6, cy + 32 - 6), size=(12, 12))
            Ellipse(pos=(cx + 28 - 6, cy + 32 - 6), size=(12, 12))

            # Legs
            Ellipse(pos=(cx - 36 - 6, cy - 44 - 6), size=(12, 12))
            Ellipse(pos=(cx + 24 - 6, cy - 44 - 6), size=(12, 12))

            # Body
            Color(*border_pink)
            Ellipse(pos=(cx - r, cy - r), size=(2*r, 2*r))
            Color(*bg_pink)
            Ellipse(pos=(cx - r + 3, cy - r + 3), size=(2*r - 6, 2*r - 6))

            # Hour hand
            Color(*text_color)
            angle_h = math.radians(-60 + shake * 2)
            Line(points=[cx, cy, cx + 22 * math.sin(angle_h), cy + 22 * math.cos(angle_h)], width=3, cap="round")

            # Minute hand
            Color(*primary_color)
            angle_m = math.radians(90 + self.step * 6)
            Line(points=[cx, cy, cx + 30 * math.sin(angle_m), cy + 30 * math.cos(angle_m)], width=2, cap="round")

            # Center dot
            Color(*text_color)
            Ellipse(pos=(cx - 4, cy - 4), size=(8, 8))

            # Wave lines
            w_alpha = abs(math.sin(self.step * 0.3))
            wave_color = (185/255.0 * w_alpha, 110/255.0 * w_alpha, 1.0 * w_alpha, 1.0)
            Color(*wave_color)
            # Line(ellipse=(x, y, w, h, start_angle, end_angle)) in degrees
            Line(ellipse=(cx - 66, cy + 10, 20, 20, 135, 225), width=2)
            Line(ellipse=(cx + 46, cy + 10, 20, 20, -45, 45), width=2)


class AlarmRingingScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._anim_event = None
        self._anim_step = 0
        self._build_ui()

    def _build_ui(self) -> None:
        layout = BoxLayout(orientation='vertical', padding=[30, 40, 30, 40], spacing=15)

        layout.add_widget(BoxLayout(size_hint_y=0.1))

        # Animated clock widget
        self._clock_widget = ClockWidget()
        self._clock_widget.pos_hint = {'center_x': 0.5}
        layout.add_widget(self._clock_widget)

        title = Label(
            text="알람입니다!",
            font_name=FONT_NAME,
            font_size='24sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height='40dp',
            halign='center'
        )
        layout.add_widget(title)

        subtitle = Label(
            text="일어나서 퍼즐을 풀어 알람을 해제하세요.",
            font_name=FONT_NAME,
            font_size='13sp',
            color=TEXT_SEC,
            halign='center',
            valign='middle',
            text_size=(280, None)
        )
        layout.add_widget(subtitle)

        layout.add_widget(BoxLayout(size_hint_y=0.2))

        # Solve puzzle button
        puzzle_btn = Button(
            text="퍼즐 풀기",
            font_name=FONT_NAME,
            font_size='18sp',
            bold=True,
            background_normal='',
            background_color=BTN_PUZZLE,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height='60dp'
        )
        puzzle_btn.bind(on_release=lambda instance: self._go_to_puzzle())
        layout.add_widget(puzzle_btn)

        layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.add_widget(layout)

    def on_show(self) -> None:
        self._start_animation()

    def _go_to_puzzle(self) -> None:
        self._stop_animation()
        self.controller.show_screen("puzzle")

    def _start_animation(self) -> None:
        self._anim_step = 0
        self._stop_animation()
        self._anim_event = Clock.schedule_interval(self._animate, 0.08)

    def _stop_animation(self) -> None:
        if self._anim_event:
            Clock.unschedule(self._anim_event)
            self._anim_event = None

    def _animate(self, dt) -> None:
        self._anim_step += 1
        self._clock_widget.set_step(self._anim_step)
