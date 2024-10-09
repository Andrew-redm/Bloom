from sqlalchemy import create_engine, inspect
import os

def print_column_names(engine, table_name):
    inspector = inspect(engine)
    
    columns = inspector.get_columns(table_name)
    print(f"Columns in table '{table_name}':")
    for column in columns:
        print(column['name'])

if __name__ == "__main__":
    db_path = os.environ.get('ONCOURT_DB_PATH')
    db_password = os.environ.get('ONCOURT_DB_PASSWORD')
    conn_str = f"access+pyodbc:///?odbc_connect=DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};PWD={db_password}"
    
    engine = create_engine(conn_str)

    print_column_names(engine, 'today_atp')

def print_table_names(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in the database:")
    for table in tables:
        print(table)

print_table_names(engine)