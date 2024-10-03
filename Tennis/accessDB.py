import os
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import csv

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')

if not db_path or not db_password:
    raise ValueError("ONCOURT_DB_PATH or ONCOURT_DB_PASSWORD environment variable not set")

conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";PWD=" + db_password

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
except pyodbc.Error as e:
    print("Error connecting to the database:", e)

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

def player_id_to_name(tour, player_id):
    query = f'''
    SELECT NAME_P
    FROM players_{tour}
    WHERE ID_P = {player_id}
    '''
    df = pd.read_sql(query, conn)
    return df['NAME_P'][0] if not df.empty else None

def player_name_to_id(tour, player_name):
    query = f'''
        SELECT ID_P
        FROM players_{tour}
        WHERE NAME_P = '{player_name.replace("'", "''")}'
    '''
    df = pd.read_sql(query, conn)
    return df['ID_P'][0] if not df.empty else None

def tournament_id_to_name(tour, tournament_id):
    #this is gross. tour means WTA/ATP but in db it means tournament
    query = f'''
    SELECT NAME_T
    FROM tours_{tour}
    WHERE ID_T = {tournament_id}
    '''
    tourneyName = pd.read_sql(query, conn)
    return tourneyName['NAME_T'][0] if not tourneyName.empty else None

def change_column_names(df, replacements):
    df = df.rename(columns=replacements)
    return df

def tournament_id_to_surface(tour, tournament_id):
    query = f'''
    SELECT ID_C_T
    FROM tours_{tour}
    WHERE ID_T = {tournament_id}
    '''
    surfacevalue = pd.read_sql(query, conn)
    surfacevalue = int(surfacevalue['ID_C_T'][0])
    surface = {1: 'hard', 2: 'clay', 3: 'indoor hard', 4:'carpet', 5: 'grass', 6: 'acrylic'}
    return surface.get(surfacevalue, None)

tournament_id_to_surface('wta', 430)

def get_matches_in_daterange(tour, start_date, end_date=None, singlesOnly=True):
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)
    query = f'''
    SELECT *
    FROM games_{tour}
    WHERE DATE_G BETWEEN #{start_date}# AND #{end_date.strftime('%Y-%m-%d')}#
    '''
    matches = pd.read_sql(query, conn)
    matches = change_column_names(matches, replacements)
    matches['winnerName'] = matches['ID Winner_G'].apply(lambda player_id: player_id_to_name(tour, player_id))
    matches['loserName'] = matches['ID Loser_G'].apply(lambda player_id: player_id_to_name(tour, player_id))
    matches['surface'] = matches['Tour ID_G'].apply(lambda x: tournament_id_to_surface(tour, x))
    if singlesOnly:
        matches = matches[~matches['winnerName'].str.contains('/') & ~matches['loserName'].str.contains('/')]
    return matches

