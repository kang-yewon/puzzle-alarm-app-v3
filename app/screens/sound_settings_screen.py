"""
Sound settings screen: select an alarm sound file.
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle, Line

from .base_screen import BaseScreen, PRIMARY, PRIMARY_DARK, TEXT, TEXT_SEC, SURFACE, BORDER, INPUT_BG, BG_COLOR, FONT_NAME


class SoundSettingsScreen(BaseScreen):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = BoxLayout(orientation='vertical')

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
            text="<",
            font_size='20sp',
            bold=True,
            background_normal='',
            background_color=SURFACE,
            color=TEXT,
            size_hint_x=None,
            width='50dp'
        )
        back_btn.bind(on_release=lambda instance: self.controller.show_screen("settings"))
        header.add_widget(back_btn)

        title_lbl = Label(
            text="Alarm Sound",
            font_name=FONT_NAME,
            font_size='16sp',
            bold=True,
            color=TEXT,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=lambda s, w: setattr(title_lbl, 'text_size', w))
        header.add_widget(title_lbl)
        header.add_widget(BoxLayout(size_hint_x=None, width='50dp')) # spacing match

        layout.add_widget(header)

        # Body Container
        body = BoxLayout(orientation='vertical', padding=[16, 20, 16, 20], spacing=16)

        # Current selection
        self._build_section_label(body, "Current Selection")

        current_frame = BoxLayout(
            orientation='horizontal',
            padding=[16, 14, 16, 14],
            spacing=12,
            size_hint_y=None,
            height='80dp'
        )
        with current_frame.canvas.before:
            Color(*SURFACE)
            self._current_bg = Rectangle(pos=current_frame.pos, size=current_frame.size)
        current_frame.bind(
            pos=lambda inst, val: setattr(self._current_bg, 'pos', val),
            size=lambda inst, val: setattr(self._current_bg, 'size', val)
        )

        note_lbl = Label(
            text="♪",
            font_size='24sp',
            color=PRIMARY,
            size_hint_x=None,
            width='30dp'
        )
        current_frame.add_widget(note_lbl)

        info_layout = BoxLayout(orientation='vertical', spacing=2)
        self._current_name = Label(
            text="Default Alarm Sound",
            font_name=FONT_NAME,
            font_size='13sp',
            bold=True,
            color=TEXT,
            halign='left',
            valign='middle'
        )
        self._current_name.bind(size=lambda s, w: setattr(self._current_name, 'text_size', w))
        
        self._current_info = Label(
            text="Built-in Beep",
            font_name=FONT_NAME,
            font_size='10sp',
            color=TEXT_SEC,
            halign='left',
            valign='middle'
        )
        self._current_info.bind(size=lambda s, w: setattr(self._current_info, 'text_size', w))

        info_layout.add_widget(self._current_name)
        info_layout.add_widget(self._current_info)
        current_frame.add_widget(info_layout)

        body.add_widget(current_frame)

        # File picker section
        self._build_section_label(body, "File Selection")

        pick_frame = BoxLayout(
            orientation='vertical',
            padding=[16, 16, 16, 16],
            spacing=8,
            size_hint_y=None,
            height='120dp'
        )
        with pick_frame.canvas.before:
            Color(*SURFACE)
            self._pick_bg = Rectangle(pos=pick_frame.pos, size=pick_frame.size)
        pick_frame.bind(
            pos=lambda inst, val: setattr(self._pick_bg, 'pos', val),
            size=lambda inst, val: setattr(self._pick_bg, 'size', val)
        )

        pick_btn = Button(
            text="Choose File",
            font_name=FONT_NAME,
            font_size='13sp',
            bold=True,
            background_normal='',
            background_color=INPUT_BG,
            color=PRIMARY,
            size_hint_y=None,
            height='50dp'
        )
        pick_btn.bind(on_release=lambda instance: self._pick_file())
        pick_frame.add_widget(pick_btn)

        hint = Label(
            text="Select an audio file (.mp3, .wav) to use as the alarm sound.",
            font_name=FONT_NAME,
            font_size='10sp',
            color=TEXT_SEC,
            halign='center',
            valign='middle',
            text_size=(250, None)
        )
        pick_frame.add_widget(hint)
        body.add_widget(pick_frame)

        body.add_widget(BoxLayout(size_hint_y=0.2))

        # Reset to default
        reset_btn = Button(
            text="Reset to Default",
            font_name=FONT_NAME,
            font_size='12sp',
            background_normal='',
            background_color=BG_COLOR,
            color=TEXT_SEC,
            size_hint_y=None,
            height='45dp'
        )
        reset_btn.bind(on_release=lambda instance: self._reset_sound())
        body.add_widget(reset_btn)

        layout.add_widget(body)
        self.add_widget(layout)

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

    def on_show(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        path = self.controller.settings.sound_path
        if path and os.path.isfile(path):
            name = os.path.basename(path)
            self._current_name.text = name
            self._current_info.text = path
        else:
            self._current_name.text = "Default Alarm Sound"
            self._current_info.text = "Built-in Beep"

    def _pick_file(self) -> None:
        # Create a popup file chooser dialog
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        file_chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=['*.mp3', '*.wav', '*.ogg', '*.m4a']
        )
        popup_layout.add_widget(file_chooser)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=10)
        
        cancel_btn = Button(
            text="Cancel",
            font_name=FONT_NAME,
            background_normal='',
            background_color=(0.9, 0.9, 0.92, 1),
            color=TEXT
        )
        select_btn = Button(
            text="Select",
            font_name=FONT_NAME,
            background_normal='',
            background_color=PRIMARY,
            color=(1, 1, 1, 1)
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        popup_layout.add_widget(btn_layout)
        
        popup = Popup(
            title="Select Alarm Sound",
            content=popup_layout,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(instance):
            if file_chooser.selection:
                path = file_chooser.selection[0]
                self.controller.settings.sound_path = path
                self.controller.save_settings()
                self._refresh()
                popup.dismiss()

        cancel_btn.bind(on_release=popup.dismiss)
        select_btn.bind(on_release=on_select)
        
        popup.open()

    def _reset_sound(self) -> None:
        self.controller.settings.sound_path = ""
        self.controller.save_settings()
        self._refresh()
