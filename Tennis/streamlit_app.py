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

def predict_outcomes(matches, tour, elo):
    predictions = []
    for _, match in matches.iterrows():
        player1_name = match['Player1']
        player2_name = match['Player2']
        player1_id = player_name_to_id(tour, player1_name)
        player2_id = player_name_to_id(tour, player2_name)
        prediction = elo.predict_match_outcome(player1_id, player2_id)
        predictions.append(prediction)
    return predictions

def main():
    st.title("Upcoming Matches")
    st.sidebar.title("Filter Matches")
    selected_tour = str.lower(st.sidebar.selectbox("Tour", ['ATP', 'WTA']))
    matches = get_upcoming_matches(selected_tour)
    matches['Tour'] = selected_tour.upper()
    matches['tournament'] = matches['Tour ID'].apply(lambda x: tournament_id_to_name(tournament_id=x, tour=selected_tour))
    if matches.empty:
        st.write("No matches found")
        return

    tournaments = matches['tournament'].unique()
    selected_tournament = st.sidebar.selectbox("Tournaments", tournaments, key="tournament_selectbox")

    elo_models = {
        'atp': load_elo_model('elo_model_atp.pkl'),
        'wta': load_elo_model('elo_model_wta.pkl')
    }

    elo = elo_models[selected_tour]
    matches = matches[matches['Tour'] == selected_tour.upper()]

    filtered_matches = matches[matches['tournament'] == selected_tournament]
    filtered_predictions = predict_outcomes(filtered_matches, selected_tour, elo)

    if filtered_matches.empty:
        st.write("No matches found for the selected tournament")
        return

    st.write(f"Matches for {selected_tournament}")
    match_data = []
    for i, (_, match) in enumerate(filtered_matches.iterrows()):
        player1_name = match['Player1']
        player2_name = match['Player2']
        prediction = filtered_predictions[i]
        p1prob = round(prediction[player1_name], 2)
        p2prob = round(prediction[player2_name], 2)

        match_data.append({
            "Player 1": player1_name,
            "Player 2": player2_name,
            "P1 Model Fair": f"{p1prob}",
            "P1 Decimal": f"{round(1/p1prob, 2)}",
            "P2 Model Fair": f"{p2prob}",
            "P2 Decimal": f"{round(1/p2prob, 2)}"
        })

    match_df = pd.DataFrame(match_data)
    st.table(match_df)

if __name__ == "__main__":
    main()