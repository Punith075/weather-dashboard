import time
import requests
import pandas as pd
import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import st_folium
from datetime import date, timedelta

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_weather" not in st.session_state:
    st.session_state.show_weather = False

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

# -------------------------------------------------
# LOGIN PAGE STYLE
# -------------------------------------------------
def login_page_style():
    st.markdown("""
    <style>
    header, footer, #MainMenu {
        visibility: hidden;
    }

    .stApp {
        background: linear-gradient(180deg, #06111f 0%, #0a1d35 45%, #113b63 100%);
        overflow: hidden;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #06111f 0%, #0a1d35 45%, #113b63 100%);
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .cloud {
        position: fixed;
        border-radius: 999px;
        background: rgba(255,255,255,0.18);
        filter: blur(1px);
        z-index: 0;
    }

    .cloud::before,
    .cloud::after {
        content: "";
        position: absolute;
        background: rgba(255,255,255,0.18);
        border-radius: 50%;
    }

    .cloud1 {
        width: 170px;
        height: 52px;
        top: 90px;
        left: -220px;
        animation: cloudMove1 28s linear infinite;
    }
    .cloud1::before {
        width: 70px;
        height: 70px;
        left: 18px;
        top: -28px;
    }
    .cloud1::after {
        width: 82px;
        height: 82px;
        left: 74px;
        top: -34px;
    }

    .cloud2 {
        width: 230px;
        height: 62px;
        top: 180px;
        left: -280px;
        animation: cloudMove2 38s linear infinite;
    }
    .cloud2::before {
        width: 90px;
        height: 90px;
        left: 24px;
        top: -36px;
    }
    .cloud2::after {
        width: 100px;
        height: 100px;
        left: 102px;
        top: -40px;
    }

    .cloud3 {
        width: 150px;
        height: 48px;
        top: 300px;
        left: -200px;
        animation: cloudMove3 33s linear infinite;
    }
    .cloud3::before {
        width: 58px;
        height: 58px;
        left: 18px;
        top: -18px;
    }
    .cloud3::after {
        width: 66px;
        height: 66px;
        left: 64px;
        top: -24px;
    }

    @keyframes cloudMove1 {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(100vw + 500px)); }
    }

    @keyframes cloudMove2 {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(100vw + 650px)); }
    }

    @keyframes cloudMove3 {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(100vw + 520px)); }
    }

    .rain {
        position: fixed;
        width: 2px;
        height: 70px;
        background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(125,211,252,0.8));
        opacity: 0.35;
        z-index: 0;
        animation: rainFall linear infinite;
    }

    @keyframes rainFall {
        0% { transform: translateY(-120px); }
        100% { transform: translateY(110vh); }
    }

    .lightning-flash {
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.12);
        z-index: 1;
        animation: lightningFlash 8s infinite;
        pointer-events: none;
    }

    @keyframes lightningFlash {
        0%, 92%, 100% { opacity: 0; }
        93% { opacity: 0.05; }
        93.5% { opacity: 0.22; }
        94% { opacity: 0.03; }
        94.6% { opacity: 0.18; }
        95% { opacity: 0; }
    }

    .stTextInput, .stButton, .stAlert {
        position: relative;
        z-index: 3;
    }

    .stTextInput > label {
        color: #e2e8f0 !important;
        font-weight: 600;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.94);
        color: #0f172a;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.4);
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-weight: 700;
        border: none;
    }
    </style>

    <div class="lightning-flash"></div>

    <div class="cloud cloud1"></div>
    <div class="cloud cloud2"></div>
    <div class="cloud cloud3"></div>

    <div class="rain" style="left:8%; animation-duration:1.5s;"></div>
    <div class="rain" style="left:14%; animation-duration:1.25s;"></div>
    <div class="rain" style="left:22%; animation-duration:1.7s;"></div>
    <div class="rain" style="left:31%; animation-duration:1.35s;"></div>
    <div class="rain" style="left:39%; animation-duration:1.6s;"></div>
    <div class="rain" style="left:48%; animation-duration:1.2s;"></div>
    <div class="rain" style="left:57%; animation-duration:1.8s;"></div>
    <div class="rain" style="left:66%; animation-duration:1.45s;"></div>
    <div class="rain" style="left:74%; animation-duration:1.55s;"></div>
    <div class="rain" style="left:83%; animation-duration:1.3s;"></div>
    <div class="rain" style="left:91%; animation-duration:1.7s;"></div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
def show_login():
    login_page_style()

    left, center, right = st.columns([1.2, 1, 1.2])

    with center:
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size: 2.2rem;
                font-weight: 700;
                color: #e2e8f0;
                margin-bottom: 20px;
                text-shadow: 0 0 10px rgba(125,211,252,0.6);
            ">
                Welcome 🌦️
            </div>
            """,
            unsafe_allow_html=True
        )

        username = st.text_input(
            "Username",
            placeholder="Enter username",
            key="login_user"
        )

        password = st.text_input(
            "Password",
            placeholder="Enter password",
            type="password",
            key="login_pass"
        )

        login_btn = st.button(
            "Enter Dashboard",
            key="login_button",
            width="stretch"
        )

        DEMO_USERNAME = "admin"
        DEMO_PASSWORD = "weather123"

        if login_btn:
            if username == DEMO_USERNAME and password == DEMO_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

