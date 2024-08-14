import streamlit as st

st.write("# Welcome to the Stock Analysis Tool!")
st.write("#### View historic stock price data for over 20,000 US-indexed companies!")

x = st.text_input("Search stock by ticker name:")
st.write(f"Viewing data for: {x}")




