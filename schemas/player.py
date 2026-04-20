from dataclasses import dataclass
from enum import Enum


class PlayerRole(Enum):
    MAFIA = "mafia"
    SHERIFF = "sheriff"
    DOCTOR = "doctor"
    CIVILIAN = "civilian"


@dataclass
class Player:
    name: str
    role: PlayerRole
    alive: bool = True
    vote_count: int = 0

    def die(self):
        self.alive = False

    def heal(self):
        self.alive = True