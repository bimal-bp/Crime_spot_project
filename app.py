import streamlit as st
import pandas as pd

# Load the .pkl file
@st.cache_data
def load_data():
    return pd.read_pickle('crime_data.pkl')

# Set up the Streamlit app
st.title('Crime Data Analysis')

# Load the data
data = load_data()

# Clean up the crime incidents column by removing commas and quotes, then convert to integers
data['crime_incidents'] = data['crime_incidents'].replace(r'"', '', regex=True)  # Remove quotation marks
data['crime_incidents'] = data['crime_incidents'].replace(r',', '', regex=True)  # Remove commas
data['crime_incidents'] = data['crime_incidents'].astype(int)  # Convert to integer

# Example function to give safety insights based on the crime data
def safety_insight(state, district):
    # Filter the data for the selected location (state, district)
    location_data = data[(data['state/ut'] == state) & (data['district'] == district)]
    
    if not location_data.empty:
        latest_data = location_data.iloc[-1]  # Get the most recent data
        crime_incidents = latest_data['crime_incidents']
        
        # Provide a safety insight based on the number of incidents
        if crime_incidents > 100:
            return "This area has had significant criminal incidents in recent years. Stay vigilant and follow safety precautions."
        elif crime_incidents > 50:
            return "This area has moderate criminal activity. Be aware of your surroundings and take necessary precautions."
        else:
            return "The crime rate in this area appears to be relatively low. However, it's always best to stay cautious."
    else:
        return "No crime data available for the selected location."

# Page selection using a button
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Home page: Display the state and district selection
if st.session_state.page == 'Home':
    state = st.selectbox('Select State/UT:', data['state/ut'].unique())

    # Filter districts based on the selected state
    districts = data[data['state/ut'] == state]['district'].unique()

    # Show the district selection after the state is selected
    district = st.selectbox('Select District:', districts)

    # Button to proceed to the next page and show the results
    if st.button('Show Crime Data'):
        # Save the selected state and district in session state
        st.session_state.state = state
        st.session_state.district = district
        st.session_state.page = 'Crime Data'  # Switch to the second page

        # Display safety insights
        safety_message = safety_insight(state, district)
        st.write(safety_message)

# Crime Data page: Display the filtered data and summary statistics
if st.session_state.page == 'Crime Data':
    # Retrieve the selected state and district from session state
    state = st.session_state.state
    district = st.session_state.district

    # Filter the data based on the selected state, district, and the last 4 years (2021-2024)
    filtered_data = data[(data['state/ut'] == state) & 
                         (data['district'] == district) & 
                         (data['year'].isin([2021, 2022, 2023, 2024]))]

    # Display the selected data on the second page
    st.subheader(f'Crime Data for {district} ({state})')
    st.dataframe(filtered_data)

    # Show summary statistics for the selected data
    if st.checkbox('Show summary statistics'):
        st.subheader('Summary Statistics')
        st.write(filtered_data.describe())

    # Button to go back to the first page
    if st.button('Go Back'):
        st.session_state.page = 'Home'
