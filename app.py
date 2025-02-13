import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

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
    'murder': 5,
    'rape': 4,
    'kidnapping & abduction': 4,
    'robbery': 3,
    'burglary': 3,
    'dowry deaths': 3
}

def calculate_crime_severity(df):
    weighted_sum = sum(df[col].sum() * weight for col, weight in crime_weights.items())
    max_possible = sum(500 * weight for weight in crime_weights.values())
    crime_index = (weighted_sum / max_possible) * 100 if max_possible > 0 else 0
    return round(crime_index, 2)

# User Input: Select State
st.title("🌍 Crime Risk Analysis for All Districts in a State")
state = st.selectbox('Select a State/UT:', crime_data['state/ut'].unique())

if state:
    # Filter data for the selected state
    state_data = crime_data[crime_data['state/ut'] == state]
    
    # Compute crime severity for each district
    district_severity = {}
    for district in state_data['district'].unique():
        district_data = state_data[state_data['district'] == district]
        district_severity[district] = calculate_crime_severity(district_data)
    
    # Display as DataFrame
    df = pd.DataFrame(list(district_severity.items()), columns=['District', 'Crime Severity Index'])
    st.dataframe(df)
    
    # Map Visualization
    st.subheader("Crime Hotspot Map for All Districts")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=6)  # Center map on India
    
    for district, severity in district_severity.items():
        location_row = location_data[(location_data['State'] == state) & (location_data['District'] == district)]
        if not location_row.empty:
            lat, lon = location_row.iloc[0]['Latitude'], location_row.iloc[0]['Longitude']
            
            # Assign colors based on severity index
            if severity < 25:
                color = 'green'
            elif 25 <= severity <= 55:
                color = 'orange'
            else:
                color = 'red'
            
            # Add CircleMarker to the map
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{district}: {severity}"
            ).add_to(m)
    
    folium_static(m)
