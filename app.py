import pandas as pd
import folium
from IPython.display import display

# Load the DataFrame
df = pd.read_pickle("state_district_lat_long.pkl")

def get_lat_long(state: str, district: str):
    result = df[(df['State'].str.lower() == state.lower()) & (df['District'].str.lower() == district.lower())]
    if not result.empty:
        lat = result['Latitude'].values[0]
        long = result['Longitude'].values[0]
        
        # Apply minor adjustments
        lat_adjusted = lat + 0.02  # Adjust latitude slightly
        long_adjusted = long + 0.02  # Adjust longitude slightly
        
        return lat_adjusted, long_adjusted
    else:
        return None

# Prompt for state and district
state_name = input("Enter the state name: ")
district_name = input("Enter the district name: ")

# Get adjusted latitude and longitude
lat_long = get_lat_long(state_name, district_name)

if lat_long:
    latitude, longitude = lat_long
    print(f"Adjusted Latitude and Longitude for {state_name}, {district_name}: ({latitude}, {longitude})")
    
    # Create a map centered on the adjusted location
    location_map = folium.Map(location=[latitude, longitude], zoom_start=10)

    # Add a marker with the district name as the popup (no icon)
    folium.Marker(
        location=[latitude, longitude],
        popup=district_name  # Display district name as the popup
    ).add_to(location_map)

    # Display the map directly in Colab
    display(location_map)
else:
    print("No data available for the provided state and district.")
