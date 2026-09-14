import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Challan History",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Challan History")

conn = sqlite3.connect("Chalan.db")

conn.execute(
    """
    CREATE TABLE IF NOT EXISTS challans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challan_no TEXT,
        vehicle_reg TEXT,
        violation TEXT,
        fine INTEGER,
        plate TEXT,
        created_at TEXT
    )
    """
)

df = pd.read_sql_query(
    "SELECT challan_no, vehicle_reg, violation, fine, plate, created_at "
    "FROM challans ORDER BY created_at DESC",
    conn
)

conn.close()

if df.empty:
    st.info("No challans issued yet. Generate one from the main page.")
else:
    st.dataframe(df, width="stretch")