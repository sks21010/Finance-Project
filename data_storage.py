import psycopg2
import yfinance as yf
import numpy as np
import pandas as pd
from psycopg2.extensions import register_adapter, AsIs



# registering a type adapter for np.int64 to ensure that pscycopg2 can handle numpy data types
# AsIs adapter ensures that numpy's int64 data type is passed to SQL
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
psycopg2.extensions.register_adapter(np.float64, psycopg2._psycopg.AsIs)

excel_tickers_filepath = r"C:\Users\iamsk\sks_Python\Financial Data Storage Project\Yahoo Ticker Symbols - September 2017.xlsx"
tickers_df = pd.read_excel(excel_tickers_filepath, header=3, usecols=[0,1,2,3,4])
tickers = tickers_df['Ticker'].tolist() 

usa_tickers = set()
for index, row in tickers_df.iterrows():
    if row["Country"] == "USA":
        usa_tickers.add(row["Ticker"])


# Database connection parameters
dbname = 'stocks'
user = 'postgres'
password = 'Narik123'
host = '127.0.0.1'
port = '5432'


# Check if database exists
def database_exists(dbname, user, password, host, port):
    conn = psycopg2.connect(
        database=dbname, user=user, password=password, host=host, port=port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'") # Returns 1 if condition is met (database exists)
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# creating the database
if not database_exists(dbname, user, password, host, port):
    conn = psycopg2.connect(
        database=dbname, user=user, password=password, host=host, port=port
    )
    conn.autocommit = True
    cursor = conn.cursor() # handler to execute SQL commands
    cursor.execute(f"CREATE DATABASE {dbname};")
    print("Database created successfully!")
    conn.close()

# creating tables in the database

conn = psycopg2.connect(
    database=dbname, user=user, password=password, host=host, port=port
)
conn.autocommit = True
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS prices
               (
                Date DATE NOT NULL,
                Open FLOAT NOT NULL,
                High FLOAT NOT NULL,
                Low FLOAT NOT NULL,
                Close FLOAT NOT NULL,
                Adj_Close FLOAT NOT NULL,
                Volume BIGINT NOT NULL,
                Ticker VARCHAR(255) NOT NULL,
                UNIQUE (Date, Ticker)
                );''')
               
print("Table created successfully")

query = '''INSERT INTO prices (Date, Open, High, Low, Close, Adj_Close, Volume, Ticker)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (Date, Ticker) DO NOTHING;'''

for ticker in usa_tickers:
    try:
        stock_data = yf.download(ticker, start='2021-8-1', end="2023-10-1")
        stock_data.index = np.datetime_as_string(stock_data.index, unit='D') # convert date to string
        stock_data['Ticker'] = ticker # create a new column for ticker
        stock_data = stock_data.rename(columns={"Adj Close": "Adj_Close"}) # Add _ to avoid name issues in database
        records = stock_data.to_records(index=True) # stock data as list of tuples
        cur.executemany(query, records)
    except:
        pass


cur.execute("SELECT COUNT(*) FROM prices;")
count = cur.fetchone()[0]
print(count)
print("Query done successfully")

cur.execute("SELECT COUNT(DISTINCT ticker) FROM prices;")
count = cur.fetchone()[0]
print(count)
print("Query done successfully")


conn.close()

# TODO: try to read ticker names from a file
# TODO: see if the dates really need to be converted to strings

# TODO: UNIQUE(Date, Ticker)
# TODO: read everything, create a subset data structure for only the stocks from USA, and then insert only that into DB

