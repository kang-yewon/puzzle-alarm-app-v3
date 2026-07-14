"""
Math puzzle: simple but tricky arithmetic questions.
"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

from .base_puzzle import BasePuzzle, COLORS, FONT_NAME


_TEMPLATES = [
    lambda: _make(random.randint(11, 19), "×", random.randint(2, 9),
                  "-", random.randint(1, 20)),
    lambda: _make(random.randint(2, 9), "×", random.randint(11, 19),
                  "+", random.randint(1, 20)),
    lambda: _make(random.randint(10, 30), "+", random.randint(10, 30),
                  "×", random.randint(2, 5)),   # order-of-operations trap
    lambda: _make_div(),
    lambda: _make(random.randint(50, 99), "-", random.randint(11, 49),
                  "+", random.randint(1, 15)),
]


def _make(a, op1, b, op2, c):
    if op1 == "×" and op2 == "+":
        answer = a * b + c
    elif op1 == "×" and op2 == "-":
        answer = a * b - c
    elif op1 == "+" and op2 == "×":
        answer = a + b * c   # order of operations trap
    elif op1 == "-" and op2 == "+":
        answer = a - b + c
    else:
        answer = a + b - c
    question = f"{a} {op1} {b} {op2} {c} = ?"
    return question, answer


def _make_div():
    b = random.randint(2, 9)
    a = b * random.randint(3, 12)
    c = random.randint(1, 10)
    answer = a // b + c
    question = f"{a} ÷ {b} + {c} = ?"
    return question, answer


def generate_question() -> tuple[str, int]:
    template = random.choice(_TEMPLATES)
    return template()


class MathPuzzle(BasePuzzle):
    def _build_ui(self) -> None:
        self._question, self._answer = generate_question()
        
        self.padding = [30, 20, 30, 20]
        self.spacing = 10

        self.add_widget(BoxLayout(size_hint_y=0.1))

        question_lbl = Label(
            text=self._question,
            font_size='28sp',
            bold=True,
            color=COLORS["text"],
            size_hint_y=None,
            height='60dp'
        )
        self.add_widget(question_lbl)

        self._entry = TextInput(
            multiline=False,
            font_size='20sp',
            halign='center',
            background_color=COLORS["input_bg"],
            foreground_color=COLORS["text"],
            size_hint_y=None,
            height='50dp',
            input_filter='int'
        )
        self._entry.bind(text=lambda instance, value: self.notify_activity())
        self._entry.bind(on_text_validate=lambda instance: self._check())
        self.add_widget(self._entry)

        hint = Label(
            text="정답 입력",
            font_name=FONT_NAME,
            font_size='12sp',
            color=COLORS["text_secondary"],
            size_hint_y=None,
            height='20dp'
        )
        self.add_widget(hint)

        confirm_btn = Button(
            text="확인",
            font_name=FONT_NAME,
            font_size='16sp',
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
            font_size='12sp',
            color=COLORS["error"],
            size_hint_y=None,
            height='30dp'
        )
        self.add_widget(self._feedback)

        self.add_widget(BoxLayout(size_hint_y=0.3))

        Clock.schedule_once(lambda dt: setattr(self._entry, 'focus', True), 0.1)

    def _check(self) -> None:
        self.notify_activity()
        raw = self._entry.text.strip()
        try:
            value = int(raw)
        except ValueError:
            self._feedback.text = "숫자를 입력해 주세요."
            self._feedback.color = COLORS["error"]
            return
        if value == self._answer:
            self._feedback.text = "정답!"
            self._feedback.color = COLORS["success"]
            Clock.schedule_once(lambda dt: self.on_success(), 0.4)
        else:
            self._feedback.text = "틀렸어요. 다시 시도하세요."
            self._feedback.color = COLORS["error"]
            self._entry.text = ""
            self._record_wrong()
