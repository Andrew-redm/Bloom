from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime
from accessDB import get_matches_in_daterange, get_player_id
import pandas as pd
import pickle
import matplotlib.pyplot as plt

class Player(BaseModel):
    id: int
    name: str
    elo: Dict[str, float] = Field(default_factory=dict)
    elo_history: Dict[str, Dict[datetime, float]] = Field(default_factory=lambda: {
        'overall': {},
        'hard': {},
        'clay': {},
        'grass': {},
        'indoor hard': {},
        'carpet': {},
        'acrylic': {},
    })

    def __init__(self, **data):
        super().__init__(**data)
        self.set_initial_elo(data.get('tournament_rank', 5)) #default to 1500

    def set_initial_elo(self, tournament_rank: int):
        initial_elo = 1500.0  # Default ELO
        if tournament_rank in [0, 1]:
            initial_elo = 1420.0
        elif tournament_rank in [6]:
            initial_elo = 1340.0
        # Apply the initial ELO across all surfaces
        self.elo = {
            'overall': initial_elo,
            'hard': initial_elo,
            'clay': initial_elo,
            'grass': initial_elo,
            'indoor hard': initial_elo,
            'carpet': initial_elo,
            'acrylic': initial_elo,
        }

    def update_elo(self, new_elo: float, date: datetime):
        self.elo['overall'] = new_elo
        self.elo_history['overall'][date] = new_elo

    def update_surface_elo(self, surface: str, new_elo: float, date: datetime):
        self.elo[surface] = new_elo
        self.elo_history[surface][date] = new_elo

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

    def calculate_expected_score(self, player1: Player, player2: Player, surface: str = 'overall') -> float:
        return 1 / (1 + 10 ** ((player2.elo[surface] - player1.elo[surface]) / 400))
    
    def update_elo(self, match: Match):
        winner = match.winner
        loser = match.loser

        expected_score_winner = self.calculate_expected_score(winner, loser)
        expected_score_loser = self.calculate_expected_score(loser, winner)

        winner.elo['overall'] += self.k_factor * (1 - expected_score_winner)
        loser.elo['overall'] += self.k_factor * (0 - expected_score_loser)

        winner.update_elo(winner.elo['overall'], match.date)
        loser.update_elo(loser.elo['overall'], match.date)
        
    def update_surface_elo(self, surface: str, match: Match):
        winner = match.winner
        loser = match.loser
        expected_score_winner = self.calculate_expected_score(winner, loser, surface)
        expected_score_loser = self.calculate_expected_score(loser, winner, surface)
        winner.elo[surface] += self.k_factor * (1 - expected_score_winner)
        loser.elo[surface] += self.k_factor * (0 - expected_score_loser)
        winner.update_surface_elo(surface, winner.elo[surface], match.date)
        loser.update_surface_elo(surface, loser.elo[surface], match.date)

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

def load_data(tour, start_date: str, end_date: str):
    matches = get_matches_in_daterange(
        tour,
        datetime.strptime(start_date, '%Y-%m-%d'),
        datetime.strptime(end_date, '%Y-%m-%d')
    )
    matches = pd.DataFrame(matches).sort_values(by='DATE_G')
    for _, match in matches.iterrows():
        winner_id = match['ID1_G']
        loser_id = match['ID2_G']
        winner_name = match['player1_name']
        loser_name = match['player2_name']

        elo.add_player(winner_id, winner_name)
        elo.add_player(loser_id, loser_name)
    
        winner = elo.get_player(winner_id)
        loser = elo.get_player(loser_id)
        match_obj = Match(winner=winner, loser=loser, date=match['DATE_G'])
        elo.update_elo(match_obj)
        elo.update_surface_elo(match['surface'], match_obj)

    return matches

#refactor some other time
# def plot_elo_history(tour, player_names: List[str], elo_type: str = 'overall'):
#     for player_name in player_names:
#         player_id = player_name_to_id(tour, player_name)
#         player = elo.get_player(player_id)
#         if not player:
#             raise ValueError(f"Player {player_name} not found in the ELO system.")

#         dates = list(player.elo_history[elo_type].keys())
#         elos = list(player.elo_history[elo_type].values())

#         plt.plot(dates, elos, marker='o', linestyle='-', label=player_name)

#     plt.title('ELO Rating History')
#     plt.xlabel('Date')
#     plt.ylabel('ELO Rating')
#     plt.legend()
#     plt.grid(True)
#     plt.show()

def plot_elo_history(tour, player_names: List[str], elo_type: str = 'overall'):
    for player_name in player_names:
        player_id = get_player_id(tour, player_name)
        player = elo.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_name} not found in the ELO system.")

        dates = list(player.elo_history[elo_type].keys())
        elos = list(player.elo_history[elo_type].values())

        plt.plot(dates, elos, marker='o', linestyle='-', label=player_name)

    plt.title('ELO Rating History')
    plt.xlabel('Date')
    plt.ylabel('ELO Rating')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage


#refactor some other time
# def get_elo_history_df(tour, player_name: str) -> pd.DataFrame:
#     player_id = player_name_to_id(tour, player_name)
#     player = elo.get_player(player_id)

#     if not player:
#         raise ValueError(f"Player {player_name} not found in the ELO system.")

#     data = {
#         'Date': list(player.elo_history.keys()),
#         'ELO': list(player.elo_history.values())
#     }

#     return pd.DataFrame(data)

def main(tour: str, start_date: str, end_date: str):
    load_data(tour, start_date, end_date)

    for player in elo.players.values():
        print(f"Player: {player.name}, ELO: {player.elo['overall']}")

def save_elo_model(filename: str):

    with open(filename, 'wb') as file:
        pickle.dump(elo, file)

def load_elo_model(filename: str) -> EloModel:
    with open(filename, 'rb') as file:
        return pickle.load(file)
    
if __name__ == "__main__":
    tour = 'wta'
    start_date = '2021-01-01'
    end_date = '2024-10-16'
    main(tour, start_date, end_date)
    save_elo_model(f'elo_model_{tour}.pkl')

