import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from database_connect import conn
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
    distinct_tickers_list = [tuple[0] for tuple in distinct_tickers]
    distinct_tickers_list.sort(key=lambda x: (x, len(x)))
    return distinct_tickers_list

selectbox_values = [""] + fetch_distinct_tickers("ticker")
selected_tickers = st.multiselect("Select tickers to view & compare (max 5):", selectbox_values, max_selections=5)

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

default_start_date = datetime(2021, 1, 1)
default_end_date = datetime(2024, 1, 1)

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

st.write("_Hover your cursor over the graph to examine stock prices at specific dates!_") # italicized text


fig = go.Figure()

for ticker in selected_tickers:
    sql = '''SELECT date, adj_close FROM prices 
            WHERE ticker = %s 
                AND date BETWEEN %s AND %s
            ORDER BY date'''
    params = (ticker, start_date_selected, end_date_selected)
    cur.execute(sql, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    
    
    fig.add_trace(go.Scatter(x=df["date"], y=df["adj_close"], mode='lines', name=ticker))

fig.update_layout(
                title={
                        'text': f"Change in Stock Price (USD) for {', '.join(selected_tickers)} from {start_date_selected} to {end_date_selected}:",
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="Date",
                    yaxis_title="Adjusted Closing Price (USD)",
                    xaxis_tickformat='%Y-%m-%d'
                )

st.plotly_chart(fig)


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


