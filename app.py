import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static, st_folium
from geopy.distance import geodesic

# Load datasets
@st.cache_data
def load_crime_data():
    return pd.read_pickle('crime_data.pkl')

@st.cache_data
def load_location_data():
    return pd.read_pickle('state_district_lat_long.pkl')

crime_data = load_crime_data()
location_data = load_location_data()

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

# 🔹 Create an interactive map to capture user location
st.title("📍 Crime Hotspots: Find Risk Level in Your Area")

m = folium.Map(location=[20.5937, 78.9629], zoom_start=6)

# Use st_folium to capture map clicks
map_data = st_folium(m, height=500, width=700)

# 🔹 Get latitude & longitude when user clicks on map
if map_data and "last_clicked" in map_data:
    user_location = map_data["last_clicked"]
    user_lat, user_lon = user_location["lat"], user_location["lng"]
    
    st.success(f"✅ Selected Location: ({user_lat}, {user_lon})")
    
    # 🔹 Filter crime hotspots within a 5 km radius
    nearby_hotspots = []
    
    for _, row in location_data.iterrows():
        hotspot_lat, hotspot_lon = row["Latitude"], row["Longitude"]
        distance_km = geodesic((user_lat, user_lon), (hotspot_lat, hotspot_lon)).km
        
        if distance_km <= 5:  # 🔥 Filter hotspots within 5 km radius
            severity = calculate_crime_severity(crime_data[crime_data['district'] == row['District']])
            nearby_hotspots.append((row["District"], hotspot_lat, hotspot_lon, severity))
    
    # 🔹 Display the filtered crime hotspots on a map
    if nearby_hotspots:
        st.subheader("🔥 Crime Hotspots within 5 KM Radius")

        crime_map = folium.Map(location=[user_lat, user_lon], zoom_start=14)
        
        # Add the user's location
        folium.Marker(
            location=[user_lat, user_lon], 
            popup="📍 Your Location",
            icon=folium.Icon(color="blue", icon="user")
        ).add_to(crime_map)
        
        # Add hotspots to the map
        for district, lat, lon, severity in nearby_hotspots:
            color = "green" if severity < 5 else "orange" if severity < 15 else "red"
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{district}: {severity}"
            ).add_to(crime_map)
        
        folium_static(crime_map)
    
    else:
        st.warning("⚠️ No crime hotspots found within 5 KM.")

