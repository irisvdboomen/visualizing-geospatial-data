import streamlit as st
import osmnx as ox
import folium
from streamlit_folium import st_folium

# List of provinces in the Netherlands with their approximate center coordinates
province_centers = {
    'Drenthe': [52.9476, 6.6239],
    'Flevoland': [52.5279, 5.5954], 
    'Friesland': [53.1642, 5.7818],
    'Gelderland': [52.0452, 5.8718],
    'Groningen': [53.2194, 6.5665],
    'Limburg': [51.4427, 6.0609],
    'Noord-Brabant': [51.4827, 5.2322],
    'Noord-Holland': [52.5206, 4.7885],
    'Overijssel': [52.4388, 6.5016],
    'Zuid-Holland': [51.9054, 4.5469],
    'Utrecht': [52.0907, 5.1214],
    'Zeeland': [51.4940, 3.8497],
    'All': [52.1326, 5.2913]  # Default coordinates for the Netherlands
}

# Colors and tags for different amenities
facility_types = {
    'school': {
        'tags': ['school', 'kindergarten', 'university', 'college'],
        'colors': {
            'school': 'blue',
            'kindergarten': 'green',
            'university': 'purple',
            'college': 'orange'
        }
    },
    'healthcare': {
        'tags': ['doctors', 'hospital', 'clinic', 'pharmacy'],
        'colors': {
            'doctors': 'blue',
            'hospital': 'green',
            'clinic': 'purple',
            'pharmacy': 'orange'
        }
    }
}

@st.cache_data()
def display_map(location, facility_type, specific_tags):
    location_query = 'Netherlands' if location == 'All' else f"{location}, Netherlands"
    
    center = province_centers.get(location, province_centers['All'])
    m = folium.Map(location=center, zoom_start=7.5 if location == 'All' else 10)

    for specific_tag in specific_tags:
        try:
            gdf = ox.geometries_from_place(location_query, {'amenity': specific_tag})
        except Exception as e:
            st.warning(f"Could not fetch data for {specific_tag} in {location}: {e}")
            continue

        color = facility_types[facility_type]['colors'][specific_tag]
        for idx, row in gdf.iterrows():
            point = row.geometry.centroid if hasattr(row.geometry, 'centroid') else row.geometry
            folium.CircleMarker(
                location=[point.y, point.x],
                radius=3,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{specific_tag.capitalize()}: {row.get('name', 'Unknown')}"
            ).add_to(m)

    return m

# Streamlit app setup
st.title('Amenities map in the Netherlands')

# Selecting the province, amenity type, and specific amenities
selected_province = st.selectbox('Select province:', ['All'] + list(province_centers.keys()), index=0)
facility_type = st.selectbox('Select amenity type:', list(facility_types.keys()))
selected_tags = st.multiselect('Select specific amenity:', facility_types[facility_type]['tags'])

# Explanation of the app
st.markdown("""
**Welcome to the amenities map of the Netherlands!**

This interactive tool allows you to explore various amenities, such as schools and healthcare facilities, across different provinces of the Netherlands. Simply follow these steps to get started:

1. **Choose a province**: Select a province to view the amenities in that area. You can also select 'All' to view amenities across the entire Netherlands.
2. **Select an amenity type**: Choose the type of amenity you're interested in, such as schools or healthcare facilities.
3. **Select specific amenities**: Narrow down your search by selecting specific types of the chosen amenity, for example, universities or hospitals.

The map will automatically update based on your selections. You can click on the colored markers to get more information about each amenity. The legend on the side will show which colors are associated with each type of amenity.

Zoom levels are adjusted automatically for a clearer view: a closer zoom for individual provinces and a broader view for the entire country. Explore the map to discover the amenities available in different parts of the Netherlands.

Enjoy exploring!
""")

with st.spinner('Fetching and displaying data...'):
    location = selected_province if selected_province in province_centers else 'All' 
    map_to_show = display_map(location, facility_type, selected_tags) 
    st_folium(map_to_show, width=700)

# Sidebar legend for facility types
st.sidebar.header(f"{facility_type.capitalize()} facilities legend")
for selected_tag in selected_tags:
    color = facility_types[facility_type]['colors'][selected_tag]
    st.sidebar.markdown(f"<span style='display: inline-block; width: 12px; height: 12px; background-color: {color}; margin-left: 1px; margin-right: 12px;'></span>{selected_tag.capitalize()}",
        unsafe_allow_html=True
    )