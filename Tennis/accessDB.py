import os
import pyodbc
import numpy as np

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')

if not db_path or not db_password:
    raise ValueError("ONCOURT_DB_PATH or ONCOURT_DB_PASSWORD environment variable not set")

conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + db_path + ";PWD=" + db_password

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = "SELECT * FROM odds_wta WHERE ID1_O = (SELECT ID_P FROM players_wta WHERE NAME_P = 'Jelena Ostapenko') OR ID2_O = (SELECT ID_P FROM players_wta WHERE NAME_P = 'Jelena Ostapenko')"
    top100WTA = '''
                    SELECT TOP 100 ratings_wta.ID_P_R, players_wta.NAME_P, ratings_wta.POS_R, ratings_wta.DATE_R
                    FROM ratings_wta
                    INNER JOIN players_wta ON ratings_wta.ID_P_R = players_wta.ID_P
                    WHERE ratings_wta.POS_R < 101 AND ratings_wta.DATE_R = (SELECT MAX(DATE_R) FROM ratings_wta)
                    ORDER BY ratings_wta.POS_R ASC'''
    result = cursor.execute(query)
except pyodbc.Error as e:
    print("Error connecting to the database:", e)


#make pandas df of the result
import pandas as pd
df = pd.read_sql(query, conn)
column_names = df.columns.to_list()
column_names

top_100 = pd.read_sql(top100WTA, conn)
top_100.head()


help(pyodbc)
def change_column_names(df, replacements):
    df = df.rename(columns=replacements)
    return df

replacements = {
    'ID1_O': 'Player 1 ID',
    'ID2_O': 'Player 2 ID',
    'NAME_P': 'Player Name',
    'ID_P': 'Player ID',
    'NAME_P': 'Name_P',
    'DATE_P': 'Birthdate_P',
    'COUNTRY_P': 'Country_P',
    'PRIZE_P': 'Prize money_P',
    'DR_P': 'Doubles Ranking_P',
    'DP_P': 'Doubles Ranking Progress_P',
    'DO_P': 'Doubles Ranking Points_P',
    'ID_T': 'Tour ID_T',
    'NAME_T': 'Tour Name_T',
    'ID_C_T': 'Surface ID_T',
    'DATE_T': 'Start Date_T',
    'RANK_T': 'Tour Rank_T',
    'LINK_T': 'Previous Tournament ID',
    'COUNTRY_T': 'Country_T',
    'PRIZE_T': 'Prize Money_T',
    'RATING_T': 'Ranking Points_T',
    'URL_T': 'Site_T',
    'LATITUDE_T': 'Latitude_T',
    'LONGITUDE_T': 'Longitude_T',
    'SINGLES_T': 'Pts By Round S_T',
    'DOUBLES_T': 'Pts By Round S_T',
    'ID1_G': 'ID Winner_G',
    'ID2_G': 'ID Loser_G',
    'ID_T_G': 'Tour ID_G',
    'ID_R_G': 'Round_G',
    'RESULT_G': 'Result_Gt',
    'DATE_G': 'Date_G',
    'TOUR': 'Tour ID',
    'DATE_GAME': 'NOT USED',
    'ID1': 'P1_ID',
    'ID2': 'P2_ID',
    'ROUND': 'Round',
    'DRAW': 'match in draw',
    'RESULT': 'Result',
    'ID_P_S': 'Player ID_S',
    'ID_T_S': 'Tour ID_S',
    'SEEDING': 'Seed',
    'DATE_R': 'Date',
    'ID_P_R': 'Player ID_R',
    'POINT_R': 'Ranking Points_R',
    'POS_R': 'Rank_R',
    'ID_B_O': 'Boomaker ID',
    'ID1_O': 'P1_ID',
    'ID2_O': 'P2_ID',
    'ID_T_O': 'TOUR',
    'ID_R_O': 'ROUND',
    'K1': 'P1 Price',
    'K2': 'P2 Price',
    'TOTAL': 'Total',
    'KTM': 'Under',
    'KTB': 'Over',
    'F1': 'P1 HC',
    'F2': 'P2 HC',
    'KF1': 'P1 HC Price',
    'KF2': 'P2 HC Price',
    'K20': '2-0',
    'K21': '2-1',
    'K12': '1-2',
    'K02': '0-2',
    'K30': '3-0',
    'K31': '3-1',
    'K32': '3-2',
    'K23': '2-3',
    'K13': '1-3',
    'K03': '0-3',
    'ID_T': 'Tour_ID',
    'ID_R': 'Round',
    'FS_1': '1st Serve Pts',
    'FSOF_1': 'first serve of',
    'ACES_1': 'Aces',
    'DF_1': 'Double Faults',
    'UE_1': 'Unforced Errors',
    'W1S_1': 'First Serve Win',
    'W1SOF_1': 'winning on first serve of',
    'W2S_1': 'Second Serve Win',
    'W2SOF_1': 'winning on second serve of',
    'WIS_1': 'Winners',
    'BP_1': 'Break Points',
    'BPOF_1' : 'break points of',
    'NA_1': 'Net Approaches',
    'NAOF_1': 'net approaches of',
    'TPW_1': 'Total Points Won',
    'FAST_1': 'Fastest Serve',
    'A1S_1': 'Average First Serve',
    'A2S_1': 'Average Second Serve',
    'RPW_1': 'Receiving Points Won',
    'RPWOF_1': 'receiving points won of'
}

df = change_column_names(df, replacements)
df.head()
df.isnull().sum()
top_100 = change_column_names(top_100, replacements)
top_100.head()

def get_top_100():
    return top_100



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

iga_odds = get_player_match_odds('Iga Swiatek')
iga_results = get_player_match_result('Iga Swiatek')

iga_odds.columns
iga_results.columns
iga_combined = pd.merge(iga_results, iga_odds, right_on=['P1_ID', 'P2_ID', 'TOUR'], left_on=['ID Winner_G', 'ID Loser_G', 'Tour ID_G'], how='outer')

iga_combined.to_csv('iga_combined.csv', index=False)