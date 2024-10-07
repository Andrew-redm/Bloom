from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float, select, and_, alias
from sqlalchemy.exc import SQLAlchemyError
import os
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import pandas as pd
from pydantic import BaseModel

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')

encoded_password = quote_plus(db_password)

conn_str = f"access+pyodbc:///?odbc_connect=DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};PWD={encoded_password}"

engine = create_engine(conn_str)
metadata = MetaData()

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
    Column('PRIZE_P', String),
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
    Column('PRIZE_T', String),
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

stat_atp = Table('stat_atp', metadata,
    Column('ID1', Integer),
    Column('ID2', Integer),
    Column('ID_T', Integer),
    Column('ID_R', Integer),
    Column('FS_1', Integer),
    Column('FSOF_1', Integer),
    Column('ACES_1', Integer),
    Column('DF_1', Integer),
    Column('UE_1', Integer),
    Column('W1S_1', Integer),
    Column('W1SOF_1', Integer),
    Column('W2S_1', Integer),
    Column('W2SOF_1', Integer),
    Column('WIS_1', Integer),
    Column('BP_1', Integer),
    Column('BPOF_1', Integer),
    Column('NA_1', Integer),
    Column('NAOF_1', Integer),
    Column('TPW_1', Integer),
    Column('FAST_1', Integer),
    Column('A1S_1', Integer),
    Column('A2S_1', Integer),
    Column('FS_2', Integer),
    Column('FSOF_2', Integer),
    Column('ACES_2', Integer),
    Column('DF_2', Integer),
    Column('UE_2', Integer),
    Column('W1S_2', Integer),
    Column('W1SOF_2', Integer),
    Column('W2S_2', Integer),
    Column('W2SOF_2', Integer),
    Column('WIS_2', Integer),
    Column('BP_2', Integer),
    Column('BPOF_2', Integer),
    Column('NA_2', Integer),
    Column('NAOF_2', Integer),
    Column('TPW_2', Integer),
    Column('FAST_2', Integer),
    Column('A1S_2', Integer),
    Column('A2S_2', Integer),
    Column('RPW_1', Integer),
    Column('RPWOF_1', Integer),
    Column('RPW_2', Integer),
    Column('RPWOF_2', Integer),
    Column('MT', Integer),
)

odds_atp = Table('odds_atp', metadata,
    Column('ID_B_O', Integer),
    Column('ID1_O', Integer),
    Column('ID2_O', Integer),
    Column('ID_T_O', Integer),
    Column('ID_R_O', Integer),
    Column('K1', Float),
    Column('K2', Float),
    Column('TOTAL', Float),
    Column('KTM', Float),
    Column('KTB', Float),
    Column('F1', Float),
    Column('F2', Float),
    Column('KF1', Float),
    Column('KF2', Float),
    Column('K20', Float),
    Column('K21', Float),
    Column('K12', Float),
    Column('K02', Float),
    Column('K30', Float),
    Column('K31', Float),
    Column('K32', Float),
    Column('K23', Float),
    Column('K13', Float),
    Column('K03', Float),
)

today_atp = Table('today_atp', metadata,
    Column('TOUR', String),
    Column('DATE_GAME', DateTime),
    Column('ID1', Integer),
    Column('ID2', Integer),
    Column('ROUND', String),
    Column('DRAW', String),
    Column('RESULT', String),
    Column('COMPLETE', String),
    Column('LIVE', String),
    Column('TIME_GAME', DateTime),
    Column('RESERVE_INT', Integer),
    Column('RESERVE_CHAR', String),
)



# Define Pydantic models
class Player(BaseModel):
    ID_P: int
    NAME_P: str
    DATE_P: datetime
    COUNTRY_P: str
    RANK_P: int
    PROGRESS_P: int
    POINT_P: int
    HARDPOINT_P: int
    HARDTOUR_P: int
    CLAYPOINT_P: int
    CLAYTOUR_P: int
    GRASSPOINT_P: int
    GRASSTOUR_P: int
    CARPETPOINT_P: int
    CARPETTOUR_P: int
    PRIZE_P: str
    CH_P: int
    DR_P: int
    DP_P: int
    DO_P: int
    IHARDPOINT_P: int
    IHARDTOUR_P: int
    ITF_ID: str

class Game(BaseModel):
    ID1_G: int
    ID2_G: int
    ID_T_G: int
    ID_R_G: int
    RESULT_G: str
    DATE_G: datetime

class Tournament(BaseModel):
    ID_T: int
    NAME_T: str
    ID_C_T: int
    DATE_T: datetime
    RANK_T: int
    LINK_T: str
    COUNTRY_T: str
    PRIZE_T: str
    RATING_T: int
    URL_T: str
    LATITUDE_T: float
    LONGITUDE_T: float
    SITE_T: str
    RACE_T: str
    ENTRY_T: str
    SINGLES_T: int
    DOUBLES_T: int
    TIER_T: str
    RESERVE_INT_T: int
    RESERVE_CHAR_T: str
    LIVE_T: int
    RESULT_T: str

class today(BaseModel):
    TOUR: str
    DATE_GAME: datetime
    ID1: int
    ID2: int
    ROUND: str
    DRAW: str
    RESULT: str
    COMPLETE: str
    LIVE: str
    TIME_GAME: datetime
    RESERVE_INT: int
    RESERVE_CHAR: str

