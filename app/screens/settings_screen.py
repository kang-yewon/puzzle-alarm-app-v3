"""
Alarm settings screen: time picker, puzzle type, puzzle count, sound shortcut.
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line

from .base_screen import BaseScreen, PRIMARY, PRIMARY_DARK, TEXT, TEXT_SEC, SURFACE, BORDER, INPUT_BG, FONT_NAME
from ..models import PuzzleType


class ClickableRow(ButtonBehavior, BoxLayout):
    pass


class SettingsScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._hour = 7
        self._minute = 0
        self._is_am = True
        self._puzzle_type = PuzzleType.MATH
        self._puzzle_count = 3
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = BoxLayout(orientation='vertical')

        # --- Header ---
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            padding=[10, 5, 10, 5]
        )
        with header.canvas.before:
            Color(*SURFACE)
            self._header_bg = Rectangle(pos=header.pos, size=header.size)
            Color(*BORDER)
            self._header_border = Line(points=[header.x, header.y, header.x + header.width, header.y], width=1)

        header.bind(
            pos=lambda inst, val: (
                setattr(self._header_bg, 'pos', val),
                setattr(self._header_border, 'points', [header.x, header.y, header.x + header.width, header.y])
            ),
            size=lambda inst, val: (
                setattr(self._header_bg, 'size', val),
                setattr(self._header_border, 'points', [header.x, header.y, header.x + header.width, header.y])
            )
        )

        back_btn = Button(
            text="←",
            font_size='20sp',
            bold=True,
            background_normal='',
            background_color=SURFACE,
            color=TEXT,
            size_hint_x=None,
            width='50dp'
        )
        back_btn.bind(on_release=lambda instance: self._cancel())
        header.add_widget(back_btn)

        title_lbl = Label(
            text="Alarm Settings",
            font_name=FONT_NAME,
            font_size='16sp',
            bold=True,
            color=TEXT,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=lambda s, w: setattr(title_lbl, 'text_size', w))
        header.add_widget(title_lbl)

        save_btn = Button(
            text="Save",
            font_name=FONT_NAME,
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=SURFACE,
            color=PRIMARY,
            size_hint_x=None,
            width='60dp'
        )
        save_btn.bind(on_release=lambda instance: self._save())
        header.add_widget(save_btn)

        main_layout.add_widget(header)

        # --- Scrollable Body ---
        scroll = ScrollView(size_hint=(1, 1))
        body = BoxLayout(orientation='vertical', size_hint_y=None, padding=[16, 20, 16, 20], spacing=16)
        body.bind(minimum_height=body.setter('height'))

        # Time Section
        self._build_section_label(body, "Alarm Time")
        
        time_container = BoxLayout(
            orientation='horizontal',
            padding=[16, 16, 16, 16],
            spacing=10,
            size_hint_y=None,
            height='150dp'
        )
        with time_container.canvas.before:
            Color(*SURFACE)
            self._time_bg = Rectangle(pos=time_container.pos, size=time_container.size)
        time_container.bind(
            pos=lambda inst, val: setattr(self._time_bg, 'pos', val),
            size=lambda inst, val: setattr(self._time_bg, 'size', val)
        )

        # Hour Adjustment
        hour_layout = BoxLayout(orientation='vertical', spacing=2)
        up_h = Button(text="▲", font_size='14sp', color=TEXT, background_normal='', background_color=(0.9, 0.9, 0.92, 1))
        up_h.bind(on_release=lambda instance: self._adjust_hour(1))
        self._hour_lbl = Label(text="07", font_size='28sp', bold=True, color=TEXT)
        down_h = Button(text="▼", font_size='14sp', color=TEXT, background_normal='', background_color=(0.9, 0.9, 0.92, 1))
        down_h.bind(on_release=lambda instance: self._adjust_hour(-1))
        hour_layout.add_widget(up_h)
        hour_layout.add_widget(self._hour_lbl)
        hour_layout.add_widget(down_h)
        time_container.add_widget(hour_layout)

        colon_lbl = Label(text=":", font_size='28sp', bold=True, color=TEXT, size_hint_x=None, width='15dp')
        time_container.add_widget(colon_lbl)

        # Minute Adjustment
        minute_layout = BoxLayout(orientation='vertical', spacing=2)
        up_m = Button(text="▲", font_size='14sp', color=TEXT, background_normal='', background_color=(0.9, 0.9, 0.92, 1))
        up_m.bind(on_release=lambda instance: self._adjust_minute(1))
        self._minute_lbl = Label(text="00", font_size='28sp', bold=True, color=TEXT)
        down_m = Button(text="▼", font_size='14sp', color=TEXT, background_normal='', background_color=(0.9, 0.9, 0.92, 1))
        down_m.bind(on_release=lambda instance: self._adjust_minute(-1))
        minute_layout.add_widget(up_m)
        minute_layout.add_widget(self._minute_lbl)
        minute_layout.add_widget(down_m)
        time_container.add_widget(minute_layout)

        # AM/PM toggle
        self._am_pm_btn = Button(
            text="AM",
            font_size='22sp',
            bold=True,
            color=TEXT,
            background_normal='',
            background_color=(0.9, 0.9, 0.92, 1),
            size_hint_x=0.4
        )
        self._am_pm_btn.bind(on_release=lambda instance: self._toggle_am_pm())
        time_container.add_widget(self._am_pm_btn)

        body.add_widget(time_container)

        # Puzzle Type Section
        self._build_section_label(body, "Puzzle Type")

        puzzle_container = BoxLayout(
            orientation='vertical',
            padding=[8, 8, 8, 8],
            spacing=5,
            size_hint_y=None,
            height='180dp'
        )
        with puzzle_container.canvas.before:
            Color(*SURFACE)
            self._puzzle_bg = Rectangle(pos=puzzle_container.pos, size=puzzle_container.size)
        puzzle_container.bind(
            pos=lambda inst, val: setattr(self._puzzle_bg, 'pos', val),
            size=lambda inst, val: setattr(self._puzzle_bg, 'size', val)
        )

        puzzle_options = [
            (PuzzleType.MATH, "Math Puzzle", "Solve simple math problems"),
            (PuzzleType.COLOR, "Color Match", "Find the different colored tile"),
            (PuzzleType.TYPING, "Sentence Typing", "Type the exact sentence"),
        ]
        self._toggle_btns = {}
        for p_val, label, sub in puzzle_options:
            row = BoxLayout(orientation='horizontal', padding=[10, 5, 10, 5], spacing=10)
            
            # ToggleButton
            t_btn = ToggleButton(
                text=label,
                font_name=FONT_NAME,
                font_size='14sp',
                bold=True,
                group='puzzle_type',
                allow_no_selection=False,
                background_normal='',
                background_down='',
                background_color=(0.9, 0.9, 0.92, 1),
                color=TEXT,
                size_hint_x=0.4
            )
            # Custom bind to handle state visuals
            t_btn.bind(state=lambda instance, state, val=p_val: self._on_puzzle_select(val, state))
            self._toggle_btns[p_val] = t_btn
            row.add_widget(t_btn)

            sub_lbl = Label(
                text=sub,
                font_name=FONT_NAME,
                font_size='11sp',
                color=TEXT_SEC,
                halign='left',
                valign='middle'
            )
            sub_lbl.bind(size=lambda s, w: setattr(sub_lbl, 'text_size', w))
            row.add_widget(sub_lbl)
            puzzle_container.add_widget(row)

        body.add_widget(puzzle_container)

        # Puzzle Count Section
        self._build_section_label(body, "Puzzle Count")

        count_container = BoxLayout(
            orientation='horizontal',
            padding=[16, 14, 16, 14],
            spacing=15,
            size_hint_y=None,
            height='60dp'
        )
        with count_container.canvas.before:
            Color(*SURFACE)
            self._count_bg = Rectangle(pos=count_container.pos, size=count_container.size)
        count_container.bind(
            pos=lambda inst, val: setattr(self._count_bg, 'pos', val),
            size=lambda inst, val: setattr(self._count_bg, 'size', val)
        )

        minus_btn = Button(
            text="−",
            font_size='22sp',
            bold=True,
            background_normal='',
            background_color=SURFACE,
            color=PRIMARY,
            size_hint_x=None,
            width='50dp'
        )
        minus_btn.bind(on_release=lambda instance: self._change_count(-1))
        count_container.add_widget(minus_btn)

        self._count_lbl = Label(
            text="3",
            font_size='22sp',
            bold=True,
            color=TEXT
        )
        count_container.add_widget(self._count_lbl)

        suffix_lbl = Label(
            text="puzzles",
            font_name=FONT_NAME,
            font_size='13sp',
            color=TEXT_SEC,
            size_hint_x=None,
            width='50dp'
        )
        count_container.add_widget(suffix_lbl)

        plus_btn = Button(
            text="+",
            font_size='22sp',
            bold=True,
            background_normal='',
            background_color=SURFACE,
            color=PRIMARY,
            size_hint_x=None,
            width='50dp'
        )
        plus_btn.bind(on_release=lambda instance: self._change_count(1))
        count_container.add_widget(plus_btn)

        body.add_widget(count_container)

        # Sound Section
        self._build_section_label(body, "Alarm Sound")

        sound_row = ClickableRow(
            orientation='horizontal',
            padding=[16, 14, 16, 14],
            spacing=10,
            size_hint_y=None,
            height='50dp'
        )
        with sound_row.canvas.before:
            Color(*SURFACE)
            self._sound_bg = Rectangle(pos=sound_row.pos, size=sound_row.size)
        sound_row.bind(
            pos=lambda inst, val: setattr(self._sound_bg, 'pos', val),
            size=lambda inst, val: setattr(self._sound_bg, 'size', val),
            on_release=lambda instance: self.controller.show_screen("sound")
        )

        self._sound_lbl = Label(
            text="🔔 morning.mp3",
            font_name=FONT_NAME,
            font_size='13sp',
            color=TEXT,
            halign='left',
            valign='middle'
        )
        self._sound_lbl.bind(size=lambda s, w: setattr(self._sound_lbl, 'text_size', w))
        sound_row.add_widget(self._sound_lbl)
        
        arrow_lbl = Label(
            text=">",
            font_size='14sp',
            color=TEXT_SEC,
            size_hint_x=None,
            width='15dp'
        )
        sound_row.add_widget(arrow_lbl)

        body.add_widget(sound_row)

        scroll.add_widget(body)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def _build_section_label(self, parent, text) -> None:
        lbl = Label(
            text=text,
            font_name=FONT_NAME,
            font_size='12sp',
            bold=True,
            color=TEXT_SEC,
            size_hint_y=None,
            height='20dp',
            halign='left',
            valign='middle'
        )
        lbl.bind(size=lambda s, w: setattr(lbl, 'text_size', w))
        parent.add_widget(lbl)

    def _adjust_hour(self, amount) -> None:
        self._hour += amount
        if self._hour > 12:
            self._hour = 1
        elif self._hour < 1:
            self._hour = 12
        self._hour_lbl.text = f"{self._hour:02d}"

    def _adjust_minute(self, amount) -> None:
        self._minute += amount
        if self._minute >= 60:
            self._minute = 0
        elif self._minute < 0:
            self._minute = 59
        self._minute_lbl.text = f"{self._minute:02d}"

    def _toggle_am_pm(self) -> None:
        self._is_am = not self._is_am
        self._am_pm_btn.text = "AM" if self._is_am else "PM"

    def _change_count(self, amount) -> None:
        self._puzzle_count += amount
        if self._puzzle_count > 5:
            self._puzzle_count = 5
        elif self._puzzle_count < 1:
            self._puzzle_count = 1
        self._count_lbl.text = str(self._puzzle_count)

    def _on_puzzle_select(self, puzzle_type: PuzzleType, state: str) -> None:
        btn = self._toggle_btns[puzzle_type]
        if state == 'down':
            self._puzzle_type = puzzle_type
            btn.background_color = PRIMARY
            btn.color = (1, 1, 1, 1)
        else:
            btn.background_color = (0.9, 0.9, 0.92, 1)
            btn.color = TEXT

    def on_show(self) -> None:
        s = self.controller.settings
        self._hour = s.hour
        self._minute = s.minute
        self._is_am = s.is_am
        self._puzzle_type = s.puzzle_type
        self._puzzle_count = s.puzzle_count

        self._hour_lbl.text = f"{self._hour:02d}"
        self._minute_lbl.text = f"{self._minute:02d}"
        self._am_pm_btn.text = "AM" if self._is_am else "PM"
        self._count_lbl.text = str(self._puzzle_count)

        # Set toggle button states
        for p_val, btn in self._toggle_btns.items():
            if p_val == self._puzzle_type:
                btn.state = 'down'
            else:
                btn.state = 'normal'

        self._refresh_sound_lbl()

    def _refresh_sound_lbl(self) -> None:
        path = self.controller.settings.sound_path
        if path and os.path.isfile(path):
            name = os.path.basename(path)
            self._sound_lbl.text = f"🔔  {name}"
        else:
            self._sound_lbl.text = "🔔  Default Sound"

    def _cancel(self) -> None:
        self.controller.show_screen("home")

    def _save(self) -> None:
        s = self.controller.settings
        s.hour = self._hour
        s.minute = self._minute
        s.is_am = self._is_am
        s.puzzle_type = self._puzzle_type
        s.puzzle_count = self._puzzle_count
        self.controller.save_settings()
        self.controller.show_screen("home")