# -------------------------------------------------
# DASHBOARD THEME
# -------------------------------------------------
def apply_dashboard_theme(theme_name: str):
    if theme_name == "Light ☀️":
        bg_color = "#f5f7fb"
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

    st.markdown(
        f"""
        <style>
        header, footer, #MainMenu {{
            visibility: hidden;
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: {bg_color} !important;
            color: {text_color} !important;
        }}

        [data-testid="stHeader"] {{
            background: {header_bg} !important;
        }}

        section[data-testid="stSidebar"] {{
            display: block !important;
            background: {sidebar_bg} !important;
            color: {text_color} !important;
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

        .stDateInput input,
        .stSelectbox div[data-baseweb="select"] > div {{
            background: {card_bg} !important;
            color: {text_color} !important;
            border-color: {card_border} !important;
        }}

        [data-testid="stInfo"] {{
            background: {info_bg} !important;
            color: {info_text} !important;
            border: 1px solid {card_border} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    return plotly_template, paper_bg, plot_bg, text_color

# -------------------------------------------------
# REQUEST HELPERS
# -------------------------------------------------
def fetch_json_with_retry(url, params, timeout=20, retries=1, wait_seconds=2):
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            if response.status_code == 429:
                if attempt < retries:
                    time.sleep(wait_seconds)
                    continue
                return None, 429

            response.raise_for_status()
            return response.json(), response.status_code

        except requests.RequestException:
            if attempt < retries:
                time.sleep(wait_seconds)
                continue
            return None, None

    return None, None

# -------------------------------------------------
# API FUNCTIONS
# -------------------------------------------------
@st.cache_data(ttl=600)
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

    data, status = fetch_json_with_retry(url, params, timeout=10, retries=1, wait_seconds=2)

    if status == 429:
        return None
    return data

@st.cache_data(ttl=1800)
def get_history(lat, lon, start, end):
    start_dt = pd.to_datetime(start).date()
    end_dt = pd.to_datetime(end).date()
    today = date.today()

    # Recent dates -> use Forecast API past_days
    if end_dt >= today - timedelta(days=5):
        past_days = max(1, (today - start_dt).days)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
            "past_days": min(past_days, 16),
            "forecast_days": 0,
            "timezone": "auto"
        }

        data, status = fetch_json_with_retry(url, params, timeout=20, retries=1, wait_seconds=2)

        if status == 429 or data is None or "hourly" not in data:
            return None

        df = pd.DataFrame(data["hourly"])
        if "time" not in df.columns:
            return None

        df["time"] = pd.to_datetime(df["time"])
        df = df[
            (df["time"].dt.date >= start_dt) &
            (df["time"].dt.date <= end_dt)
        ]
        return {"hourly": df.to_dict(orient="list")}

    # Older dates -> use archive API
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "auto"
    }

    data, status = fetch_json_with_retry(url, params, timeout=20, retries=1, wait_seconds=2)

    if status == 429 or data is None or "hourly" not in data:
        return None

    return data

def apply_plotly_theme(fig, plotly_template, paper_bg, plot_bg, text_color):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def show_dashboard():
    st.sidebar.title("Select Location")
    theme = st.sidebar.radio("Theme", ["Light ☀️", "Dark 🌙"], key="dashboard_theme")

    plotly_template, paper_bg, plot_bg, text_color = apply_dashboard_theme(theme)

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
    logout_btn = st.sidebar.button("Logout", width="stretch")

    if logout_btn:
        st.session_state.logged_in = False
        st.session_state.show_weather = False
        st.session_state.weather_data = None
        st.rerun()

    st.markdown('<div class="main-title">🌦 Weather Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Forecast + historical weather analysis + rain percentage</div>',
        unsafe_allow_html=True
    )

    if get_weather_btn:
        if start_date > end_date:
            st.error("Start date must be earlier than or equal to end date.")
            st.session_state.show_weather = False
            st.session_state.weather_data = None
        else:
            with st.spinner("Fetching weather data..."):
                lat, lon = PLACES[place]
                weather = get_weather(lat, lon)
                history = get_history(lat, lon, str(start_date), str(end_date))

            if weather is None:
                st.warning("Weather API is busy right now. Please wait a few seconds and try again.")
                st.session_state.show_weather = False
                st.session_state.weather_data = None
            elif history is None:
                st.warning("Historical API is temporarily unavailable. Current weather still works.")
                st.session_state.weather_data = {
                    "place": place,
                    "lat": lat,
                    "lon": lon,
                    "weather": weather,
                    "history": {"hourly": {}}
                }
                st.session_state.show_weather = True
            else:
                st.session_state.weather_data = {
                    "place": place,
                    "lat": lat,
                    "lon": lon,
                    "weather": weather,
                    "history": history
                }
                st.session_state.show_weather = True

    if clear_btn:
        st.session_state.show_weather = False
        st.session_state.weather_data = None

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

        history_df = pd.DataFrame()
        if history is not None and "hourly" in history and history["hourly"]:
            history_df = pd.DataFrame(history["hourly"])
            if not history_df.empty and "time" in history_df.columns:
                history_df["time"] = pd.to_datetime(history_df["time"])

        m = folium.Map(location=[lat, lon], zoom_start=6, tiles="OpenStreetMap")
        folium.Marker([lat, lon], tooltip=place, popup=place).add_to(m)

        fig_forecast_temp = px.line(
            forecast_df, x="time", y="temperature_2m", markers=True, title="Forecast Temperature"
        )
        apply_plotly_theme(fig_forecast_temp, plotly_template, paper_bg, plot_bg, text_color)

        fig_rain = px.bar(
            forecast_df, x="time", y="precipitation_probability", title="Forecast Rain Percentage"
        )
        apply_plotly_theme(fig_rain, plotly_template, paper_bg, plot_bg, text_color)
        fig_rain.update_yaxes(title="Rain Percentage (%)", range=[0, 100])

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
            if not history_df.empty:
                st.subheader("Historical Temperature")
                fig_history_temp = px.line(
                    history_df, x="time", y="temperature_2m", markers=True, title="Historical Temperature"
                )
                apply_plotly_theme(fig_history_temp, plotly_template, paper_bg, plot_bg, text_color)
                st.plotly_chart(fig_history_temp, width="stretch")

                st.subheader("Historical Rainfall")
                fig_history_rain = px.bar(
                    history_df, x="time", y="precipitation", title="Historical Rainfall"
                )
                apply_plotly_theme(fig_history_rain, plotly_template, paper_bg, plot_bg, text_color)
                fig_history_rain.update_yaxes(title="Rainfall (mm)")
                st.plotly_chart(fig_history_rain, width="stretch")

                show_df = history_df.rename(columns={
                    "time": "Time",
                    "temperature_2m": "Temperature (°C)",
                    "relative_humidity_2m": "Humidity (%)",
                    "wind_speed_10m": "Wind Speed (km/h)",
                    "precipitation": "Rainfall (mm)"
                })

                st.subheader("Historical Data")
                st.dataframe(show_df, width="stretch", hide_index=True)
            else:
                st.info("Historical data is temporarily unavailable for this selection.")
    else:
        st.info("Select a place and click Get Weather")

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    show_dashboard()
else:
    show_login()