def get_tournaments_in_daterange(tour, start_date, end_date=None):
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
    FROM tours_{tour}
    WHERE DATE_T BETWEEN #{start_date}# AND #{end_date.strftime('%Y-%m-%d')}#
    '''
    tournaments = pd.read_sql(query, conn)
    tournaments = change_column_names(tournaments, replacements)
    return tournaments

def get_matches_in_tournament(tour, tournament_ids, singlesOnly=True):
    tournament_ids_str = ', '.join(map(str, tournament_ids))
    query = f'''
    SELECT games_{tour}.*, tours_{tour}.NAME_T, tours_{tour}.ID_C_T
    FROM games_{tour}
    INNER JOIN tours_{tour} ON games_{tour}.ID_T_G = tours_{tour}.ID_T
    WHERE ID_T_G IN ({tournament_ids_str})
    '''
    matches = pd.read_sql(query, conn)
    matches = change_column_names(matches, replacements)
    matches['winnerName'] = matches['ID Winner_G'].apply(lambda player_id: player_id_to_name(tour, player_id))
    matches['loserName'] = matches['ID Loser_G'].apply(lambda player_id: player_id_to_name(tour, player_id))
    if singlesOnly:
        matches = matches[~matches['winnerName'].str.contains('/') & ~matches['loserName'].str.contains('/')]
    return matches

def get_match_stats(tour, id1, id2, tournament_id):
    query = f'''
    SELECT stat_{tour}.*
    FROM stat_{tour}
    WHERE ((ID1 = ? AND ID2 = ?) OR (ID1 = ? AND ID2 = ?)) AND ID_T = ?
    '''
    params = (int(id1), int(id2), int(id2), int(id1), int(tournament_id))
    stats = pd.read_sql(query, conn, params=params)
    stats = change_column_names(stats, replacements)
    return stats

#dont think i have ever actually used this
def get_top_100():
    top100WTA = '''
    SELECT TOP 100 ratings_wta.ID_P_R, players_wta.NAME_P, ratings_wta.POS_R, ratings_wta.DATE_R
    FROM ratings_wta
    INNER JOIN players_wta ON ratings_wta.ID_P_R = players_wta.ID_P
    WHERE ratings_wta.POS_R < 101 AND ratings_wta.DATE_R = (SELECT MAX(DATE_R) FROM ratings_wta)
    ORDER BY ratings_wta.POS_R ASC'''

    top_100 = pd.read_sql(top100WTA, conn)
    return top_100

def get_match_odds(tour, P1ID, P2ID, tournament_id):
    query = f"""
    SELECT *
    FROM odds_{tour}
    WHERE ID1_O = ? AND ID2_O = ? AND ID_T_O = ?
    """
    prices = pd.read_sql(query, conn, params=[P1ID, P2ID, tournament_id])
    # prices = change_column_names(prices, replacements)
    return prices

def get_upcoming_matches(tour, remove_doubles=True):
    query = f'''
    SELECT *
    FROM today_{tour}
    WHERE today_{tour}.DATE_GAME >= NOW()
    '''
    today = pd.read_sql(query, conn)
    today['Player1'] = today['ID1'].apply(lambda player_id: player_id_to_name(tour, player_id))
    today['Player2'] = today['ID2'].apply(lambda player_id: player_id_to_name(tour, player_id))
    today = change_column_names(today, replacements)
    if remove_doubles:
        today = today[~today['Player1'].str.contains('/') & ~today['Player2'].str.contains('/')]
    return today

def get_player_match_result(tour, player_name):
    query = f'''
    SELECT games_{tour}.*, tours_{tour}.NAME_T, tours_{tour}.ID_C_T
    FROM games_{tour}
    INNER JOIN tours_{tour} ON games_{tour}.ID_T_G = tours_{tour}.ID_T
    WHERE ID1_G = (SELECT ID_P FROM players_{tour} WHERE NAME_P = '{player_name}') OR ID2_G = (SELECT ID_P FROM players_{tour} WHERE NAME_P = '{player_name}')
    '''
    results = pd.read_sql(query, conn)
    results = change_column_names(results, replacements)
    return results

def get_matches_in_tournament(tour, tournament_ids, singlesOnly=True):
    tournament_ids_str = ', '.join(map(str, tournament_ids))
    query = f'''
    SELECT games_{tour}.*, tours_{tour}.NAME_T, tours_{tour}.ID_C_T
    FROM games_{tour}
    INNER JOIN tours_{tour} ON games_{tour}.ID_T_G = tours_{tour}.ID_T
    WHERE ID_T_G IN ({tournament_ids_str})
    '''
    matches = pd.read_sql(query, conn)
    matches = change_column_names(matches, replacements)
    matches['winnerName'] = matches['ID Winner_G'].apply(player_id_to_name)
    matches['loserName'] = matches['ID Loser_G'].apply(player_id_to_name)
    if singlesOnly:
        matches = matches[~matches['winnerName'].str.contains('/') & ~matches['loserName'].str.contains('/')]
    return matches

