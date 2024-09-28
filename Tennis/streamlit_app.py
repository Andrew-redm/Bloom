import streamlit as st
from datetime import datetime
import pandas as pd
import pickle
from accessDB import get_upcoming_matches, player_name_to_id, tournament_id_to_name
from naiveElo import EloModel, Player, Match

#lots of cheap performance improvements can be made here
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
    matches['tournament'] = matches['Tour ID'].apply(tournament_id_to_name)
    if matches.empty:
        st.write("No matches found")
        return

    st.sidebar.title("Filter Matches")
    tournaments = matches['tournament'].unique()
    selected_tournament = st.sidebar.selectbox("Tournaments", tournaments)

    filtered_matches = matches[matches['tournament'] == selected_tournament]
    filtered_predictions = predict_outcomes(filtered_matches)

    if filtered_matches.empty:
        st.write("No matches found for the selected tournament")
        return

    st.write(f"Matches for {selected_tournament}")
    match_data = []
    for i, (_, match) in enumerate(filtered_matches.iterrows()):
        player1_name = match['Player1']
        player2_name = match['Player2']
        prediction = filtered_predictions[i]
        p1prob = round(prediction[player1_name],2)
        p2prob = round(prediction[player2_name],2)

        match_data.append({
            "Player 1": player1_name,
            "Player 2": player2_name,
            "Player 1 Model Fair": f"{p1prob}",
            "Player 1 Decimal": f"{round(1/p1prob,2)}",
            "Player 2 Model Fair": f"{p2prob}",
            "Player 2 Decimal": f"{round(1/p2prob,2)}"
        })

        match_df = pd.DataFrame(match_data)
        st.table(match_df)

if __name__ == "__main__":
    main()