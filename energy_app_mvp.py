# energy_app_mvp.py

import pandas as pd
import streamlit as st
from datetime import datetime

import os

st.sidebar.header("📝 Log Today’s Usage")

today_units = st.sidebar.number_input("Units Consumed Today (kWh)", min_value=0.0)
ac_hours = st.sidebar.number_input("AC Usage (hours)", min_value=0.0)
geyser_minutes = st.sidebar.number_input("Geyser Usage (minutes)", min_value=0)
tv_hours = st.sidebar.number_input("TV Usage (hours)", min_value=0.0)
submit = st.sidebar.button("Save Entry")

if submit:
    new_row = {
        "date": pd.to_datetime("today").date(),
        "units_consumed": today_units,
        "ac_usage_hours": ac_hours,
        "geyser_usage_minutes": geyser_minutes,
        "tv_usage_hours": tv_hours,
        "total_bill": round(today_units * 7.5, 2)  # example rate ₹7.5 per unit
    }

    # Append to CSV (create if not exists)
    file_path = "C:\Users\Vijit\Documents\Energy App\synthetic_energy_data_last_30_days.csv"
    df_new = pd.DataFrame([new_row])

    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(file_path, index=False)
    st.success("✅ Data logged successfully!")

# Load the synthetic dataset
df = pd.read_csv("C:\Users\Vijit\Documents\Energy App\synthetic_energy_data_last_30_days.csv")
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


# Optional: appliance breakdown
if "ac_usage_hours" in df.columns:
    st.subheader("Appliance Usage Patterns")
    st.bar_chart(df[["ac_usage_hours", "geyser_usage_minutes", "tv_usage_hours"]])

st.markdown("---")
st.markdown("Made with ❤️ using synthetic data. Replace with real-time meter/API data in production.")