class Stat(BaseModel):
    ID1: int
    ID2: int
    ID_T: int
    ID_R: int
    FS_1: int
    FSOF_1: int
    ACES_1: int
    DF_1: int
    UE_1: int
    W1S_1: int
    W1SOF_1: int
    W2S_1: int
    W2SOF_1: int
    WIS_1: int
    BP_1: int
    BPOF_1: int
    NA_1: int
    NAOF_1: int
    TPW_1: int
    FAST_1: int
    A1S_1: int
    A2S_1: int
    FS_2: int
    FSOF_2: int
    ACES_2: int
    DF_2: int
    UE_2: int
    W1S_2: int
    W1SOF_2: int
    W2S_2: int
    W2SOF_2: int
    WIS_2: int
    BP_2: int
    BPOF_2: int
    NA_2: int
    NAOF_2: int
    TPW_2: int
    FAST_2: int
    A1S_2: int
    A2S_2: int
    RPW_1: int
    RPWOF_1: int
    RPW_2: int
    RPWOF_2: int
    MT: int

ratings_atp = Table('ratings_atp', metadata,
    Column('DATE_R', DateTime),
    Column('ID_P_R', Integer),
    Column('POINT_R', Integer),
    Column('POS_R', Integer),
)

class Rating(BaseModel):
    DATE_R: datetime
    ID_P_R: int
    POINT_R: int
    POS_R: int

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
            games_table.c.ID2_G,
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
            query = query.where(games_table.c.ID_R_G == 1) 

        with engine.connect() as connection:
            result = connection.execute(query)
            matches = pd.DataFrame(result.fetchall(), columns=result.keys())
            return matches
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

def get_tournaments_in_daterange(tour, start_date, end_date=None):
    """
    Retrieves tournaments within a specified date range from the 'tours_wta' table.

    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime, optional): The end date of the range. Defaults to the day before the current date if not provided.
    """
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        tours_table = Table(f'tours_{tour}', metadata, autoload_with=engine)

        query = select(tours_table).where(
            and_(
                tours_table.c.DATE_T >= start_date_str,
                tours_table.c.DATE_T <= end_date_str
            )
        )

        with engine.connect() as connection:
            result = connection.execute(query)
            tournaments = pd.DataFrame(result.fetchall(), columns=result.keys())
            return tournaments
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

def get_matches_in_tournament(tour, tournament_ids, singlesOnly=True):
    try:
        games_table = Table(f'games_{tour}', metadata, autoload_with=engine)
        tours_table = Table(f'tours_{tour}', metadata, autoload_with=engine)
        players_table = Table(f'players_{tour}', metadata, autoload_with=engine)

        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            games_table,
            tours_table.c.NAME_T.label('tournament_name'),
            tours_table.c.ID_C_T.label('tournament_country'),
            player1.c.NAME_P.label('winnerName'),
            player2.c.NAME_P.label('loserName')
        ).select_from(
            games_table.join(tours_table, games_table.c.ID_T_G == tours_table.c.ID_T)
                       .join(player1, games_table.c.ID1_G == player1.c.ID_P)
                       .join(player2, games_table.c.ID2_G == player2.c.ID_P)
        ).where(
            games_table.c.ID_T_G.in_(tournament_ids)
        )

        with engine.connect() as connection:
            result = connection.execute(query)
            matches = pd.DataFrame(result.fetchall(), columns=result.keys())

            if singlesOnly:
                matches = matches[~matches['winnerName'].str.contains('/') & ~matches['loserName'].str.contains('/')]

            return matches
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

def get_match_stats(tour, id1, id2, tournament_id):
    try:
        stats_table = Table(f'stat_{tour}', metadata, autoload_with=engine)
        
        query = select(stats_table).where(
            and_(
                stats_table.c.ID_T == tournament_id,
                or_(
                    and_(stats_table.c.ID1 == id1, stats_table.c.ID2 == id2),
                    and_(stats_table.c.ID1 == id2, stats_table.c.ID2 == id1)
                )
            )
        )
        
        with engine.connect() as connection:
            result = connection.execute(query)
            stats = pd.DataFrame(result.fetchall(), columns=result.keys())
            return stats
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None
      
def get_match_odds(tour, P1ID, P2ID, tournament_id):
    try:
        odds_table = Table(f'odds_{tour}', metadata, autoload_with=engine)
        
        query = select(odds_table).where(
            and_(
                odds_table.c.ID1_O == P1ID,
                odds_table.c.ID2_O == P2ID,
                odds_table.c.ID_T_O == tournament_id
            )
        )
        
        with engine.connect() as connection:
            result = connection.execute(query)
            odds = pd.DataFrame(result.fetchall(), columns=result.keys())
            return odds
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None


def get_upcoming_matches(tour, remove_doubles=True):
    try:
        today_table = Table(f'today_{tour}', metadata, autoload_with=engine)
        players_table = Table(f'players_{tour}', metadata, autoload_with=engine)
        odds_table = Table(f'odds_{tour}', metadata, autoload_with=engine)
        
        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            today_table,
            player1.c.NAME_P.label('Player1'),
            player2.c.NAME_P.label('Player2'),
            odds_table.c.K1.label('P1_Odds'),
            odds_table.c.K2.label('P2_Odds')
        ).select_from(
            today_table.join(player1, today_table.c.ID1 == player1.c.ID_P)
                       .join(player2, today_table.c.ID2 == player2.c.ID_P)
                       .outerjoin(odds_table, and_(
                           today_table.c.ID1 == odds_table.c.ID1_O,
                           today_table.c.ID2 == odds_table.c.ID2_O
                       ))
        ).where(
            today_table.c.DATE_GAME >= datetime.now()
        )

        with engine.connect() as connection:
            result = connection.execute(query)
            today = pd.DataFrame(result.fetchall(), columns=result.keys())
                
        if remove_doubles:
            today = today[~today['Player1'].str.contains('/') & ~today['Player2'].str.contains('/')]

        return today
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None
    
get_upcoming_matches('atp')

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