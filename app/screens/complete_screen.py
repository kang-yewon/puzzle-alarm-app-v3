"""
Completion screen: shown for 3 seconds after all puzzles are solved.
"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse

from .base_screen import BaseScreen, hex_to_kivy, TEXT, TEXT_SEC, FONT_NAME

SUCCESS = hex_to_kivy("#4CAF50")
CONFETTI_COLORS = [
    hex_to_kivy("#B96EFF"),
    hex_to_kivy("#FF6B9D"),
    hex_to_kivy("#4CAF50"),
    hex_to_kivy("#FFB800"),
    hex_to_kivy("#42A5F5")
]


class ConfettiWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 100)
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            for _ in range(30):
                x = random.randint(10, 290)
                y = random.randint(5, 90)
                size = random.randint(4, 10)
                color = random.choice(CONFETTI_COLORS)
                Color(*color)
                Rectangle(pos=(self.x + x, self.y + y), size=(size, size / 2))


class CheckCircleWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 100)
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*SUCCESS)
            Ellipse(pos=self.pos, size=self.size)


class CompleteScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._countdown = 3
        self._timer = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = BoxLayout(orientation='vertical', padding=[30, 40, 30, 40], spacing=10)

        # Confetti
        self._confetti = ConfettiWidget()
        self._confetti.pos_hint = {'center_x': 0.5}
        layout.add_widget(self._confetti)

        # Check Circle & ✓ Mark
        check_container = BoxLayout(size_hint_y=None, height='100dp')
        check_container.add_widget(BoxLayout(size_hint_x=0.3)) # spacer
        
        check_bg = CheckCircleWidget()
        check_bg.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # We overlay the checkmark text label on top of the circle
        check_label = Label(
            text="✓",
            font_size='44sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='center',
            valign='middle'
        )
        check_label.bind(size=lambda s, w: setattr(check_label, 'text_size', w))

        # Relative layout/overlap using a custom widget position
        overlap = BoxLayout(size_hint_x=None, width='100dp')
        overlap.pos_hint = {'center_x': 0.5}
        # Add to canvas background and text on top
        overlap.add_widget(check_bg)
        
        check_container.add_widget(overlap)
        check_container.add_widget(BoxLayout(size_hint_x=0.3)) # spacer
        layout.add_widget(check_container)
        
        # We need to manually reposition check_label on top of check_bg
        check_bg.bind(pos=lambda inst, val: setattr(check_label, 'pos', val))
        self.add_widget(check_label)

        title = Label(
            text="Success!",
            font_name=FONT_NAME,
            font_size='32sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height='50dp',
            halign='center'
        )
        layout.add_widget(title)

        subtitle = Label(
            text="All puzzles solved successfully.",
            font_name=FONT_NAME,
            font_size='14sp',
            color=TEXT_SEC,
            size_hint_y=None,
            height='30dp',
            halign='center'
        )
        layout.add_widget(subtitle)

        layout.add_widget(BoxLayout(size_hint_y=0.2))

        self._counter_lbl = Label(
            text="Returning to home screen in 3 seconds.",
            font_name=FONT_NAME,
            font_size='11sp',
            color=TEXT_SEC,
            size_hint_y=None,
            height='30dp',
            halign='center'
        )
        layout.add_widget(self._counter_lbl)

        self.add_widget(layout)

    def on_show(self) -> None:
        self._countdown = 3
        self._confetti.draw()
        self._tick()

    def _tick(self, dt=None) -> None:
        if self._countdown > 0:
            self._counter_lbl.text = f"Returning to home screen in {self._countdown} seconds."
            self._countdown -= 1
            self._timer = Clock.schedule_once(self._tick, 1.0)
        else:
            self.controller.on_puzzles_complete()
