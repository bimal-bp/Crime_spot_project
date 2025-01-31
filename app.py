import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# State and district selection
st.title('Crime Data Analysis & Safety Insights')

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

    # Updated Crime Severity Score Calculation with New Thresholds
    crime_weights = {
        'murder': 7,
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

    # Updated Thresholds for Safety Messages
    if crime_severity_index < 30:
        st.success("🟢 This area is relatively safe.")
    elif crime_severity_index < 60:
        st.warning("🟠 Moderate risk; stay cautious.")
    else:
        st.error("🔴 High risk! Precaution is advised.")

    # Interactive Crime Hotspot Map
    st.subheader('Crime Hotspot Map')

    # Lookup latitude and longitude from location_data
    location_row = location_data[
        (location_data['State'] == state) & 
        (location_data['District'] == district)
    ]

    if not location_row.empty:
        latitude, longitude = location_row.iloc[0]['Latitude'], location_row.iloc[0]['Longitude']
        
        m = folium.Map(location=[latitude, longitude], zoom_start=10)

        # Check if latitude and longitude columns are available
        if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
            for idx, row in filtered_data.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"{district} Crimes: {row['murder']} murders"
                ).add_to(m)
        else:
            st.warning("Latitude and Longitude information is missing for crime events.")
        
        folium_static(m)
    else:
        st.warning("Coordinates for the selected district were not found.")
