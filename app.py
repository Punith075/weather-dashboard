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
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Session state
# -----------------------------
if "show_weather" not in st.session_state:
    st.session_state.show_weather = False

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("Select Location")

theme = st.sidebar.radio("Theme", ["Light ☀️", "Dark 🌙"])

PLACES = {
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Trichy": (10.7905, 78.7047),
    "Vellore": (12.9165, 79.1325),
    "Tamil Nadu": (11.1271, 78.6569),
    "Karnataka": (15.3173, 75.7139)
}

place = st.sidebar.selectbox("Choose place", list(PLACES.keys()))
start_date = st.sidebar.date_input("Start Date", date.today() - timedelta(days=7))
end_date = st.sidebar.date_input("End Date", date.today() - timedelta(days=1))

get_weather_btn = st.sidebar.button("Get Weather", width="stretch")
clear_btn = st.sidebar.button("Clear", width="stretch")

# -----------------------------
# Theme settings
# -----------------------------
if theme == "Light ☀️":
    bg_color = "#f5f7fb"
    app_bg = "#f5f7fb"
    sidebar_bg = "#ffffff"
    header_bg = "#f5f7fb"
    text_color = "#1e293b"
    title_color = "#0f172a"
    subtitle_color = "#475569"
    card_bg = "#ffffff"
    card_border = "#e2e8f0"
    label_color = "#64748b"
    metric_color = "#0f172a"
    info_bg = "#e0f2fe"
    info_text = "#0f172a"
    plotly_template = "plotly_white"
    paper_bg = "#f5f7fb"
    plot_bg = "#ffffff"
else:
    bg_color = "#020617"
    app_bg = "#020617"
    sidebar_bg = "#0f172a"
    header_bg = "#020617"
    text_color = "#f8fafc"
    title_color = "#f8fafc"
    subtitle_color = "#cbd5e1"
    card_bg = "#1e293b"
    card_border = "#334155"
    label_color = "#cbd5e1"
    metric_color = "#f8fafc"
    info_bg = "#1e293b"
    info_text = "#f8fafc"
    plotly_template = "plotly_dark"
    paper_bg = "#020617"
    plot_bg = "#1e293b"

