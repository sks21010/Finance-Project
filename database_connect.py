import streamlit as st
import psycopg2

@st.cache_resource(ttl=600)
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# @st.cache_data(ttl=600)
# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchone()[0]
    

# sql = 'SELECT COUNT(*) FROM prices;'

# st.write((run_query(sql)))
    
