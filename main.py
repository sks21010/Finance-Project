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
            
            word-break: break-word;
            font-size: 2em;
            line-height: 1.2;
        }
    </style>
    <div class="custom-title-section">
        <h1>Welcome to the Stock Analysis Web Tool!</h1>
        <h4>View historic stock price data for companies in the NASDAQ 100 index!</h4>
    </div>
    """, unsafe_allow_html=True)


cur = conn.cursor()


def fetch_distinct_tickers(column_name):
    """Returns a list of distinct ticker names"""

    sql = f"SELECT DISTINCT({column_name}) FROM prices;"
    cur.execute(sql)
    distinct_tickers = cur.fetchall()
    distinct_tickers_list = [tuple[0] for tuple in distinct_tickers] # cur.fetchall() returns a tuple, 2nd value is blank in this case
    distinct_tickers_list.sort(key=lambda x: (x, len(x)))
    return distinct_tickers_list

selectbox_values = [""] + fetch_distinct_tickers("ticker")
selected_tickers = st.multiselect("Select tickers (max 5):", selectbox_values, max_selections=5)


def largest_data_gap():
    """Returns the largest gap of days in between data"""

    sql = '''WITH DateDifferences AS (
        SELECT 
            date,
            LEAD(date) OVER (ORDER BY date) AS next_date,
            LEAD(date) OVER (ORDER BY date) - date AS date_diff
        FROM 
            prices
    )
    SELECT 
        MAX(date_diff) AS max_difference
    FROM 
        DateDifferences
    WHERE 
        next_date IS NOT NULL;'''

    cur.execute(sql)
    days_gap = cur.fetchone()[0]
    return days_gap

# Date range
default_start_date = datetime(2021, 1, 1)
default_end_date = datetime(2024, 1, 1)

# Controlling date selection
start_date_selected = st.date_input("Start date:", 
                                    value=default_start_date, 
                                    min_value=default_start_date, 
                                    max_value=default_end_date - timedelta(days=largest_data_gap())
                                    )

end_date_selected = st.date_input("End date:", 
                                  value=default_end_date, 
                                  min_value = start_date_selected + timedelta(days=largest_data_gap()), 
                                  max_value=default_end_date
                                  )



st.write(f"Showing data for {', '.join(selected_tickers)} from {start_date_selected} to {end_date_selected}:")
st.write("")

plt.figure(figsize=(10, 5))

for ticker in selected_tickers:
    sql = '''SELECT date, adj_close FROM prices 
            WHERE ticker = %s 
                AND date BETWEEN %s AND %s
            ORDER BY date'''
    params = (ticker, start_date_selected, end_date_selected) # parameters to SQL statement must be provided in tuple form
    cur.execute(sql, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    
    
    plt.plot(df["date"], df["adj_close"], label=ticker)

# plt.title(f"Stock Price Over Time for {selected_ticker}", pad=20)
plt.title(f"Change in Stock Price (USD) for {', '.join(selected_tickers)} from {start_date_selected} to {end_date_selected}:", pad=20)
plt.xlabel("Date", labelpad=20)
plt.ylabel("Adjusted Closing Price (USD)", labelpad=20)
plt.xticks(rotation=45)
plt.grid(True)
plt.figtext(0.5, 
            -0.15, 
            "Note: YYYY-MM-DD for larger ranges, MM-DD-HH for very small ranges, if any such meaningful ranges exist.", 
            ha='center', 
            va='center', 
            fontsize=9, 
            color='red', 
            bbox=dict(facecolor='none', edgecolor='none', pad=5)
            )
plt.legend()
st.pyplot(plt)


footer = """
    <style>
    .footer {
        position: fixed;
        display: flex;
        bottom: 0;
        left: 0;
        width: 100vw;
        height: 4vh;
        background-color: #f1f1f1;
        font-size: 14px;
        color: #333;
        text-align: center;
        align-items: center;
        justify-content: center;
        padding-left: 7.5vh;
        margin: 0;
    }
    </style>
    <div class="footer">
        &copy; 2024 Sri Kiran Sripada. All rights reserved.
    </div>
"""

st.markdown(footer, unsafe_allow_html=True)


