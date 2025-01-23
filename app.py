import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from statsmodels.tsa.arima.model import ARIMA

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_pickle('crime_data.pkl')

data = load_data()

# Capitalize state and district names for consistency
data['state/ut'] = data['state/ut'].str.title()
data['district'] = data['district'].str.title()

# Page selection state management
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Home page - State and District selection
if st.session_state.page == 'Home':
    st.title('Crime Data Analysis & Safety Insights')

    state = st.selectbox('Select State/UT:', data['state/ut'].unique())

    districts = data[data['state/ut'] == state]['district'].unique()
    district = st.selectbox('Select District:', districts)

    if st.button('Show Crime Data'):
        st.session_state.state = state
        st.session_state.district = district
        st.session_state.page = 'Crime Data'

# Crime Data Page - Display insights and analysis
if st.session_state.page == 'Crime Data':
    state = st.session_state.state
    district = st.session_state.district

    filtered_data = data[
        (data['state/ut'] == state) &
        (data['district'] == district) &
        (data['year'].isin([2023, 2024]))
    ]

    st.subheader(f'Crime Data for {district}, {state}')
    st.dataframe(filtered_data)

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
        crime_index = (weighted_sum / max_possible) * 100  # Normalize to a 0-100 scale
        return round(crime_index, 2)

    crime_severity_index = calculate_crime_severity(filtered_data)
    st.metric(label="Crime Severity Index (Higher is riskier)", value=crime_severity_index)

    if crime_severity_index < 40:
        st.success("🟢 This area is relatively safe.")
    elif crime_severity_index < 70:
        st.warning("🟠 Moderate risk; stay cautious.")
    else:
        st.error("🔴 High risk! Precaution is advised.")

    # Crime Trend Visualization (Single Line Graph for 2021-2024)
    st.subheader('Crime Trends Over the Years')
    trend_data = data[
        (data['state/ut'] == state) &
        (data['district'] == district) &
        (data['year'].isin([2021, 2022, 2023, 2024]))
    ].groupby('year')['murder'].sum()
    st.line_chart(trend_data)

    # Crime Frequency Analysis
    st.subheader('Crime Distribution')
    crime_types = ['murder', 'rape', 'kidnapping & abduction', 'robbery', 'burglary', 'dowry deaths']
    crime_frequencies = filtered_data[crime_types].sum().sort_values(ascending=False)
    st.bar_chart(crime_frequencies)

    # Interactive Crime Heatmap
    st.subheader('Crime Hotspot Map')
    m = folium.Map(location=[filtered_data['latitude'].mean(), filtered_data['longitude'].mean()], zoom_start=10)
    for idx, row in filtered_data.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=f"Crime: {row['murder']} Murders").add_to(m)
    folium_static(m)

    # Back Button
    if st.button('Go Back'):
        st.session_state.page = 'Home'
