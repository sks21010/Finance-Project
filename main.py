import streamlit as st
from database_connect import conn
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.markdown("""
    <style>
        .custom-title-section {
            width: 100vh;
            overflow: hidden;
        }
    </style>
    <div class="custom-title-section">
        <h1>Welcome to the Stock Analysis Tool!</h1>
        <h4>View historic stock price data for over 20,000 US-indexed companies!</h4>
    </div>
    """, unsafe_allow_html=True)


cur = conn.cursor()


def fetch_distinct_tickers(column_name):
    sql = f"SELECT DISTINCT({column_name}) FROM prices;"
    cur.execute(sql)
    distinct_tickers = cur.fetchall()
    distinct_tickers_list = [tuple[0] for tuple in distinct_tickers] # cur.fetchall() returns a tuple, 2nd value is blank in this case
    distinct_tickers_list.sort(key=lambda x: (x, len(x)))
    return distinct_tickers_list

selectbox_values = fetch_distinct_tickers("ticker")
selected_ticker = st.selectbox("Select a ticker:", selectbox_values)


# Date range
default_start_date = datetime(2021, 1, 1)
default_end_date = datetime(2024, 1, 1)

# Controlling date selection
start_date_selected = st.date_input("Start date:", value=default_start_date, min_value=default_start_date, max_value=default_end_date - timedelta(days=1))
end_date_selected = st.date_input("End date:", value=default_end_date, min_value = start_date_selected + timedelta(days=1), max_value=default_end_date)



st.write(f"Change in stock price of {selected_ticker} from {start_date_selected} to {end_date_selected}")


sql = '''SELECT date, adj_close FROM prices 
        WHERE ticker = %s 
            AND date BETWEEN %s AND %s
        ORDER BY date'''
params = (selected_ticker, start_date_selected, end_date_selected) # parameters to SQL statement must be provided in tuple form
cur.execute(sql, params)
rows = cur.fetchall()
columns = [desc[0] for desc in cur.description]

df = pd.DataFrame(rows, columns=columns)

# Plotting with Matplotlib
plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["adj_close"])
plt.title(f"Stock Price Over Time for {selected_ticker}")
plt.xlabel("Date")
plt.ylabel("Adjusted Closing Price (USD)")
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt)




