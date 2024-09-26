from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
from accessDB import get_tournaments_in_daterange, get_matches_in_tournament

class Player(BaseModel):
    id: int
    name: str
    elo: float = 1500.0
    elo_history: Dict[datetime, float] = {}

    def update_elo(self, new_elo: float, date: datetime):
        self.elo = new_elo
        self.elo_history[date] = new_elo

class Match(BaseModel):
    winner: Player
    loser: Player
    date: datetime

class EloModel:
    def __init__(self, k_factor: float = 32):
        self.players: Dict[int, Player] = {}
        self.k_factor = k_factor

    def add_player(self, player_id: int, player_name: str):
        if player_id not in self.players:
            self.players[player_id] = Player(id=player_id, name=player_name)

    def get_player(self, player_id: int) -> Player:
        return self.players.get(player_id)

    def update_elo(self, match: Match):
        winner = match.winner
        loser = match.loser

        updated_score_winner = 1 / (1 + 10 ** ((loser.elo - winner.elo) / 400))
        updated_score_loser = 1 / (1 + 10 ** ((winner.elo - loser.elo) / 400))

        winner.elo += self.k_factor * (1 - updated_score_winner)
        loser.elo += self.k_factor * (0 - updated_score_loser)

    def process_matches(self, matches: List[Match]):
        for match in matches:
            self.update_elo(match)

def main(start_date: str, end_date: str):
    elo = EloModel()
    tournaments = get_tournaments_in_daterange(
        datetime.strptime(start_date, '%Y-%m-%d'),
        datetime.strptime(end_date, '%Y-%m-%d')
    )

    matches = get_matches_in_tournament(list(set(tournaments['Tour_ID'])))
    for _, match in matches.iterrows():
        winner_id = match['ID Winner_G']
        loser_id = match['ID Loser_G']
        winner_name = match['winnerName']
        loser_name = match['loserName']

        elo.add_player(winner_id, winner_name)
        elo.add_player(loser_id, loser_name)
    
        winner = elo.get_player(winner_id)
        loser = elo.get_player(loser_id)
        match = Match(winner=winner, loser=loser, date=match['Date_G'])
        elo.update_elo(match)

    for player in elo.players.values():
        print(f"Player: {player.name}, ELO: {player.elo}")

if __name__ == "__main__":
    start_date = '2023-01-01'
    end_date = '2024-06-30'
    main(start_date, end_date)