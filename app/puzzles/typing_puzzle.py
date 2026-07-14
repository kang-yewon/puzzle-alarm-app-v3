"""
Typing puzzle: type the displayed sentence exactly.
"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line

from .base_puzzle import BasePuzzle, COLORS, FONT_NAME


_SENTENCES = [
    "오늘도 좋은 하루입니다.",
    "일어나서 하루를 시작하세요.",
    "좋은 아침이에요, 힘내세요!",
    "오늘 하루도 파이팅입니다.",
    "일어나야 할 시간이에요.",
    "새로운 하루가 시작되었습니다.",
    "건강한 하루 보내세요.",
    "일찍 일어나는 새가 먹이를 잡는다.",
    "지금 일어나면 하루가 달라집니다.",
    "알람을 끄고 기지개를 켜세요.",
]


def pick_sentence() -> str:
    return random.choice(_SENTENCES)


class TypingPuzzle(BasePuzzle):
    def _build_ui(self) -> None:
        self._target = pick_sentence()

        self.padding = [30, 15, 30, 15]
        self.spacing = 10

        desc = Label(
            text="아래 문장을 똑같이 입력하세요.",
            font_name=FONT_NAME,
            font_size='13sp',
            color=COLORS["text_secondary"],
            size_hint_y=None,
            height='24dp'
        )
        self.add_widget(desc)

        # Target Frame Container (White background, light purple border)
        target_container = BoxLayout(
            orientation='vertical',
            padding=[10, 14, 10, 14],
            size_hint_y=None,
            height='90dp'
        )
        
        with target_container.canvas.before:
            Color(*COLORS["surface"])
            self._target_bg = Rectangle(pos=target_container.pos, size=target_container.size)
            Color(*COLORS["border"])
            self._target_border = Line(rectangle=(target_container.x, target_container.y, target_container.width, target_container.height), width=1)
            
        target_container.bind(
            pos=lambda inst, val: (
                setattr(self._target_bg, 'pos', val),
                setattr(self._target_border, 'points', [target_container.x, target_container.y, target_container.x + target_container.width, target_container.y, target_container.x + target_container.width, target_container.y + target_container.height, target_container.x, target_container.y + target_container.height, target_container.x, target_container.y])
            ),
            size=lambda inst, val: (
                setattr(self._target_bg, 'size', val),
                setattr(self._target_border, 'points', [target_container.x, target_container.y, target_container.x + target_container.width, target_container.y, target_container.x + target_container.width, target_container.y + target_container.height, target_container.x, target_container.y + target_container.height, target_container.x, target_container.y])
            )
        )

        target_lbl = Label(
            text=self._target,
            font_name=FONT_NAME,
            font_size='16sp',
            bold=True,
            color=COLORS["primary"],
            halign='center',
            valign='middle',
            text_size=(280, None)
        )
        target_container.add_widget(target_lbl)
        self.add_widget(target_container)

        self._entry = TextInput(
            multiline=False,
            font_name=FONT_NAME,
            font_size='14sp',
            halign='center',
            background_color=COLORS["input_bg"],
            foreground_color=COLORS["text"],
            size_hint_y=None,
            height='50dp'
        )
        self._entry.bind(text=lambda instance, value: self.notify_activity())
        self._entry.bind(on_text_validate=lambda instance: self._check())
        self.add_widget(self._entry)

        hint = Label(
            text="여기에 입력하세요.",
            font_name=FONT_NAME,
            font_size='11sp',
            color=COLORS["text_secondary"],
            size_hint_y=None,
            height='20dp'
        )
        self.add_widget(hint)

        confirm_btn = Button(
            text="확인",
            font_name=FONT_NAME,
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=COLORS["primary"],
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height='50dp'
        )
        confirm_btn.bind(on_release=lambda instance: self._check())
        self.add_widget(confirm_btn)

        self._feedback = Label(
            text="",
            font_name=FONT_NAME,
            font_size='11sp',
            color=COLORS["error"],
            size_hint_y=None,
            height='30dp'
        )
        self.add_widget(self._feedback)

        Clock.schedule_once(lambda dt: setattr(self._entry, 'focus', True), 0.1)

    def _check(self) -> None:
        self.notify_activity()
        typed = self._entry.text.strip()
        if typed == self._target:
            self._feedback.text = "정답!"
            self._feedback.color = COLORS["success"]
            Clock.schedule_once(lambda dt: self.on_success(), 0.4)
        else:
            self._feedback.text = "똑같이 입력해 주세요."
            self._feedback.color = COLORS["error"]
            self._entry.text = ""
            self._record_wrong()
