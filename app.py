import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from statsmodels.tsa.arima.model import ARIMA

# Load the dataset and aggregated district coordinates
@st.cache_data
def load_data():
    crime_data = pd.read_pickle('crime_data.pkl')
    location_data = pd.read_pickle('state_district_lat_long.pkl')
    return crime_data, location_data

crime_data, location_data = load_data()

# Capitalize state and district names for consistency
crime_data['state/ut'] = crime_data['state/ut'].str.title()
crime_data['district'] = crime_data['district'].str.title()

# Page selection state management
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Home page - State and District selection
if st.session_state.page == 'Home':
    st.title('Crime Data Analysis & Safety Insights')

    state = st.selectbox('Select State/UT:', crime_data['state/ut'].unique())
    districts = crime_data[crime_data['state/ut'] == state]['district'].unique()
    district = st.selectbox('Select District:', districts)

    if st.button('Show Crime Data'):
        st.session_state.state = state
        st.session_state.district = district
        st.session_state.page = 'Crime Data'

# Crime Data Page - Display insights and analysis
if st.session_state.page == 'Crime Data':
    state = st.session_state.state
    district = st.session_state.district

    # Filter the crime data
    filtered_data = crime_data[
        (crime_data['state/ut'] == state) &
        (crime_data['district'] == district) &
        (crime_data['year'].isin([2023, 2024]))
    ]

    st.subheader(f'Crime Data for {district}, {state}')

    # Crime Severity Score Calculation
    crime_weights = {
        'murder': 5,
        'rape': 4,
        'kidnapping & abduction': 4,
        'robbery': 3,
        'burglary': 2,
        'dowry deaths': 3
    }

    def calculate_crime_severity(df):
        weighted_sum = sum(df[col].sum() * weight for col, weight in crime_weights.items())
        max_possible = sum(df[col].max() * weight for col, weight in crime_weights.items())
        crime_index = (weighted_sum / max_possible) * 100 if max_possible else 0
        return round(crime_index, 2)

    crime_severity_index = calculate_crime_severity(filtered_data)
    st.metric(label="Crime Severity Index (Higher is riskier)", value=crime_severity_index)

    if crime_severity_index < 40:
        st.success("🟢 This area is relatively safe.")
    elif crime_severity_index < 70:
        st.warning("🟠 Moderate risk; stay cautious.")
    else:
        st.error("🔴 High risk! Precaution is advised.")

    # Crime Frequency Analysis
    st.subheader('Crime Distribution')
    crime_types = ['murder', 'rape', 'kidnapping & abduction', 'robbery', 'burglary', 'dowry deaths']
    crime_frequencies = filtered_data[crime_types].sum().sort_values(ascending=False)
    st.bar_chart(crime_frequencies)

    # Crime Trend Visualization (2021-2024) - All trends in one graph
    st.subheader('Crime Trends Over the Years')
    trend_data = crime_data[(crime_data['state/ut'] == state) & (crime_data['district'] == district) & (crime_data['year'].isin([2021, 2022, 2023, 2024]))]
    
    plt.figure(figsize=(10, 6))
    for crime in crime_types:
        crime_sum_by_year = trend_data.groupby('year')[crime].sum()
        plt.plot(crime_sum_by_year.index, crime_sum_by_year.values, label=crime)
    
    plt.title(f'Crime Trends for {district}, {state} (2021-2024)')
    plt.xlabel('Year')
    plt.ylabel('Crime Count')
    plt.legend(title="Crime Types")
    st.pyplot(plt)

    # Interactive Crime Hotspot Map
    st.subheader('Crime Hotspot Map')

    # Lookup latitude and longitude from location_data
    location_row = location_data[
        (location_data['State'].str.lower() == state.lower()) & 
        (location_data['District'].str.lower() == district.lower())
    ]

    if not location_row.empty:
        latitude, longitude = location_row.iloc[0]['Latitude'], location_row.iloc[0]['Longitude']
        
        m = folium.Map(location=[latitude, longitude], zoom_start=10)
        
        for idx, row in filtered_data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{district} Crimes: {row['murder']} murders"
            ).add_to(m)
        
        folium_static(m)
    else:
        st.warning("Coordinates for the selected district were not found.")

    # Safety Recommendations
    st.subheader('Safety Recommendations')
    if crime_frequencies['murder'] > 50:
        st.warning("🔴 Avoid high-crime areas at night and stay vigilant.")
    if crime_frequencies['rape'] > 30:
        st.warning("⚠️ Travel in groups and use verified transport services.")
    if crime_frequencies['burglary'] > 100:
        st.warning("🏠 Install security systems and inform neighbors when away.")

    # Back Button
    if st.button('Go Back'):
        st.session_state.page = 'Home'
