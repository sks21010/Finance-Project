import streamlit as st
import psycopg2


def init_connection():
    try: 
        return psycopg2.connect(**st.secrets["postgres"])
    except psycopg2.OperationalError as e:
        st.error(f"Operational error: {e}")
    except psycopg2.InterfaceError as e:
        st.error(f"Interface error: {e}")
        try:
            return psycopg2.connect(**st.secrets["postgres"])
        except Exception as retry_e:
            st.error(f"Retry failed: {retry_e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None

conn = init_connection()
    
