import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Custom CSS for better styling
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        border: 2px solid #ddd;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 2px 4px 6px rgba(0,0,0,0.1);
    }
    .title {
        color: #4a90e2;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        color: gray;
        margin-top: 20px;
    }
    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
    }
    .warning-alert {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
    }
    .danger-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Load the datasets
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

# App state management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'state' not in st.session_state:
    st.session_state.state = None
if 'district' not in st.session_state:
    st.session_state.district = None

# Login Page
if not st.session_state.logged_in:
    with st.container():
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Crime Safety Insights 🚨</div>", unsafe_allow_html=True)
        
        name = st.text_input("👤 Enter your Name")
        gender = st.radio("🧍 Select Gender", ['Male', 'Female', 'Other'])
        age = st.number_input("📅 Enter your Age", min_value=1, max_value=120, value=25)
        
        if st.button("🔐 Login"):
            if name.strip() and gender:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.success(f"Welcome, {name}!")
            else:
                st.error("Please enter all required fields.")
else:
    # Input Page for State and District
    st.markdown(f"### Hello {st.session_state.user_name}, Let's Select Your Region 📍")

    state = st.selectbox('Select State/UT:', crime_data['state/ut'].unique())
    districts = crime_data[crime_data['state/ut'] == state]['district'].unique()
    district = st.selectbox('Select District:', districts)

    if st.button('Show Crime Data'):
        st.session_state.state = state
        st.session_state.district = district

        filtered_data = crime_data[
            (crime_data['state/ut'] == state) &
            (crime_data['district'] == district) &
            (crime_data['year'] == 2024)
        ]

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
            max_possible = sum(500 * weight for weight in crime_weights.values())
            crime_index = (weighted_sum / max_possible) * 100 if max_possible > 0 else 0
            return round(crime_index, 2)

        crime_severity_index = calculate_crime_severity(filtered_data)
        st.metric(label="Crime Severity Index (Higher is riskier)", value=crime_severity_index)

        # Updated Risk Thresholds with better interface
        if crime_severity_index < 25:
            st.markdown("<div class='success-alert'>🟢 This area is relatively safe.</div>", unsafe_allow_html=True)
        elif 25 <= crime_severity_index <= 55:
            st.markdown("<div class='warning-alert'>🟠 Moderate risk; stay cautious.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='danger-alert'>🔴 High risk! Precaution is advised.</div>", unsafe_allow_html=True)

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
