import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Load the dataset
@st.cache_data
def load_crime_data():
    return pd.read_pickle('crime_data.pkl')

@st.cache_data
def load_location_data():
    return pd.read_pickle('state_district_lat_long.pkl')

crime_data = load_crime_data()
location_data = load_location_data()

crime_data['state/ut'] = crime_data['state/ut'].str.title()
crime_data['district'] = crime_data['district'].str.title()
location_data['State'] = location_data['State'].str.title()
location_data['District'] = location_data['District'].str.title()

# Crime Severity Score Calculation
crime_weights = {
    'murder': 7,
    'rape': 5,
    'kidnapping & abduction': 5,
    'robbery': 3,
    'burglary': 3,
    'dowry deaths': 4
}

def calculate_crime_severity(df):
    weighted_sum = sum(df[col].sum() * weight for col, weight in crime_weights.items())
    max_possible = sum(500 * weight for weight in crime_weights.values())
    crime_index = (weighted_sum / max_possible) * 100 if max_possible > 0 else 0
    return round(crime_index, 2)

# Home Page UI - Login Form
def login_page():
    st.title("🌍 Crime Data Analysis & Safety Insights")
    st.subheader("🔐 Please Log in to Continue")

    name = st.text_input("Enter your name:")
    age = st.number_input("Enter your age:", min_value=1, max_value=120)
    gender = st.selectbox("Select your gender:", ["Male", "Female", "Other"])

    if st.button("Proceed to Next Step"):
        if name and age and gender:
            st.session_state.name = name
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.page = 'LocationInputPage'
        else:
            st.warning("Please fill in all the fields.")

# Second Page - Location selection for Crime Analysis
def location_input_page():
    st.title("🌍 Enter Your Location")
    state = st.selectbox('Select State/UT:', crime_data['state/ut'].unique())
    districts = crime_data[crime_data['state/ut'] == state]['district'].unique()
    district = st.selectbox('Select District:', districts)

    if st.button('Proceed to Crime Data Analysis'):
        if state and district:
            st.session_state.state = state
            st.session_state.district = district
            st.session_state.page = 'CrimeAnalysisPage'
        else:
            st.warning("Please select both state and district.")

# Crime Analysis Page - Crime Data Display
def crime_analysis_page():
    st.title("🔍 Crime Data Analysis for Selected Location")

    state = st.session_state.state
    district = st.session_state.district

    filtered_data = crime_data[
        (crime_data['state/ut'] == state) & 
        (crime_data['district'] == district)
    ]

    # Calculate Crime Severity Index for 2022, 2023, and 2024
    trend_data = {}
    for year in [2022, 2023, 2024]:
        yearly_data = filtered_data[filtered_data['year'] == year]
        trend_data[year] = calculate_crime_severity(yearly_data)

    # Display Crime Severity Index for 2024
    crime_severity_index = trend_data[2024]
    st.metric(label="Crime Severity Index (Higher is riskier)", value=crime_severity_index)

    # Crime Severity Trend Line Chart
    st.subheader("Crime Severity Trend (2022 - 2024)")
    st.line_chart(pd.DataFrame(trend_data, index=["Crime Severity Index"]).T)

    # Risk Assessment and Recommendations
    if crime_severity_index < 25:
        st.markdown("<div class='success-alert'>🟢 This area is relatively safe.</div>", unsafe_allow_html=True)
        st.write("Recommendation: Maintain neighborhood watch programs and increase public awareness.")
    elif 25 <= crime_severity_index <= 55:
        st.markdown("<div class='warning-alert'>🟠 Moderate risk; stay cautious.</div>", unsafe_allow_html=True)
        st.write("Recommendation: Consider additional security measures and community involvement.")
    else:
        st.markdown("<div class='danger-alert'>🔴 High risk! Precaution is advised.</div>", unsafe_allow_html=True)
        st.write("Recommendation: Increase law enforcement presence and community safety initiatives.")

    # Crime Hotspot Map without markers
    st.subheader('Crime Hotspot Map')

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

# Main code for app flow
if 'page' not in st.session_state:
    st.session_state.page = 'LoginPage'

# Page routing based on session state
if st.session_state.page == 'LoginPage':
    login_page()
elif st.session_state.page == 'LocationInputPage':
    location_input_page()
elif st.session_state.page == 'CrimeAnalysisPage':
    crime_analysis_page()
