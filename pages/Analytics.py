import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Challan Analytics")

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
        created_at TEXT,
        status TEXT DEFAULT 'Unpaid'
    )
    """
)

df = pd.read_sql_query("SELECT * FROM challans", conn)
conn.close()

if df.empty:
    st.info("No challans yet. Data will appear here once challans are generated.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Violations by Type")
        st.bar_chart(df["violation"].value_counts())

    with col2:
        st.subheader("Revenue")
        paid_df = df[df["status"] == "Paid"]
        st.metric("Total Paid Revenue", f"₹{paid_df['fine'].sum()}")
        st.metric("Total Pending Revenue", f"₹{df[df['status'] != 'Paid']['fine'].sum()}")

    st.subheader("Daily Revenue Trend")
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    st.line_chart(df.groupby("date")["fine"].sum())