from typing import Optional

from pydantic import BaseModel
from enum import Enum


class ActionType(Enum):
    KILL = "kill"
    HEAL = "heal"
    VOTE = "vote"
    SKIP = "skip"
    SPEECH = "speech"
    INTRODUCE = "introduce"
    CHECK = "check"

    
class AgentResponse(BaseModel):
    action: ActionType
    target: Optional[str]
    text: Optional[str]