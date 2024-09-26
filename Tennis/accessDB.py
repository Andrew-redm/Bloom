import os
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import csv

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')

def load_replacements(file_path):
    replacements = {}
    with open(file_path, mode='r') as infile:
        reader = csv.reader(infile)
        for rows in reader:
            key = rows[0]
            value = rows[1]
            replacements[key] = value
    return replacements

replacements = load_replacements('replacements.csv')

def player_id_to_name(player_id):
    query = f'''
    SELECT NAME_P
    FROM players_wta
    WHERE ID_P = {player_id}
    '''
    df = pd.read_sql(query, conn)
    return df['NAME_P'][0] if not df.empty else None

def player_name_to_id(player_name):
    query = f'''
    SELECT ID_P
    FROM players_wta
    WHERE NAME_P = '{player_name}'
    '''
    df = pd.read_sql(query, conn)
    return df['ID_P'][0] if not df.empty else None

def tournament_id_to_name(tournament_id):
    query = f'''
    SELECT NAME_T
    FROM tours_wta
    WHERE ID_T = {tournament_id}
    '''
    tourneyName = pd.read_sql(query, conn)
    return tourneyName['NAME_T'][0] if not tourneyName.empty else None

def change_column_names(df, replacements):
    df = df.rename(columns=replacements)
    return df

def get_tournaments_in_daterange(start_date, end_date=None):
    """
    Retrieves tournaments within a specified date range from the 'tours_wta' table.

    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime, optional): The end date of the range. Defaults to the day before the current date if not provided.
    """
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)
    query = f'''
    SELECT *
    FROM tours_wta
    WHERE DATE_T BETWEEN #{start_date}# AND #{end_date.strftime('%Y-%m-%d')}#
    '''
    tournaments = pd.read_sql(query, conn)
    tournaments = change_column_names(tournaments, replacements)
    return tournaments

def get_matches_in_tournament(tournament_ids, singlesOnly=True):
    """
    Retrieves matches from the 'games_wta' table for the given list of tournament IDs.

    Args:
        tournament_ids (list of int): List of tournament IDs.
    """
    tournament_ids_str = ', '.join(map(str, tournament_ids))
    query = f'''
    SELECT games_wta.*, tours_wta.NAME_T, tours_wta.ID_C_T
    FROM games_wta
    INNER JOIN tours_wta ON games_wta.ID_T_G = tours_wta.ID_T
    WHERE ID_T_G IN ({tournament_ids_str})
    '''
    matches = pd.read_sql(query, conn)
    matches = change_column_names(matches, replacements)
    matches['winnerName'] = matches['ID Winner_G'].apply(player_id_to_name)
    matches['loserName'] = matches['ID Loser_G'].apply(player_id_to_name)
    if singlesOnly:
        matches = matches[~matches['winnerName'].str.contains('/') & ~matches['loserName'].str.contains('/')]
    return matches

def get_match_stats(id1, id2, tournament_id):
    query = '''
    SELECT stat_wta.*
    FROM stat_wta
    WHERE ((ID1 = ? AND ID2 = ?) OR (ID1 = ? AND ID2 = ?)) AND ID_T = ?
    '''
    params = (int(id1), int(id2), int(id2), int(id1), int(tournament_id))
    stats = pd.read_sql(query, conn, params=params)
    stats = change_column_names(stats, replacements)
    return stats

def get_top_100():
    top100WTA = '''
                SELECT TOP 100 ratings_wta.ID_P_R, players_wta.NAME_P, ratings_wta.POS_R, ratings_wta.DATE_R
                FROM ratings_wta
                INNER JOIN players_wta ON ratings_wta.ID_P_R = players_wta.ID_P
                WHERE ratings_wta.POS_R < 101 AND ratings_wta.DATE_R = (SELECT MAX(DATE_R) FROM ratings_wta)
                ORDER BY ratings_wta.POS_R ASC'''
    top_100 = change_column_names(pd.read_sql(top100WTA, conn), replacements)
    return top_100

#this should really take a player pair and tournament id to return prices for one match only
def get_player_match_odds(player_name):
    query = f'''
    SELECT odds_wta.*, players_wta.NAME_P
    FROM odds_wta
    INNER JOIN players_wta ON (odds_wta.ID1_O = players_wta.ID_P OR odds_wta.ID2_O = players_wta.ID_P)
    WHERE players_wta.NAME_P = '{player_name}'
    '''
    prices = pd.read_sql(query, conn)
    prices = change_column_names(prices, replacements)
    return prices

def get_todays_matches():
    query = '''
    SELECT *
    FROM today_wta
    WHERE today_wta.DATE_GAME >= NOW()
    '''
    today = pd.read_sql(query, conn)
    return today

def get_player_match_result(player_name):
    query = f'''
    SELECT games_wta.*, tours_wta.NAME_T, tours_wta.ID_C_T
    FROM games_wta
    INNER JOIN tours_wta ON games_wta.ID_T_G = tours_wta.ID_T
    WHERE ID1_G = (SELECT ID_P FROM players_wta WHERE NAME_P = '{player_name}') OR ID2_G = (SELECT ID_P FROM players_wta WHERE NAME_P = '{player_name}')
    '''
    results = pd.read_sql(query, conn)
    results = change_column_names(results, replacements)
    return results

if not db_path or not db_password:
    raise ValueError("ONCOURT_DB_PATH or ONCOURT_DB_PASSWORD environment variable not set")

conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";PWD=" + db_password

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
except pyodbc.Error as e:
    print("Error connecting to the database:", e)