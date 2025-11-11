import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Museum Recommender", layout="wide")

st.title("🏛️ Museum Recommender Dashboard")
st.write("Explore museum information, weather data, and recommendations.")

# ---- Sidebar ----
with st.sidebar:
    st.header("Settings")
    city = st.text_input("Enter City Name", "Seoul")
    api_key = st.text_input("Enter your OpenWeatherMap API Key", type="password")
    max_museums = st.slider("Number of museums to show", 1, 10, 5)
    show_weather = st.checkbox("Show Weather Data", True)
    show_humidity = st.checkbox("Show Humidity", True)
    show_precipitation = st.checkbox("Show Precipitation", True)
    show_temp = st.checkbox("Show Temperature", True)

# ---- Data Retrieval ----
def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {
            "Temperature (°C)": data["main"]["temp"],
            "Humidity (%)": data["main"]["humidity"],
            "Precipitation (mm)": data.get("rain", {}).get("1h", 0),
            "Weather": data["weather"][0]["description"].title(),
        }
    else:
        return None

def get_museum_data(city):
    # 模拟数据
    museums = [
        {"Name": "National Museum of Korea", "Rating": 9.2, "Visitors": 12000, "Location": "Seoul"},
        {"Name": "Leeum Samsung Museum of Art", "Rating": 8.7, "Visitors": 8000, "Location": "Seoul"},
        {"Name": "Seoul Museum of History", "Rating": 8.4, "Visitors": 6000, "Location": "Seoul"},
        {"Name": "War Memorial of Korea", "Rating": 8.9, "Visitors": 9500, "Location": "Seoul"},
        {"Name": "MMCA Seoul", "Rating": 8.6, "Visitors": 7000, "Location": "Seoul"},
    ]
    return pd.DataFrame(museums[:max_museums])

# ---- Display ----
museum_data = get_museum_data(city)
weather_data = get_weather(city, api_key) if api_key else None

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🎨 Top {max_museums} Museums in {city}")
    st.dataframe(museum_data)

    fig = px.bar(
        museum_data,
        x="Name",
        y="Rating",
        text="Rating",
        color="Rating",
        title="Museum Ratings",
        color_continuous_scale="teal"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌦️ Weather Info")
    if weather_data:
        if show_temp:
            st.metric("Temperature (°C)", weather_data["Temperature (°C)"])
        if show_humidity:
            st.metric("Humidity (%)", weather_data["Humidity (%)"])
        if show_precipitation:
            st.metric("Precipitation (mm)", weather_data["Precipitation (mm)"])
        st.write(f"**Condition:** {weather_data['Weather']}")
    else:
        st.warning("Enter a valid API key to see weather data.")

# ---- Footer ----
st.markdown("---")
st.caption("© 2025 Museum Dashboard by [Your Name]. Built with Streamlit.")