# -----------------------------
# Apply theme CSS
# -----------------------------
st.markdown(
    f"""
    <style>
    header, footer, #MainMenu {{
        visibility: hidden;
    }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: {app_bg} !important;
        color: {text_color} !important;
    }}

    [data-testid="stHeader"] {{
        background: {header_bg} !important;
    }}

    [data-testid="stToolbar"] {{
        right: 1rem;
    }}

    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        color: {text_color} !important;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    .main-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {title_color};
        margin-bottom: 0.25rem;
    }}

    .sub-title {{
        font-size: 1rem;
        color: {subtitle_color};
        margin-bottom: 1rem;
    }}

    div[data-testid="stMetric"] {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 14px !important;
        padding: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    div[data-testid="stMetric"] label {{
        color: {label_color} !important;
    }}

    div[data-testid="stMetric"] div {{
        color: {metric_color} !important;
        font-weight: 700 !important;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stText"],
    .st-emotion-cache-10trblm,
    .st-emotion-cache-16idsys {{
        color: {text_color} !important;
    }}

    [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    [data-baseweb="tab"] {{
        color: {text_color} !important;
    }}

    [data-testid="stInfo"] {{
        background: {info_bg} !important;
        color: {info_text} !important;
        border: 1px solid {card_border} !important;
    }}

    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input {{
        background: {card_bg} !important;
        color: {text_color} !important;
        border-color: {card_border} !important;
    }}

    .stButton > button {{
        border-radius: 10px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Title
# -----------------------------
st.markdown('<div class="main-title">🌦 Weather Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Forecast + historical weather analysis + rain percentage</div>',
    unsafe_allow_html=True
)

# -----------------------------
# API functions
# -----------------------------
def get_weather(lat, lon):
    try:
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
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Failed to fetch weather data")
        return None


def get_history(lat, lon, start, end):
    try:
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
    except Exception:
        st.error("Failed to fetch historical data")
        return None


def apply_plotly_theme(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# -----------------------------
# Button logic
# -----------------------------
if get_weather_btn:
    if start_date > end_date:
        st.error("Start date must be earlier than or equal to end date.")
        st.session_state.show_weather = False
        st.session_state.weather_data = None
    else:
        lat, lon = PLACES[place]
        weather = get_weather(lat, lon)
        history = get_history(lat, lon, str(start_date), str(end_date))

        if weather is not None and history is not None:
            st.session_state.weather_data = {
                "place": place,
                "lat": lat,
                "lon": lon,
                "weather": weather,
                "history": history
            }
            st.session_state.show_weather = True
        else:
            st.session_state.show_weather = False
            st.session_state.weather_data = None

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

    current_temp = weather["current"]["temperature_2m"]
    current_humidity = weather["current"]["relative_humidity_2m"]
    current_wind = weather["current"]["wind_speed_10m"]

    forecast_df = pd.DataFrame(weather["hourly"])
    forecast_df["time"] = pd.to_datetime(forecast_df["time"])

    daily_df = pd.DataFrame(weather["daily"])
    daily_rain_pct = int(daily_df["precipitation_probability_max"].iloc[0]) if not daily_df.empty else 0

    history_df = pd.DataFrame(history["hourly"])
    history_df["time"] = pd.to_datetime(history_df["time"])

    m = folium.Map(location=[lat, lon], zoom_start=6, tiles="OpenStreetMap")
    folium.Marker([lat, lon], tooltip=place, popup=place).add_to(m)

    fig_forecast_temp = px.line(
        forecast_df,
        x="time",
        y="temperature_2m",
        markers=True,
        title="Forecast Temperature"
    )
    apply_plotly_theme(fig_forecast_temp)
    fig_forecast_temp.update_yaxes(title="Temperature (°C)")

    fig_rain = px.bar(
        forecast_df,
        x="time",
        y="precipitation_probability",
        title="Forecast Rain Percentage"
    )
    apply_plotly_theme(fig_rain)
    fig_rain.update_yaxes(title="Rain Percentage (%)", range=[0, 100])

    fig_history_temp = px.line(
        history_df,
        x="time",
        y="temperature_2m",
        markers=True,
        title="Historical Temperature"
    )
    apply_plotly_theme(fig_history_temp)
    fig_history_temp.update_yaxes(title="Temperature (°C)")

    fig_history_rain = px.bar(
        history_df,
        x="time",
        y="precipitation",
        title="Historical Rainfall"
    )
    apply_plotly_theme(fig_history_rain)
    fig_history_rain.update_yaxes(title="Rainfall (mm)")

    show_df = history_df.rename(columns={
        "time": "Time",
        "temperature_2m": "Temperature (°C)",
        "relative_humidity_2m": "Humidity (%)",
        "wind_speed_10m": "Wind Speed (km/h)",
        "precipitation": "Rainfall (mm)"
    })

    tab1, tab2, tab3 = st.tabs(["Current", "Forecast", "History"])

    with tab1:
        st.subheader(f"📍 {place}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{current_temp} °C")
            st.metric("Wind Speed", f"{current_wind} km/h")
        with col2:
            st.metric("Humidity", f"{current_humidity} %")
            st.metric("Rain Chance", f"{daily_rain_pct} %")

        st.subheader("Map")
        st_folium(m, width=None, height=300)

    with tab2:
        st.subheader("Forecast Temperature")
        st.plotly_chart(fig_forecast_temp, width="stretch")

        st.subheader("Forecast Rain")
        st.plotly_chart(fig_rain, width="stretch")

    with tab3:
        st.subheader("Historical Temperature")
        st.plotly_chart(fig_history_temp, width="stretch")

        st.subheader("Historical Rainfall")
        st.plotly_chart(fig_history_rain, width="stretch")

        st.subheader("Historical Data")
        st.dataframe(show_df, width="stretch", hide_index=True)

else:
    st.info("Select a place and click Get Weather")
