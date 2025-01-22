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

# Page selection
page = st.sidebar.radio('Select a page:', ['Home', 'Crime Data'])

if page == 'Home':
    # Display the state selection on the first page (Home)
    state = st.selectbox('Select State/UT:', data['state/ut'].unique())

    # Filter districts based on the selected state
    districts = data[data['state/ut'] == state]['district'].unique()

    # Show the district selection after the state is selected
    district = st.selectbox('Select District:', districts)

    # Save the selected state and district in session state
    st.session_state.state = state
    st.session_state.district = district

elif page == 'Crime Data':
    # Check if state and district are selected
    if 'state' in st.session_state and 'district' in st.session_state:
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

    else:
        st.warning('Please select a state and district on the Home page first.')
