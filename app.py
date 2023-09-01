import streamlit as st
import pandas as pd
import folium
import joblib
import datetime

from streamlit_folium import folium_static
from PIL import Image

# Define a function to convert datetime to date
def datetime_to_date(df):
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.day_of_week
    return df[['month', 'day_of_week']]

pipeline =joblib.load("rff_model2.joblib")

# Title
st.title('Fishing Worldwide')

# Static Map of fishing events around the world
st.markdown('''
Below is a map of sample fishing events around the world 🗺''')
image = Image.open('output.png')
st.image(image, caption='Fishing events around the World')

st.subheader('Our goal is to map the trajectory of the boat and identify fishing events')

# Upload csv information
st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.markdown('''Check your data before proceeding''')
    st.write(data)

    if st.button(":fishing_pole_and_fish:  Check this boat  :fishing_pole_and_fish:"):
        st.write('🟢 Not fishing | 🔴 Fishing')

        # Extract lattitude and longitude from Dataframe
        #data['is_fishing'] = pipeline.predict(data)
        data['is_fishing'] = pipeline.predict(data)
        place_lat=data["lat"].tolist()
        place_lng=data["lon"].tolist()
        num = round(len(place_lat)/2)

        # Create folium map
        base_map = folium.Map(location=[place_lat[num], place_lng[num]], control_scale=True)

        # Get coordinates for fishing events
        df_fishing = data[data['is_fishing']==1]
        fishing = list(zip(df_fishing.lat, df_fishing.lon))

        # Get coordinates for fishing events
        df_not_fishing = data[data['is_fishing']==0]
        not_fishing = list(zip(df_not_fishing.lat, df_not_fishing.lon))

        # Create markers for each fishing event
        for fish in fishing:
            icon=folium.Icon(color='white', icon_color="red")
            folium.Marker(fish, icon=icon).add_to(base_map)

        for notfish in not_fishing:
            icon=folium.Icon(color='white', icon_color="green")
            folium.Marker(notfish, icon=icon).add_to(base_map)

        # Create line that connect points
        points = []
        for i in range(len(place_lat)):
            points.append([place_lat[i], place_lng[i]])
        folium.PolyLine(locations=points, color='yellow').add_to(base_map)

        # Bounds to autozom map autozooms
        sw = data[['lat', 'lon']].min().values.tolist()
        ne = data[['lat', 'lon']].max().values.tolist()
        base_map.fit_bounds([sw, ne])

        # Displays map
        folium_static(base_map)
        st.write(data)
