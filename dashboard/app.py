import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

st.title("bot-S Monitoring Dashboard")

# Health check
health = requests.get(f"{API_URL}/health").json()
st.subheader("Service Status")
st.write("✅" if health.get("status")=="ok" else "❌", health)

# Trades table
st.subheader("Trades")
resp = requests.get(f"{API_URL}/trades/download")
if resp.status_code == 200:
    df_trades = pd.read_csv(pd.compat.StringIO(resp.text))
    st.dataframe(df_trades)
else:
    st.write("No trades data available.")

# Risk report embed
st.subheader("Risk Report")
report_url = f"{API_URL}/risk/report"
st.components.v1.iframe(report_url, height=600, scrolling=True)
