import streamlit as st
from datetime import datetime
import pandas as pd
import pickle
from accessDB import get_upcoming_matches, player_name_to_id
from naiveElo import EloModel, Player, Match


def load_elo_model(filename: str):
    with open(filename, 'rb') as file:
        return pickle.load(file)

elo = load_elo_model('elo_model.pkl')

def predict_outcomes(matches):
    predictions = []
    for _, match in matches.iterrows():
        player1_name = match['Player1']
        player2_name = match['Player2']
        player1_id = player_name_to_id(player1_name)
        player2_id = player_name_to_id(player2_name)
        prediction = elo.predict_match_outcome(player1_id, player2_id)
        predictions.append(prediction)
    return predictions

def main():
    st.title("Today's Matches")

    matches = get_upcoming_matches()
    if matches.empty:
        st.write("No matches found")
        return

    predictions = predict_outcomes(matches)

    for i, (_, match) in enumerate(matches.iterrows()):
        player1_name = match['Player1']
        player2_name = match['Player2']
        # odds_player1 = match['Odds_Player1']
        # odds_player2 = match['Odds_Player2']
        prediction = predictions[i]

        st.write(f"{player1_name} vs {player2_name}")
        st.write(f"{player1_name} - {prediction[player1_name]:.2f}%, {player2_name} - {prediction[player2_name]:.2f}%")
        st.write("---")

if __name__ == "__main__":
    main()

