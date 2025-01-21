import streamlit as st
import pandas as pd

# Load the .pkl file
@st.cache_data
def load_data():
    return pd.read_pickle('/content/crime_data.pkl')

# Set up the Streamlit app
st.title('Crime Data Analysis')

# Load the data
data = load_data()

# Display the state selection
state = st.selectbox('Select State/UT:', data['state/ut'].unique())

# Filter districts based on the selected state
districts = data[data['state/ut'] == state]['district'].unique()

# Show the district selection after the state is selected
district = st.selectbox('Select District:', districts)

# Filter the data based on the selected state and district
filtered_data = data[(data['state/ut'] == state) & (data['district'] == district)]

# Display the selected data
st.subheader(f'Crime Data for {district} ({state})')
st.dataframe(filtered_data)

# Show summary statistics for the selected data
if st.checkbox('Show summary statistics'):
    st.subheader('Summary Statistics')
    st.write(filtered_data.describe())
