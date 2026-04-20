from typing import Optional

from dataclasses import dataclass
from enum import Enum


class HistoryType(Enum):
    KILL = "kill"
    HEAL = "heal"
    VOTE = "vote"
    SKIP = "skip"
    SPEECH = "speech"
    INTRODUCE = "introduce"
    KICKED = "kicked"


@dataclass
class History:
    type: HistoryType
    player: Optional[str]
    target: Optional[str]
    text: Optional[str]

    def __str__(self):
        if self.type == HistoryType.KILL:
            return f"{self.target} was killed during the night"
        elif self.type == HistoryType.HEAL:
            return f"{self.target} was killed during the night, but got healed by doctor"
        elif self.type == HistoryType.VOTE:
            return f"{self.player} voted for {self.target}"
        elif self.type == HistoryType.SKIP:
            return f"{self.player} skipped"
        elif self.type == HistoryType.SPEECH:
            return f"{self.player} said: {self.text}"
        elif self.type == HistoryType.INTRODUCE:
            return f"{self.player} introduced: {self.text}"
        elif self.type == HistoryType.KICKED:
            return f"{self.player} was kicked"
        