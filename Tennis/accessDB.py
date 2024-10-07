from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float, select, and_, alias
from sqlalchemy.exc import SQLAlchemyError
import os
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import pandas as pd

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')

encoded_password = quote_plus(db_password)

conn_str = f"access+pyodbc:///?odbc_connect=DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};PWD={encoded_password}"

print(f"Connection String: {conn_str}")

engine = create_engine(conn_str)
metadata = MetaData()

#what a mess
games_atp = Table('games_atp', metadata,
    Column('ID1_G', Integer),
    Column('ID2_G', Integer),
    Column('ID_T_G', Integer),
    Column('ID_R_G', Integer),
    Column('RESULT_G', String),
    Column('DATE_G', DateTime),
)

players_atp = Table('players_atp', metadata,
    Column('ID_P', Integer, primary_key=True),
    Column('NAME_P', String),
    Column('DATE_P', DateTime),
    Column('COUNTRY_P', String),
    Column('RANK_P', Integer),
    Column('PROGRESS_P', Integer),
    Column('POINT_P', Integer),
    Column('HARDPOINT_P', Integer),
    Column('HARDTOUR_P', Integer),
    Column('CLAYPOINT_P', Integer),
    Column('CLAYTOUR_P', Integer),
    Column('GRASSPOINT_P', Integer),
    Column('GRASSTOUR_P', Integer),
    Column('CARPETPOINT_P', Integer),
    Column('CARPETTOUR_P', Integer),
    Column('PRIZE_P', Float),
    Column('CH_P', Integer),
    Column('DR_P', Integer),
    Column('DP_P', Integer),
    Column('DO_P', Integer),
    Column('IHARDPOINT_P', Integer),
    Column('IHARDTOUR_P', Integer),
    Column('ITF_ID', String),
)

tours_atp = Table('tours_atp', metadata,
    Column('ID_T', Integer, primary_key=True),
    Column('NAME_T', String),
    Column('ID_C_T', Integer),
    Column('DATE_T', DateTime),
    Column('RANK_T', Integer),
    Column('LINK_T', String),
    Column('COUNTRY_T', String),
    Column('PRIZE_T', Float),
    Column('RATING_T', Integer),
    Column('URL_T', String),
    Column('LATITUDE_T', Float),
    Column('LONGITUDE_T', Float),
    Column('SITE_T', String),
    Column('RACE_T', String),
    Column('ENTRY_T', String),
    Column('SINGLES_T', Integer),
    Column('DOUBLES_T', Integer),
    Column('TIER_T', String),
    Column('RESERVE_INT_T', Integer),
    Column('RESERVE_CHAR_T', String),
    Column('LIVE_T', Integer),
    Column('RESULT_T', String),
)

try:
    with engine.connect() as connection:
        query = select(
            games_atp.c.ID1_G,
            games_atp.c.ID2_G,
            games_atp.c.RESULT_G,
            games_atp.c.DATE_G,
            players_atp.c.NAME_P.label('Player1_Name'),
            players_atp.c.COUNTRY_P.label('Player1_Country'),
            tours_atp.c.NAME_T.label('Tournament_Name'),
            tours_atp.c.COUNTRY_T.label('Tournament_Country')
        ).select_from(
            games_atp.join(players_atp, games_atp.c.ID1_G == players_atp.c.ID_P)
                     .join(tours_atp, games_atp.c.ID_T_G == tours_atp.c.ID_T)
        ).limit(10)  
        result = connection.execute(query)
        for row in result:
            print(row)
    print("Success")
except SQLAlchemyError as e:
    print(f"Holy moses: {e}")

def get_player_id(tour, player_name):
    try:
        players_table = Table(f'players_{tour}', metadata, autoload_with=engine)
        query = select(players_table.c.ID_P).where(players_table.c.NAME_P == player_name)
        
        with engine.connect() as connection:
            result = connection.execute(query)
            player_id = result.scalar()
            return player_id
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

def get_matches_in_daterange(tour, start_date, end_date=None, singles_only=True):
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        games_table = Table(f'games_{tour}', metadata, autoload_with=engine)
        players_table = Table(f'players_{tour}', metadata, autoload_with=engine)
        tours_table = Table(f'tours_{tour}', metadata, autoload_with=engine)

        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            games_table.c.ID1_G,
            games_table.c.DATE_G,
            player1.c.NAME_P.label('player1_name'),
            player2.c.NAME_P.label('player2_name'),
            tours_table.c.NAME_T.label('tournament_name')
        ).select_from(
            games_table.join(player1, games_table.c.ID1_G == player1.c.ID_P)
                       .join(player2, games_table.c.ID2_G == player2.c.ID_P)
                       .join(tours_table, games_table.c.ID_T_G == tours_table.c.ID_T)
        ).where(
            and_(
                games_table.c.DATE_G >= start_date_str,
                games_table.c.DATE_G <= end_date_str
            )
        )

        if singles_only:
            query = query.where(games_table.c.ID_R_G == 1)  # Assuming 1 indicates singles matches

        with engine.connect() as connection:
            result = connection.execute(query)
            matches = pd.DataFrame(result.fetchall(), columns=result.keys())
            return matches
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

matches = get_matches_in_daterange('atp', datetime(2021, 1, 1), datetime(2021, 1, 31))
print(matches)

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
    p1_odds = []
    p2_odds = []
    for _, match in today.iterrows():
        odds = get_match_odds(tour, match['P1_ID'], match['P2_ID'], match['Tour ID'])
        if not odds.empty:
            p1_odds.append(odds['K1'].values[0])
            p2_odds.append(odds['K2'].values[0])
        else:
            p1_odds.append(None)
            p2_odds.append(None)
    today['P1 Odds'] = p1_odds
    today['P2 Odds'] = p2_odds
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