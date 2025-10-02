import os
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Customs Monitor Dashboard", layout="wide")

DB_URL = st.secrets.get("database_url", "sqlite:///data/monitor.db")

engine = create_engine(DB_URL, echo=False, future=True)
with engine.connect() as con:
    df = pd.read_sql("SELECT * FROM items ORDER BY created_at DESC", con)

st.title("📊 Customs & Customs-Law Monitor")
st.caption("Vámkódex, vámszabályok és kapcsolódó jogi változások figyelése")

risk = st.multiselect("Kockázati szint", ["high", "medium", "low"], default=["high", "medium", "low"])
source = st.multiselect("Forrás", sorted(df["source"].dropna().unique().tolist()) if not df.empty else [], default=None)

filt = df.copy()
if not df.empty:
    if risk:
        filt = filt[filt["risk_level"].isin(risk)]
    if source:
        filt = filt[filt["source"].isin(source)]

st.subheader("Események listája")
if not df.empty:
    st.dataframe(filt[["created_at", "source", "title", "url", "risk_level", "published_at", "lang"]])
else:
    st.info("Még nincsenek adatok. A begyűjtés első futása után jelennek meg az események.")

st.subheader("Időbeli alakulás")
if not df.empty:
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    counts = df.groupby(["date", "risk_level"]).size().reset_index(name="count")
    fig = px.line(counts, x="date", y="count", color="risk_level")
    st.plotly_chart(fig, use_container_width=True)
