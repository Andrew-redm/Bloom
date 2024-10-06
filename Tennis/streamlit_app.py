import streamlit as st
import pandas as pd
import pickle
from accessDB import get_upcoming_matches, player_name_to_id, tournament_id_to_name
from naiveElo import EloModel, Player, Match

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

def format_player_name(player_name, model_value, market_price):
    if model_value > market_price + 0.03:
        return f'<b>{player_name}</b>'
    else:
        return player_name

def main():
    st.title("Upcoming Matches")
    st.sidebar.title("Filter Matches")
    selected_tour = str.lower(st.sidebar.selectbox("Tour", ['ATP', 'WTA']))
    atp_matches = get_upcoming_matches('atp')
    wta_matches = get_upcoming_matches('wta')
    atp_matches['Tour'] = 'ATP'
    wta_matches['Tour'] = 'WTA'
    all_matches = pd.concat([atp_matches, wta_matches], ignore_index=True)
    all_matches['tournament'] = all_matches['Tour ID'].apply(lambda x: tournament_id_to_name(tournament_id=x, tour=selected_tour))

    if all_matches.empty:
        st.write("No matches found")
        return

    tournaments = all_matches['tournament'].unique()
    selected_tournament = st.sidebar.selectbox("Tournaments", tournaments, key="tournament_selectbox")

    elo_models = {
        'atp': load_elo_model('elo_model_atp.pkl'),
        'wta': load_elo_model('elo_model_wta.pkl')
    }

    elo = elo_models[selected_tour]
    filtered_matches = all_matches[(all_matches['Tour'] == selected_tour.upper()) & (all_matches['tournament'] == selected_tournament)]
    filtered_predictions = predict_outcomes(filtered_matches, selected_tour, elo)

    if filtered_matches.empty:
        st.write("No matches found for the selected tournament")
        return

    st.write(f"Matches for {selected_tournament}")

    filtered_matches['P1 Market'] = 1 / filtered_matches['P1 Odds']
    filtered_matches['P2 Market'] = 1 / filtered_matches['P2 Odds']

    match_data = [
        {
            "Player 1": match['Player1'],
            "P1 Model Fair": round(filtered_predictions[i][match['Player1']], 2),
            'P1 Market': match['P1 Market'],
            "Player 2": match['Player2'],
            "P2 Model Fair": round(filtered_predictions[i][match['Player2']], 2),
            "P2 Market": match['P2 Market'],
        }
        for i, (_, match) in enumerate(filtered_matches.iterrows())
    ]

    match_df = pd.DataFrame(match_data)
    match_df['Player 1'] = match_df.apply(lambda row: format_player_name(row['Player 1'], row['P1 Model Fair'], row['P1 Market']), axis=1)
    match_df['Player 2'] = match_df.apply(lambda row: format_player_name(row['Player 2'], row['P2 Model Fair'], row['P2 Market']), axis=1)
    match_df_html = match_df.to_html(escape=False, index=False)
    st.markdown(match_df_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()