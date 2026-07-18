"""
Home screen: displays alarm time, on/off toggle, and settings button.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse

from .base_screen import BaseScreen, PRIMARY, TEXT, TEXT_SEC, FONT_NAME


class CanvasToggle(ButtonBehavior, Widget):
    def __init__(self, active=True, on_active=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (56, 28)
        self.active = active
        self.on_active = on_active
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Pill background
            color = (185/255.0, 110/255.0, 1.0, 1.0) if self.active else (204/255.0, 204/255.0, 204/255.0, 1.0)
            Color(*color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14])

            # Knob
            Color(1.0, 1.0, 1.0, 1.0)
            x = self.x + 42 - 11 if self.active else self.x + 14 - 11
            y = self.y + 14 - 11
            Ellipse(pos=(x, y), size=(22, 22))

    def on_press(self):
        self.active = not self.active
        self.draw()
        if self.on_active:
            self.on_active(self.active)


class HomeScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = BoxLayout(orientation='vertical', padding=[30, 40, 30, 40], spacing=20)

        # Clock icon
        icon_lbl = Label(
            text="⏰", 
            font_size='56sp', 
            size_hint_y=None, 
            height='100dp',
            halign='center'
        )
        layout.add_widget(icon_lbl)

        # "Next Alarm"
        next_lbl = Label(
            text="Next Alarm",
            font_name=FONT_NAME,
            font_size='14sp',
            color=TEXT_SEC,
            size_hint_y=None,
            height='24dp',
            halign='center'
        )
        layout.add_widget(next_lbl)

        # Time label
        self._time_lbl = Label(
            text="07:00 AM",
            font_size='48sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height='70dp',
            halign='center'
        )
        layout.add_widget(self._time_lbl)

        layout.add_widget(BoxLayout(size_hint_y=0.1))

        # Toggle row
        toggle_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        toggle_row.add_widget(BoxLayout(size_hint_x=0.3))  # Spacer

        self._toggle = CanvasToggle(active=True, on_active=self._toggle_alarm)
        toggle_row.add_widget(self._toggle)

        self._toggle_label = Label(
            text="ON",
            font_name=FONT_NAME,
            font_size='14sp',
            bold=True,
            color=PRIMARY,
            size_hint_x=0.3,
            halign='left',
            valign='middle'
        )
        self._toggle_label.bind(size=lambda s, w: setattr(self._toggle_label, 'text_size', w))
        toggle_row.add_widget(self._toggle_label)
        toggle_row.add_widget(BoxLayout(size_hint_x=0.2))  # Spacer

        layout.add_widget(toggle_row)

        layout.add_widget(BoxLayout(size_hint_y=0.3))

        # Settings button
        settings_btn = Button(
            text="  ⚙  Settings",
            font_name=FONT_NAME,
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=PRIMARY,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height='55dp'
        )
        settings_btn.bind(on_release=lambda instance: self.controller.show_screen("settings"))
        layout.add_widget(settings_btn)

        layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.add_widget(layout)

    def _toggle_alarm(self, active: bool) -> None:
        settings = self.controller.settings
        settings.enabled = active
        self.controller.save_settings()
        self._refresh()

    def on_show(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        s = self.controller.settings
        self._time_lbl.text = s.display_time()
        self._toggle.active = s.enabled
        self._toggle.draw()
        if s.enabled:
            self._toggle_label.text = "ON"
            self._toggle_label.color = PRIMARY
        else:
            self._toggle_label.text = "OFF"
            self._toggle_label.color = TEXT_SEC
