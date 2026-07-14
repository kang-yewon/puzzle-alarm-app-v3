"""
Data models for the puzzle alarm app.
Designed to be UI-framework-agnostic for easy mobile porting.
"""

from dataclasses import dataclass, field
from enum import Enum


class PuzzleType(Enum):
    MATH = "math"
    COLOR = "color"
    TYPING = "typing"


@dataclass
class AlarmSettings:
    hour: int = 7
    minute: int = 0
    is_am: bool = True          # True = AM, False = PM
    enabled: bool = True
    puzzle_type: PuzzleType = PuzzleType.MATH
    puzzle_count: int = 3
    sound_path: str = ""        # Empty string = use built-in beep

    def hour_24(self) -> int:
        """Return hour in 24-hour format."""
        h = self.hour % 12
        return h if self.is_am else h + 12

    def display_time(self) -> str:
        period = "AM" if self.is_am else "PM"
        return f"{self.hour:02d}:{self.minute:02d} {period}"
