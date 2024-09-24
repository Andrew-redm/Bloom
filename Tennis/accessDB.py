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

def get_tournaments_in_daterange(start_date, end_date=None):
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)
    query = f'''
    SELECT *
    FROM tours_wta
    WHERE DATE_T BETWEEN #{start_date}# AND #{end_date.strftime('%Y-%m-%d')}#
    '''
    df = pd.read_sql(query, conn)
    df = change_column_names(df, replacements)
    return df

def get_matches_in_tournament(tournament_id):   
    query = f'''
    SELECT games_wta.*, tours_wta.NAME_T, tours_wta.ID_C_T
    FROM games_wta
    INNER JOIN tours_wta ON games_wta.ID_T_G = tours_wta.ID_T
    WHERE ID_T_G = {tournament_id}
    '''
    df = pd.read_sql(query, conn)
    df = change_column_names(df, replacements)
    return df


def get_match_stats(id1, id2, tournament_id):
    query = '''
    SELECT stat_wta.*
    FROM stat_wta
    WHERE ((ID1 = ? AND ID2 = ?) OR (ID1 = ? AND ID2 = ?)) AND ID_T = ?
    '''
    params = (int(id1), int(id2), int(id2), int(id1), int(tournament_id))
    df = pd.read_sql(query, conn, params=params)
    df = change_column_names(df, replacements)
    return df

def change_column_names(df, replacements):
    df = df.rename(columns=replacements)
    return df

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
    df = pd.read_sql(query, conn)
    df = change_column_names(df, replacements)
    return df

def get_player_match_result(player_name):
    query = f'''
    SELECT games_wta.*, tours_wta.NAME_T, tours_wta.ID_C_T
    FROM games_wta
    INNER JOIN tours_wta ON games_wta.ID_T_G = tours_wta.ID_T
    WHERE ID1_G = (SELECT ID_P FROM players_wta WHERE NAME_P = '{player_name}') OR ID2_G = (SELECT ID_P FROM players_wta WHERE NAME_P = '{player_name}')
    '''
    df = pd.read_sql(query, conn)
    df = change_column_names(df, replacements)
    return df

if not db_path or not db_password:
    raise ValueError("ONCOURT_DB_PATH or ONCOURT_DB_PASSWORD environment variable not set")

conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";PWD=" + db_password

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
except pyodbc.Error as e:
    print("Error connecting to the database:", e)


# example usage
# iga_odds = get_player_match_odds('Iga Swiatek')
# iga_results = get_player_match_result('Iga Swiatek')
# iga_combined = pd.merge(iga_results, iga_odds, right_on=['P1_ID', 'P2_ID', 'TOUR'], left_on=['ID Winner_G', 'ID Loser_G', 'Tour ID_G'], how='outer')
# this needs work
# query = "SELECT * FROM odds_wta WHERE ID1_O = (SELECT ID_P FROM players_wta WHERE NAME_P = 'Jelena Ostapenko') OR ID2_O = (SELECT ID_P FROM players_wta WHERE NAME_P = 'Jelena Ostapenko')"