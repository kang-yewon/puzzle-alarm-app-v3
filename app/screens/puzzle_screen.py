"""
Puzzle screen: sequences N puzzles, manages the 15-second idle timer,
pauses alarm while on screen, resumes alarm if idle timer expires.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from .base_screen import BaseScreen, hex_to_kivy, PRIMARY, TEXT, TEXT_SEC, SURFACE, FONT_NAME
from ..models import PuzzleType
from ..puzzles.math_puzzle import MathPuzzle
from ..puzzles.color_puzzle import ColorPuzzle
from ..puzzles.typing_puzzle import TypingPuzzle

WARNING = hex_to_kivy("#FF9800")
PROGRESS_BG = hex_to_kivy("#E8D5FF")
IDLE_SECONDS = 15


class ProgressBarWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '6dp'
        self.progress = 0.0
        self.bind(pos=self.draw, size=self.draw)

    def set_progress(self, progress):
        self.progress = progress
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # BG
            Color(*PROGRESS_BG)
            Rectangle(pos=self.pos, size=self.size)
            # Fill
            if self.progress > 0:
                Color(*PRIMARY)
                Rectangle(pos=self.pos, size=(self.width * self.progress, self.height))


class PuzzleScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._current_puzzle_widget = None
        self._idle_event = None
        self._puzzle_index = 0
        self._total = 1
        self._alarm_ringing = False
        self._remaining = IDLE_SECONDS
        self._build_ui()

    def _build_ui(self) -> None:
        layout = BoxLayout(orientation='vertical')

        # Header Row
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='45dp',
            padding=[0, 10, 0, 10]
        )
        with header.canvas.before:
            Color(*SURFACE)
            self._header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(
            pos=lambda inst, val: setattr(self._header_bg, 'pos', val),
            size=lambda inst, val: setattr(self._header_bg, 'size', val)
        )

        self._progress_lbl = Label(
            text="Puzzle 1 / 1",
            font_name=FONT_NAME,
            font_size='14sp',
            bold=True,
            color=TEXT,
            halign='center',
            valign='middle'
        )
        self._progress_lbl.bind(size=lambda s, w: setattr(self._progress_lbl, 'text_size', w))
        header.add_widget(self._progress_lbl)
        layout.add_widget(header)

        # Progress bar
        self._progress_bar = ProgressBarWidget()
        layout.add_widget(self._progress_bar)

        # Puzzle Container
        self._puzzle_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        layout.add_widget(self._puzzle_container)

        # Idle timer label
        self._timer_lbl = Label(
            text=f"Alarm will ring again if idle for {IDLE_SECONDS}s.",
            font_name=FONT_NAME,
            font_size='11sp',
            color=TEXT_SEC,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height='45dp',
            text_size=(300, None)
        )
        layout.add_widget(self._timer_lbl)

        self.add_widget(layout)

    def on_show(self) -> None:
        from .. import audio_manager
        audio_manager.pause_alarm()
        self._puzzle_index = 0
        self._total = self.controller.settings.puzzle_count
        self._alarm_ringing = False
        self._load_puzzle()
        self._reset_idle_timer()
        Window.bind(on_key_down=self._on_window_key_down)

    def on_leave(self) -> None:
        self._cancel_idle_timer()
        Window.unbind(on_key_down=self._on_window_key_down)

    def _load_puzzle(self) -> None:
        if self._current_puzzle_widget:
            self._puzzle_container.remove_widget(self._current_puzzle_widget)
            self._current_puzzle_widget = None

        self._progress_lbl.text = f"Puzzle {self._puzzle_index + 1} / {self._total}"
        self._progress_bar.set_progress(self._puzzle_index / self._total)

        puzzle_type = self.controller.settings.puzzle_type
        klass = {
            PuzzleType.MATH: MathPuzzle,
            PuzzleType.COLOR: ColorPuzzle,
            PuzzleType.TYPING: TypingPuzzle,
        }[puzzle_type]

        widget = klass(
            on_success=self._on_puzzle_solved,
            on_max_fails=self._on_max_fails,
            controller=self.controller
        )
        self._puzzle_container.add_widget(widget)
        self._current_puzzle_widget = widget

    def _on_puzzle_solved(self) -> None:
        self._silence_alarm()
        self._reset_idle_timer()
        self._puzzle_index += 1
        if self._puzzle_index >= self._total:
            self._finish()
        else:
            self._load_puzzle()

    def _on_max_fails(self) -> None:
        # Reset back to puzzle index 0
        Clock.schedule_once(lambda dt: self._do_max_fails_reset(), 0)

    def _do_max_fails_reset(self) -> None:
        self._silence_alarm()
        self._cancel_idle_timer()
        self._puzzle_index = 0
        self._load_puzzle()
        self._reset_idle_timer()
        if self._timer_lbl:
            self._timer_lbl.text = "3 wrong answers! Restarting from the first puzzle."
            self._timer_lbl.color = WARNING

    def _finish(self) -> None:
        self._cancel_idle_timer()
        from .. import audio_manager
        audio_manager.stop_alarm()
        self.controller.show_screen("complete")

    # Inactivity / Touch Hooks
    def on_touch_down(self, touch):
        self._on_activity()
        return super().on_touch_down(touch)

    def _on_window_key_down(self, window, key, *args):
        self._on_activity()

    def _on_activity(self) -> None:
        self._silence_alarm()
        self._reset_idle_timer()
        if self._current_puzzle_widget:
            self._current_puzzle_widget.notify_activity()

    def _reset_idle_timer(self) -> None:
        self._cancel_idle_timer()
        self._remaining = IDLE_SECONDS
        self._tick_idle()

    def _cancel_idle_timer(self) -> None:
        if self._idle_event:
            Clock.unschedule(self._idle_event)
            self._idle_event = None

    def _tick_idle(self, dt=None) -> None:
        if self._remaining <= 5:
            self._timer_lbl.text = f"Alarm will ring again in {self._remaining}s!"
            self._timer_lbl.color = WARNING
        else:
            self._timer_lbl.text = f"Alarm will ring again if idle for {self._remaining}s."
            self._timer_lbl.color = TEXT_SEC

        if self._remaining <= 0:
            self._on_idle_timeout()
            return
        
        self._remaining -= 1
        self._idle_event = Clock.schedule_once(self._tick_idle, 1.0)

    def _on_idle_timeout(self) -> None:
        from .. import audio_manager
        audio_manager.resume_alarm()
        self._alarm_ringing = True
        self._timer_lbl.text = "Alarm is ringing! Solve puzzles to turn it off."
        self._timer_lbl.color = WARNING

    def _silence_alarm(self) -> None:
        if not self._alarm_ringing:
            return
        from .. import audio_manager
        audio_manager.pause_alarm()
        self._alarm_ringing = False
