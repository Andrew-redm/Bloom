from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
from accessDB import get_matches_in_daterange, player_name_to_id
import pandas as pd
import pickle
import matplotlib.pyplot as plt


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

    def calculate_expected_score(self, player1: Player, player2: Player) -> float:
        return 1 / (1 + 10 ** ((player2.elo - player1.elo) / 400))

    def update_elo(self, match: Match):
        winner = match.winner
        loser = match.loser

        expected_score_winner = self.calculate_expected_score(winner, loser)
        expected_score_loser = self.calculate_expected_score(loser, winner)

        winner.elo += self.k_factor * (1 - expected_score_winner)
        loser.elo += self.k_factor * (0 - expected_score_loser)

        winner.update_elo(winner.elo, match.date)
        loser.update_elo(loser.elo, match.date)

    def process_matches(self, matches: List[Match]):
        for match in matches:
            self.update_elo(match)

    def predict_match_outcome(self, player1_id: int, player2_id: int) -> Dict[str, float]:
        player1 = self.get_player(player1_id)
        player2 = self.get_player(player2_id)

        if not player1 or not player2:
            raise ValueError("Both players must be added to the ELO system before predicting a match.")

        expected_score1 = self.calculate_expected_score(player1, player2)
        expected_score2 = self.calculate_expected_score(player2, player1)

        return {
            player1.name: expected_score1,
            player2.name: expected_score2
        }

elo = EloModel()

def load_data(start_date: str, end_date: str):
    matches = get_matches_in_daterange(
        datetime.strptime(start_date, '%Y-%m-%d'),
        datetime.strptime(end_date, '%Y-%m-%d')
    )
    matches = matches.sort_values(by='Date_G')
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

def plot_elo_history(player_names: List[str]):
    plt.figure(figsize=(10, 5))

    for player_name in player_names:
        player_id = player_name_to_id(player_name)
        player = elo.get_player(player_id)

        if not player:
            raise ValueError(f"Player {player_name} not found in the ELO system.")

        dates = list(player.elo_history.keys())
        elos = list(player.elo_history.values())

        plt.plot(dates, elos, marker='o', linestyle='-', label=player_name)

    plt.title('ELO Rating History')
    plt.xlabel('Date')
    plt.ylabel('ELO Rating')
    plt.legend()
    plt.grid(True)
    plt.show()

def get_elo_history_df(player_name: str) -> pd.DataFrame:
    player_id = player_name_to_id(player_name)
    player = elo.get_player(player_id)

    if not player:
        raise ValueError(f"Player {player_name} not found in the ELO system.")

    data = {
        'Date': list(player.elo_history.keys()),
        'ELO': list(player.elo_history.values())
    }

    return pd.DataFrame(data)

def main(start_date: str, end_date: str):
    load_data(start_date, end_date)

    for player in elo.players.values():
        print(f"Player: {player.name}, ELO: {player.elo}")

if __name__ == "__main__":
    start_date = '2022-01-01'
    end_date = '2024-09-20'
    main(start_date, end_date)

def save_elo_model(filename: str):
    with open(filename, 'wb') as file:
        pickle.dump(elo, file)

def load_elo_model(filename: str) -> EloModel:
    with open(filename, 'rb') as file:
        return pickle.load(file)