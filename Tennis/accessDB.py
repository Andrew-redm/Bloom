from sqlalchemy import create_engine, select, and_, alias, or_, Table, MetaData, not_
from sqlalchemy.exc import SQLAlchemyError
import os
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import pandas as pd
from models import metadata, games_atp, players_atp, tours_atp, stat_atp, ratings_atp, odds_atp, today_atp

db_path = os.environ.get('ONCOURT_DB_PATH')
db_password = os.environ.get('ONCOURT_DB_PASSWORD')
conn_str = f"access+pyodbc:///?odbc_connect=DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};PWD={db_password}"
engine = create_engine(conn_str)

def get_table(tour, table_name):
    if tour == 'atp':
        return Table(f'{table_name}_atp', metadata, autoload_with=engine)
    elif tour == 'wta':
        return Table(f'{table_name}_wta', metadata, autoload_with=engine)
    else:
        raise ValueError("Invalid tour specified")

def get_player_id(tour, player_name):
    try:
        players_table = get_table(tour, 'players')
        query = select(players_table.c.ID_P).where(players_table.c.NAME_P == player_name)
        
        with engine.connect() as connection:
            result = connection.execute(query)
            player_id = result.scalar()
            return player_id
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

get_player_id('wta', 'Serena Williams')

def get_matches_in_daterange(tour, start_date, end_date=None, singles_only=True):
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        games_table = get_table(tour, 'games')
        players_table = get_table(tour, 'players')
        tours_table = get_table(tour, 'tours')

        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            games_table.c.ID1_G,
            games_table.c.ID2_G,
            games_table.c.DATE_G,
            player1.c.NAME_P.label('player1_name'),
            player2.c.NAME_P.label('player2_name'),
            tours_table.c.NAME_T.label('tournament_name'),
            tours_table.c.ID_C_T.label('surface'),
            tours_table.c.RANK_T.label('tournament_rank')
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
            query = query.where(
                not_(player1.c.NAME_P.like('%/%'))
            )

        with engine.connect() as connection:
            result = connection.execute(query)
            matches = pd.DataFrame(result.fetchall(), columns=result.keys())
            matches['surface'] = matches['surface'].map({1: 'hard', 2: 'clay', 3: 'indoor hard', 4: 'carpet', 5: 'grass', 6: 'acrylic'})
        
            return matches
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None

def get_tournaments_in_daterange(tour, start_date, end_date=None):
    """
    Retrieves tournaments within a specified date range from the 'tours' table.

    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime, optional): Defaults to the day before the current date if not provided.
    """
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        tours_table = get_table(tour, 'tours')
        
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
        games_table = get_table(tour, 'games')
        players_table = get_table(tour, 'players')
        tours_table = get_table(tour, 'tours')

        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            games_table,
            tours_table.c.NAME_T.label('tournament_name'),
            tours_table.c.COUNTRY_T.label('tournament_country'),
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
        stat_table = get_table(tour, 'stat')
        
        query = select(stat_table).where(
            and_(
                stat_table.c.ID_T == tournament_id,
                or_(
                    and_(stat_table.c.ID1 == id1, stat_table.c.ID2 == id2),
                    and_(stat_table.c.ID1 == id2, stat_table.c.ID2 == id1)
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
    
def get_upcoming_matches(tour, remove_doubles=True):
    try:
        today_table = get_table(tour, 'today')
        players_table = get_table(tour, 'players')
        odds_table = get_table(tour, 'odds')
        tours_table = get_table(tour, 'tours')

        player1 = alias(players_table, name='player1')
        player2 = alias(players_table, name='player2')

        query = select(
            today_table,
            player1.c.NAME_P.label('Player1'),
            player2.c.NAME_P.label('Player2'),
            odds_table.c.K1.label('P1_Odds'),
            odds_table.c.K2.label('P2_Odds'),
            tours_table.c.ID_C_T.label('Surface'),
            tours_table.c.NAME_T.label('Tournament')
        ).select_from(
            today_table.join(player1, today_table.c.ID1 == player1.c.ID_P)
                       .join(player2, today_table.c.ID2 == player2.c.ID_P)
                       .outerjoin(odds_table, and_(
                           today_table.c.ID1 == odds_table.c.ID1_O,
                           today_table.c.ID2 == odds_table.c.ID2_O
                       ))
                       .join(tours_table, today_table.c.TOUR == tours_table.c.ID_T) 
        ).where(
            today_table.c.DATE_GAME >= datetime.now()
        ).order_by(
            (odds_table.c.K1 + odds_table.c.K2).desc()
        )

        with engine.connect() as connection:
            result = connection.execute(query)
            today = pd.DataFrame(result.fetchall(), columns=result.keys())
                
        if remove_doubles:
            today = today[~today['Player1'].str.contains('/') & ~today['Player2'].str.contains('/')]
        today['Surface'] = today['Surface'].map({1: 'hard', 2: 'clay', 3: 'indoor hard', 4: 'carpet', 5: 'grass', 6: 'acrylic'})
        today = today.drop_duplicates(subset=['ID1', 'ID2', 'DATE_GAME'], keep='first')
        
        return today
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None
    
