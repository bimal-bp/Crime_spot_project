import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Load the datasets
@st.cache_data
def load_crime_data():
    return pd.read_pickle('crime_data.pkl')

@st.cache_data
def load_location_data():
    return pd.read_pickle('state_district_lat_long.pkl')

crime_data = load_crime_data()
location_data = load_location_data()

# Capitalize state and district names for consistency
crime_data['state/ut'] = crime_data['state/ut'].str.title()
crime_data['district'] = crime_data['district'].str.title()
location_data['State'] = location_data['State'].str.title()
location_data['District'] = location_data['District'].str.title()

# Login Page
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login Page")

    name = st.text_input("Enter your Name")
    gender = st.radio("Select Gender", ['Male', 'Female', 'Other'])
    age = st.number_input("Enter your Age", min_value=1, max_value=120, value=25)

    if st.button("Login"):
        if name and gender:
            st.session_state.logged_in = True
            st.session_state.user_name = name
            st.success(f"Welcome, {name}! You are logged in.")
        else:
            st.error("Please enter your name and select your gender.")
else:
    # Home Page
    st.title(f"Welcome, {st.session_state.user_name}!")
    st.write("Navigate and analyze crime insights in your area.")

    if st.button("Go to Crime Analysis 🔍"):
        st.session_state.page = 'Analysis'

# Analysis Page
if 'page' in st.session_state and st.session_state.page == 'Analysis':
    st.title("🔍 Select Location for Crime Analysis")

    # State and District Selection
    state = st.selectbox('Select State/UT:', crime_data['state/ut'].unique())
    districts = crime_data[crime_data['state/ut'] == state]['district'].unique()
    district = st.selectbox('Select District:', districts)

    if st.button('Show Crime Data'):
        filtered_data = crime_data[
            (crime_data['state/ut'] == state) &
            (crime_data['district'] == district) &
            (crime_data['year'] == 2024)  # Only consider 2024 data
        ]

        st.subheader(f'Crime Data for {district}, {state} (2024)')

        # Crime Severity Score Calculation
        crime_weights = {
            'murder': 10,
            'rape': 6,
            'kidnapping & abduction': 5,
            'robbery': 4,
            'burglary': 3,
            'dowry deaths': 4
        }

        def calculate_crime_severity(df):
            weighted_sum = sum(df[col].sum() * weight for col, weight in crime_weights.items())
            max_possible = sum(500 * weight for weight in crime_weights.values())  # Hypothetical normalization factor
            crime_index = (weighted_sum / max_possible) * 100 if max_possible > 0 else 0
            return round(crime_index, 2)

        crime_severity_index = calculate_crime_severity(filtered_data)
        st.metric(label="Crime Severity Index (Higher is riskier)", value=crime_severity_index)

        # Updated Risk Thresholds
        if crime_severity_index < 25:
            st.success("🟢 This area is relatively safe.")
        elif 25 <= crime_severity_index <= 55:
            st.warning("🟠 Moderate risk; stay cautious.")
        else:
            st.error("🔴 High risk! Precaution is advised.")

        # Crime Hotspot Map (without markers)
        st.subheader('Crime Hotspot Map')

        # Lookup latitude and longitude from location_data
        location_row = location_data[
            (location_data['State'] == state) & 
            (location_data['District'] == district)
        ]

        if not location_row.empty:
            latitude, longitude = location_row.iloc[0]['Latitude'], location_row.iloc[0]['Longitude']

            m = folium.Map(location=[latitude, longitude], zoom_start=10)
            folium_static(m)
        else:
            st.warning("Coordinates for the selected district were not found.")
