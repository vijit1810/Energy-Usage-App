import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Smart Energy Saver", layout="wide")
st.title("⚡ Smart Energy Saver App")
st.markdown("Track your electricity usage, get alerts, and predict future consumption.")

DATA_FILE = "synthetic_energy_data_last_30_days.csv"

# Load Data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        return pd.DataFrame(columns=[
            "date", "units_consumed", "ac_usage_hours",
            "geyser_usage_minutes", "tv_usage_hours", "total_bill"
        ])

df = load_data()

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Manual Input", "🔮 Predictions"])

# ========== TAB 1 ==========
with tab1:
    st.subheader("📈 Daily Usage Overview")
    if not df.empty:
        st.metric("Total Days Logged", len(df))
        st.metric("Avg Daily Units", round(df["units_consumed"].mean(), 2))
        st.metric("Estimated Monthly Bill", f"₹ {round(df['total_bill'].sum(), 2)}")

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["units_consumed"],
                                 mode="lines+markers", name="Units Consumed"))
        fig.update_layout(title="📅 Daily Energy Usage", xaxis_title="Date", yaxis_title="kWh")
        st.plotly_chart(fig, use_container_width=True)

        # Show last entries
        st.markdown("### 🧾 Last 5 Days' Entries")
        st.dataframe(df.tail(5), use_container_width=True)

        # Smart alerts
        st.markdown("### ⚠️ Smart Alerts")
        avg_units = df["units_consumed"].mean()
        last = df.sort_values("date").iloc[-1]

        if last["units_consumed"] > 1.2 * avg_units:
            st.warning(f"⚡ High usage alert: {last['units_consumed']} kWh (avg {avg_units:.2f})")
        if last.get("ac_usage_hours", 0) > 6:
            st.warning(f"🌬️ AC used for {last['ac_usage_hours']} hrs. Try reducing usage.")
        if last.get("geyser_usage_minutes", 0) > 40:
            st.warning(f"🚿 Geyser used for {last['geyser_usage_minutes']} mins. May be heating too long.")
    else:
        st.info("No data yet. Please log your usage in the next tab.")

# ========== TAB 2 ==========
with tab2:
    st.subheader("📝 Log Today's Usage")
    with st.form("log_form"):
        today_units = st.number_input("Units Consumed Today (kWh)", min_value=0.0, step=0.1)
        ac_hours = st.number_input("AC Usage (hours)", min_value=0.0, step=0.5)
        geyser_mins = st.number_input("Geyser Usage (minutes)", min_value=0, step=5)
        tv_hours = st.number_input("TV Usage (hours)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("✅ Submit")

        if submitted:
            new_entry = {
                "date": pd.to_datetime("today").date(),
                "units_consumed": today_units,
                "ac_usage_hours": ac_hours,
                "geyser_usage_minutes": geyser_mins,
                "tv_usage_hours": tv_hours,
                "total_bill": round(today_units * 7.5, 2)
            }

            new_df = pd.DataFrame([new_entry])
            full_df = pd.concat([df, new_df], ignore_index=True)
            full_df.to_csv(DATA_FILE, index=False)
            st.success("✅ Entry saved successfully! Please refresh the app.")

# ========== TAB 3 ==========
with tab3:
    st.subheader("🔮 Predict Next 7 Days' Usage (Linear Regression)")
    if len(df) < 10:
        st.info("Need at least 10 days of data to train model.")
    else:
        df['day_of_week'] = df['date'].dt.dayofweek
        X = df[["day_of_week", "ac_usage_hours", "geyser_usage_minutes", "tv_usage_hours"]]
        y = df["units_consumed"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict next 7 days
        future_days = pd.date_range(df['date'].max() + pd.Timedelta(days=1), periods=7)
        future_df = pd.DataFrame({
            "day_of_week": future_days.dayofweek,
            "ac_usage_hours": [4]*7,
            "geyser_usage_minutes": [30]*7,
            "tv_usage_hours": [2]*7
        })

        preds = model.predict(future_df)

        pred_chart = go.Figure()
        pred_chart.add_trace(go.Bar(x=future_days.strftime("%a %d %b"), y=preds, name="Predicted kWh"))
        pred_chart.update_layout(title="🔮 Next 7 Days Predicted Usage", yaxis_title="kWh")
        st.plotly_chart(pred_chart, use_container_width=True)

        st.write("### 🔢 Prediction Table")
        st.dataframe(pd.DataFrame({
            "Date": future_days.date,
            "Predicted Units": [round(p, 2) for p in preds]
        }))
