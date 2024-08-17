import streamlit as st
import psycopg2

@st.cache_resource(ttl=600)
def init_connection():
    try: 
        return psycopg2.connect(**st.secrets["postgres"])
    except psycopg2.OperationalError as e:
        st.error(f"Operational error: {e}")
    except psycopg2.InterfaceError as e:
        st.error(f"Interface error: {e}")
        return psycopg2.connect(**st.secrets["postgres"])
    except Exception as e:
        st.error(f"Unexpected error: {e}")

conn = init_connection()
    
