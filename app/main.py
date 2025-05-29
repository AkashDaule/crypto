# app/main.py

import streamlit as st
import pandas as pd
import altair as alt
from collections import deque
from datetime import datetime
from data_provider import fetch_price
import time

st.set_page_config(page_title="Crypto Real-Time Dashboard", layout="wide")

# Sidebar Controls
st.sidebar.header("Controls")
symbol = st.sidebar.text_input("Symbol", value="BTCUSDT")
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 30, 5)

# Dark Mode Toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode_checkbox = st.sidebar.checkbox("Dark mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode_checkbox

# Alert threshold input
alert_threshold = st.sidebar.number_input("Notify me when price > ", min_value=0.0, value=50000.0, step=1.0)

# Initialize deque cache
if "data" not in st.session_state:
    st.session_state.data = deque(maxlen=300)

# Fetch data
raw = fetch_price(symbol.upper())

if raw:
    timestamp = datetime.utcnow()
    price = float(raw["lastPrice"])
    volume = float(raw["volume"])
    st.session_state.data.append({"timestamp": timestamp, "price": price, "volume": volume})

    df = pd.DataFrame(st.session_state.data)
    df.set_index("timestamp", inplace=True)

    df["rolling"] = df["price"].rolling(window=10, min_periods=1).mean()
    df["pct_change"] = df["price"].pct_change().fillna(0) * 100

    # Check alert
    if price > alert_threshold:
        st.sidebar.warning(f"⚠️ Alert! Price exceeded {alert_threshold}")

    # Define colors based on theme
    if st.session_state.dark_mode:
        bg_color = "#0e1117"
        text_color = "white"
        logo_color = "white"
        chart_color = "lightblue"
    else:
        bg_color = "white"
        text_color = "black"
        logo_color = "black"
        chart_color = "blue"

    # Inject CSS for background and text colors
    st.markdown(
        f"""
        <style>
        .main {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .css-1d391kg {{
            color: {text_color} !important;
        }}
        /* Title style */
        .crypto-title {{
            font-size: 2rem;
            font-weight: bold;
            color: {text_color};
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        /* Logo style */
        .crypto-logo {{
            width: 30px;
            height: 30px;
            fill: {logo_color};
        }}
        /* Metric value color */
        div[data-testid="stMetricValue"] > div {{
            color: {text_color} !important;
        }}
        /* Sidebar label color */
        label[for^="sidebar"] {{
            color: {text_color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title with logo
    st.markdown(
        f"""
        <div class="crypto-title">
            <svg class="crypto-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="{logo_color}" stroke-width="2" fill="{logo_color}" />
                <text x="12" y="16" text-anchor="middle" font-size="12" fill="{bg_color}" font-family="Arial" font-weight="bold">₿</text>
            </svg>
            Crypto Real-Time Dashboard
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI Tiles
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(label="Last Price", value=f"${price:,.2f}")
    kpi_col2.metric(label="1-min % Change", value=f"{df['pct_change'].tail(60).mean():.2f}%")
    kpi_col3.metric(label="Volume (1-min)", value=f"{df['volume'].tail(60).sum():,.2f}")

    # Line chart
    line_chart = (
        alt.Chart(df.reset_index())
        .mark_line(color=chart_color)
        .encode(
            x=alt.X("timestamp:T", axis=alt.Axis(labelColor=text_color, titleColor=text_color)),
            y=alt.Y("price:Q", axis=alt.Axis(labelColor=text_color, titleColor=text_color)),
            tooltip=[alt.Tooltip("timestamp:T", title="Time"), alt.Tooltip("price:Q", title="Price")],
        )
        .properties(height=400)
    )

    st.altair_chart(line_chart, use_container_width=True)

else:
    st.error(f"⚠️ Failed to fetch data for symbol '{symbol.upper()}'. Please check the symbol and API availability.")

# Sleep and rerun
time.sleep(refresh_interval)
st.experimental_rerun() if hasattr(st, "experimental_rerun") else None
