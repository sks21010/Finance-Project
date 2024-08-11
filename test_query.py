import psycopg2

from dotenv import load_dotenv
import os
load_dotenv()

# Database connection parameters
dbname = os.getenv('DBNAME')
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")


conn = psycopg2.connect(
    database=dbname, user=user, password=password, host=host, port=port
)
conn.autocommit = True
cur = conn.cursor()

try: 
    sql = "SELECT COUNT(*) FROM prices;"
    cur.execute(sql)
    output = cur.fetchone()[0]
    print(output)
    print("Query performed successfully")
    
except:
    print("Cannot query from non-existent table")

finally:
    conn.close()