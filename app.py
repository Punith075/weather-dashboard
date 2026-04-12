import requests
import pandas as pd
import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import st_folium
from datetime import date, timedelta

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦",
    layout="wide"
)

# -----------------------------
# Session state
# -----------------------------
if "show_weather" not in st.session_state:
    st.session_state.show_weather = False

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

# -----------------------------
# LIGHT THEME CSS
# -----------------------------
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

.stApp {
    background-color: #f5f7fb;
    color: #1e293b;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

.main-title {
    font-size: 36px;
    font-weight: bold;
    color: #0f172a;
}

.sub-title {
    color: #475569;
    margin-bottom: 20px;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

div[data-testid="stMetric"] label {
    color: #64748b !important;
}

div[data-testid="stMetric"] div {
    color: #0f172a !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Title
# -----------------------------
st.markdown('<div class="main-title">🌦 Weather Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Forecast + historical weather analysis + rain percentage</div>', unsafe_allow_html=True)

# -----------------------------
# Places
# -----------------------------
PLACES = {
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
    "Tamil Nadu": (11.1271, 78.6569),
    "Karnataka": (15.3173, 75.7139)
}

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Select Location")

place = st.sidebar.selectbox("Choose place", list(PLACES.keys()))
start_date = st.sidebar.date_input("Start Date", date.today() - timedelta(days=7))
end_date = st.sidebar.date_input("End Date", date.today() - timedelta(days=1))

get_weather_btn = st.sidebar.button("Get Weather")
clear_btn = st.sidebar.button("Clear")

# -----------------------------
# API
# -----------------------------
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability",
        "daily": "precipitation_probability_max",
        "forecast_days": 3,
        "timezone": "auto"
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def get_history(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "auto"
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


# -----------------------------
# Plotly light theme
# -----------------------------
def make_light_plotly(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#f5f7fb",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# -----------------------------
# Button logic
# -----------------------------
if get_weather_btn:
    try:
        if start_date > end_date:
            st.error("Start date must be earlier than or equal to end date.")
            st.session_state.show_weather = False
            st.session_state.weather_data = None
        else:
            lat, lon = PLACES[place]
            weather = get_weather(lat, lon)
            history = get_history(lat, lon, str(start_date), str(end_date))

            st.session_state.weather_data = {
                "place": place,
                "lat": lat,
                "lon": lon,
                "weather": weather,
                "history": history
            }
            st.session_state.show_weather = True
    except Exception as e:
        st.session_state.show_weather = False
        st.session_state.weather_data = None
        st.error(f"Error: {e}")

if clear_btn:
    st.session_state.show_weather = False
    st.session_state.weather_data = None

# -----------------------------
# Display
# -----------------------------
if st.session_state.show_weather and st.session_state.weather_data:
    data = st.session_state.weather_data
    place = data["place"]
    lat = data["lat"]
    lon = data["lon"]

    weather = data["weather"]
    history = data["history"]

    st.subheader(f"📍 {place}")

    current_temp = weather["current"]["temperature_2m"]
    current_humidity = weather["current"]["relative_humidity_2m"]
    current_wind = weather["current"]["wind_speed_10m"]

    forecast_df = pd.DataFrame(weather["hourly"])
    forecast_df["time"] = pd.to_datetime(forecast_df["time"])

    daily_df = pd.DataFrame(weather["daily"])
    daily_rain_pct = int(daily_df["precipitation_probability_max"].iloc[0]) if not daily_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature", f"{current_temp} °C")
    c2.metric("Humidity", f"{current_humidity} %")
    c3.metric("Wind Speed", f"{current_wind} km/h")
    c4.metric("Rain Chance", f"{daily_rain_pct} %")

    st.subheader("Map")
    m = folium.Map(location=[lat, lon], zoom_start=6, tiles="OpenStreetMap")
    folium.Marker([lat, lon]).add_to(m)
    st_folium(m, width=None, height=400)

    st.subheader("Forecast Temperature")
    fig = px.line(forecast_df, x="time", y="temperature_2m", markers=True)
    make_light_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast Rain Percentage")
    fig_rain = px.bar(
        forecast_df,
        x="time",
        y="precipitation_probability",
        title="Hourly Rain Chance (%)"
    )
    make_light_plotly(fig_rain)
    fig_rain.update_yaxes(title="Rain Percentage (%)", range=[0, 100])
    st.plotly_chart(fig_rain, use_container_width=True)

    history_df = pd.DataFrame(history["hourly"])
    history_df["time"] = pd.to_datetime(history_df["time"])

    st.subheader("Historical Temperature")
    fig2 = px.line(history_df, x="time", y="temperature_2m", markers=True)
    make_light_plotly(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Historical Rainfall")
    fig3 = px.bar(
        history_df,
        x="time",
        y="precipitation",
        title="Past Rainfall (mm)"
    )
    make_light_plotly(fig3)
    fig3.update_yaxes(title="Rainfall (mm)")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Historical Data")
    show_df = history_df.rename(columns={
        "time": "Time",
        "temperature_2m": "Temperature (°C)",
        "relative_humidity_2m": "Humidity (%)",
        "wind_speed_10m": "Wind Speed (km/h)",
        "precipitation": "Rainfall (mm)"
    })
    st.dataframe(show_df, use_container_width=True, hide_index=True)

else:
    st.info("Select a place and click Get Weather")