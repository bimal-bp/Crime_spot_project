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

# Capitalize the state and district names
data['state/ut'] = data['state/ut'].str.title()
data['district'] = data['district'].str.title()

# Convert the year to integer to remove the quotes
data['year'] = data['year'].astype(int)

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
