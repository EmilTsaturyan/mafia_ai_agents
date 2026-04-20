import os
from typing import List, Dict, Tuple
import random
import time

from langchain.agents import create_agent   
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from constants.prompt import SYSTEM_PROMPT, PERSONAL_PROMPT
from schemas.response import AgentResponse, ActionType
from schemas.history import History, HistoryType
from schemas.player import Player, PlayerRole
from schemas.phase import PhaseType


api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key


class Game:
    def __init__(
            self, 
            llm: BaseChatModel,
            number_of_players: int = 5,
            number_of_mafia: int = 1
            ):
        self.llm: BaseChatModel = llm
        self.history: List[History] = []
        self.players: List[Player] = []
        self.number_of_players: int = number_of_players
        self.number_of_mafia: int = number_of_mafia
        self.sheriff_checked: Dict[str, PlayerRole] = {} #for sheriff private info
        self.last_heal: str = "" #for doctor private info
        self.phase: PhaseType = PhaseType.INTRODUCE

    def generate_roles(self) -> List[PlayerRole]:
        number_of_civilian = self.number_of_players - self.number_of_mafia - 2 # Sherrif and Doctor
        roles = (
            [PlayerRole.CIVILIAN] * number_of_civilian +
            [PlayerRole.MAFIA] * self.number_of_mafia +
            [PlayerRole.SHERIFF] +
            [PlayerRole.DOCTOR]
        )
        random.shuffle(roles)

        return roles

    def create_players(self) -> None:
        roles = self.generate_roles()
        for i in range(self.number_of_players):
            
            self.players.append(
                Player(
                    name=f"Player{i+1}",
                    role=roles[i]
                )
            )

    def get_player_by_name(self, name: str) -> Player:
        for player in self.players:
            if player.name == name:
                return player
    
    def get_alive_players(self) -> List[str]:
        return [player.name for player in self.players if player.alive]
    
    def get_all_players(self) -> List[str]:
        return [player.name for player in self.players]
    
    def get_mafia_team(self) -> List[str]: #for mafia private info
        return [player.name for player in self.players if player.role == PlayerRole.MAFIA]
    
    def get_history(self) -> str:
        return str([str(history) for history in self.history])

    def get_private_info(self, player: Player) -> str:
        if player.role == PlayerRole.MAFIA:
            return f"Mafia Team: {self.get_mafia_team()}"
        elif player.role == PlayerRole.SHERIFF:
            return f"You checked this players: {self.sheriff_checked}"
        elif player.role == PlayerRole.DOCTOR:
            return f"Last time you healed: {self.last_heal}, you cant heal this persion again"
        else:
            return ""
    
    def get_personal_prompt(self, player: Player) -> str:
        return PERSONAL_PROMPT.format(
            name=player.name,
            role=player.role.value,
            phase=self.phase.value,
            alive_players=self.get_alive_players(),
            players=self.get_all_players(),
            history=self.get_history(),
            private_info=self.get_private_info(player)
        )
    
    def invoke(self, prompt: str) -> AgentResponse:
        response = self.llm.invoke({
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        return response.get("structured_response")
    
    def check_win_condition(self) -> bool:
        return (self.number_of_mafia >= len(self.get_alive_players()) - self.number_of_mafia) or (self.number_of_mafia <= 0)
    
    def introduction_phase(self) -> None:
        for player in self.players:
            prompt = self.get_personal_prompt(player)
            response = self.invoke(prompt)
            print(f"Name: {player.name}, Role: {player.role.value}")
            print(f"Action: {response.action.value}, Target: {response.target}, Text: {response.text}")
            print("-" * 100)
            self.history.append(History(
                type=HistoryType.INTRODUCE,
                player=player.name,
                target=None,
                text=response.text
            ))
    
    def nigh_phase(
        self, 
        response: AgentResponse,
        player: Player
        ) -> Tuple[Dict[str, Player], Player]:
        
        killed_players: Dict[str, Player] = {}
        healed_player: Player = None

        if player.role == PlayerRole.MAFIA and response.action == ActionType.KILL:
            target_player = self.get_player_by_name(response.target)
            killed_players[player.name] = target_player
        elif player.role == PlayerRole.SHERIFF and response.action == ActionType.CHECK:
            target_player = self.get_player_by_name(response.target)
            target_player_role = target_player.role.value
            self.sheriff_checked[target_player.name] = target_player_role
        elif player.role == PlayerRole.DOCTOR and response.action == ActionType.HEAL:
            target_player = self.get_player_by_name(response.target)
            if target_player.alive:
                target_player.heal()
                healed_player = target_player
                self.last_heal = healed_player.name

        return killed_players, healed_player

    def day_phase(
        self,
        response: AgentResponse,
        player: Player
    ) -> None:
        if response.action == ActionType.SPEECH:
            self.history.append(History(
                type=HistoryType.SPEECH,
                player=player.name,
                target=None,
                text=response.text
            ))

    def vote_phase(
        self,
        response: AgentResponse,
        player: Player
    ) -> int:
        skipped_count = 0
        if response.action == ActionType.VOTE:
            target_player = self.get_player_by_name(response.target)
            target_player.vote_count += 1
            self.history.append(History(
                type=HistoryType.VOTE,
                player=player.name,
                target=target_player.name,
                text=response.text
            ))
        elif response.action == ActionType.SKIP:
            skipped_count += 1
            self.history.append(History(
                type=HistoryType.SKIP,
                player=player.name,
                target=None,
                text=response.text
            ))
        return skipped_count

    def apply_night_actions(self, killed_players: Dict[str, Player], healed_player: Player) -> None:
        for killer, killed_player in killed_players.items():
            if killed_player == healed_player:
                self.history.append(History(
                    type=HistoryType.HEAL,
                    player=killer,
                    target=healed_player.name,
                    text=None
                ))
            else:
                killed_player.die()
                self.history.append(History(
                    type=HistoryType.KILL,
                    player=killer,
                    target=killed_player.name,
                    text=None
                ))
    
    def apply_vote_actions(self, skipped_count: int) -> None:
        max_vote_count = 0
        for player in self.players:
            if player.vote_count > max_vote_count:
                max_vote_count = player.vote_count
        
        players_with_max_votes = [player for player in self.players if player.vote_count == max_vote_count]
        
        if len(players_with_max_votes) == 1 and max_vote_count > 0 and skipped_count < max_vote_count:
            max_vote_player = players_with_max_votes[0]
            max_vote_player.die()
            self.history.append(History(
                type=HistoryType.KICKED,
                player=max_vote_player.name,
                target=None,
                text=None
            ))

            if max_vote_player.role == PlayerRole.MAFIA:
                self.number_of_mafia -= 1
        
        for player in self.players:
            player.vote_count = 0

    def print_history(self) -> None:
        for history in self.history:
            print(history)

    def start(self):
        #Create players
        self.create_players()

        #Introduction phase
        self.phase = PhaseType.INTRODUCE
        self.introduction_phase()
        
        #Main game loop
        while self.check_win_condition() is not True:
            for phase in [PhaseType.NIGHT, PhaseType.DAY, PhaseType.VOTE]:
                self.phase = phase
                skipped_count = 0
                killed_players = {}
                healed_player = None

                for player in self.players:
                    if player.alive:
                        prompt = self.get_personal_prompt(player)
                        response = self.invoke(prompt)

                        #Day phase
                        if self.phase == PhaseType.DAY:
                            self.day_phase(response, player)
                        #Vote phase
                        elif self.phase == PhaseType.VOTE:
                            skipped_count += self.vote_phase(response, player)

                        #Nigh phase
                        if self.phase == PhaseType.NIGHT:
                            kp, hp = self.nigh_phase(response, player)
                            killed_players.update(kp)
                            if hp:
                                healed_player = hp
                
                # Apply night actions
                self.apply_night_actions(killed_players, healed_player)
                killed_players = {}
                healed_player = None
                
                # Apply vote actions
                if self.phase == PhaseType.VOTE:
                    self.apply_vote_actions(skipped_count)
                time.sleep(60)
        self.print_history()



def main():
    llm = create_agent(
        ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview"),
        system_prompt=SYSTEM_PROMPT,
        response_format=AgentResponse
    )
    game = Game(llm, 5, 1)
    game.start()


if __name__ == "__main__":
    main()