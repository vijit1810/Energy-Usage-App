# energy_app_mvp.py

import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Load the synthetic dataset
df = pd.read_csv("synthetic_energy_data_last_30_days.csv")
df["date"] = pd.to_datetime(df["date"])

# Calculate projections
today = df["date"].max()
days_passed = df.shape[0]
avg_daily_units = df["units_consumed"].mean()
projected_units = round(avg_daily_units * 30, 2)
projected_bill = round((df["total_bill"].sum() / days_passed) * 30, 2)

# Alert logic
threshold_units = 360  # Example: Alert if projected > 360 units/month
alert = projected_units > threshold_units

# Streamlit UI
st.title("⚡ Energy Usage Tracker - MVP")

st.write(f"Tracking from **{df['date'].min().date()}** to **{today.date()}**")
st.metric("📈 Avg Daily Units", f"{avg_daily_units:.2f} units/day")
st.metric("🔮 Projected Monthly Units", f"{projected_units} units")
st.metric("💰 Projected Monthly Bill", f"₹{projected_bill}")

if alert:
    st.warning("⚠️ You are projected to exceed the monthly unit threshold! Reduce AC/Geyser usage.")

# Line Chart - Units Consumed Per Day
fig = px.line(df, x="date", y="units_consumed", title="Daily Electricity Consumption (Units)")
st.plotly_chart(fig)

# Optional: appliance breakdown
if "ac_usage_hours" in df.columns:
    st.subheader("Appliance Usage Patterns")
    st.bar_chart(df[["ac_usage_hours", "geyser_usage_minutes", "tv_usage_hours"]])

st.markdown("---")
st.markdown("Made with ❤️ using synthetic data. Replace with real-time meter/API data in production.")
