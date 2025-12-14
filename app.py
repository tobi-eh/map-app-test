import streamlit as st
import plotly.express as px
import pandas as pd
import extra_streamlit_components as stx

# Page config
st.set_page_config(page_title="Travel Map", page_icon="🌎", layout="wide")

# Constants
SCOPE_US = "USA (States)"
SCOPE_WORLD = "World"
SCOPE_EU = "Europe"

# Reduce whitespace around the main container to maximize map size
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌎 Travel Tracker")
st.write("Mark the places you have visited to visualize them on the map.")

# -- DATA SETUP --
# 1. List of US States
us_states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]
us_states_defaults = [
    "AL", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "LA", 
    "ME", "MD", "MA", "MS", "MT", "NV", "NH", "NJ", 
    "NY", "NC", "OH", "OR", "PA", "RI", "SC", "TX", "UT",
    "VT", "VA", "WA", "WY"
    #
    # "AK","AR", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "MI", 
    # "MN", "MO",  "NE", 
    # "ND", "NM", "OK",  "SD", "TN", "WV", "WI", 
]
countries_euro_defaults = [
    "Austria", "Belgium", "Czechia", "Denmark", "France", "Germany", "Greece",
    "Hungary", "Iceland", "Ireland", "Italy", "Netherlands", "Portugal",
    "Slovak Republic", "Slovenia",  "Spain", "Switzerland", "United Kingdom"
]
countries_world_defaults = countries_euro_defaults + [
    "United States", "Canada", "Egypt", "Japan",  "New Zealand", "Turkey" 
]

# 2. List of Countries (using ISO-3 code for better mapping, or standard names)
# Use a comprehensive ISO-3166 dataset to get all countries and regions:
@st.cache_data
def load_country_data():
    url = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
    df = pd.read_csv(url)
    # Map formal ISO names to common names to match defaults and Plotly's fuzzy matching
    df['name'] = df['name'].replace({
        "United States of America": "United States",
        "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
        "Russian Federation": "Russia",
        "Netherlands, Kingdom of the": "Netherlands",
        "Slovakia": "Slovak Republic",
        "Korea (Republic of)": "South Korea",
        "Viet Nam": "Vietnam",
        "Türkiye": "Turkey",
    })
    return df

df_geo = load_country_data()
all_countries = df_geo['name'].unique().tolist()
europe_countries = df_geo[df_geo['region'] == 'Europe']['name'].unique().tolist()

# SIDEBAR ###########################################################################

map_type = st.sidebar.radio("Map Scope", [SCOPE_US, SCOPE_WORLD, SCOPE_EU])

# COOKIE DEFAULTS ###################################################################
cookie_manager = stx.CookieManager()
cookie_states = cookie_manager.get("visited_states")
cookie_countries = cookie_manager.get("visited_countries")
# Determine defaults: Use cookies if available, otherwise use hardcoded defaults
if map_type == SCOPE_US:
    defaults = cookie_states if cookie_states is not None else us_states_defaults
    defaults = [s for s in defaults if s in us_states] # Ensure validity
else:
    # For countries, use the cookie list (which contains ALL visited countries) or the hardcoded list
    source_list = cookie_countries if cookie_countries is not None else (
        countries_world_defaults if map_type == SCOPE_WORLD else countries_euro_defaults
    )
    current_options = all_countries if map_type == SCOPE_WORLD else europe_countries
    defaults = [c for c in source_list if c in current_options]

# MAIN CONTENT ######################################################################
if map_type == SCOPE_US:
    st.sidebar.header("🇺🇸 Select States Visited")
    # Multi-select for states
    visited_states = st.sidebar.multiselect(
        "Choose states:", 
        options=us_states,
        default=defaults
    )
    
    # Save to cookie if changed
    if cookie_states != visited_states:
        cookie_manager.set("visited_states", visited_states)
    
    # Create DataFrame for plotting
    # We create a dataframe with ALL states, and mark 'Visited' as 1 or 0
    df_states = pd.DataFrame({"State": us_states})
    df_states['Visited'] = df_states['State'].apply(lambda x: 1 if x in visited_states else 0)
    
    # Plot USA Map
    fig = px.choropleth(
        df_states,
        locations='State', 
        locationmode="USA-states",
        color='Visited',
        color_continuous_scale=["#f0f2f6", "#00cc96"], # Light grey to Green
        range_color=(0, 1),
        scope="usa",
        title="States I Have Visited",
        height=800,
        hover_name="State",
        hover_data={'Visited': False, 'State': False}
    )
    fig.update_layout(coloraxis_showscale=False, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    st.info(f"You have visited **{len(visited_states)}** out of 50 states ({len(visited_states)/50:.1%}).")


elif map_type == SCOPE_WORLD or map_type == SCOPE_EU:
    st.sidebar.header("🌍 Select Countries Visited")
    # Multi-select for countries
    countries_show = all_countries if map_type == SCOPE_WORLD else europe_countries
    visited_countries = st.sidebar.multiselect(
        "Choose countries:", 
        options= countries_show,
        default = defaults
    )
    
    # Save to cookie if changed. 
    # Logic: We must preserve visited countries that are NOT currently visible (e.g. Japan when looking at Europe)
    current_full_list = cookie_countries if cookie_countries is not None else []
    # 1. Keep countries that are NOT in the current options (preserved from hidden views)
    preserved_hidden = [c for c in current_full_list if c not in countries_show]
    # 2. Add the currently selected countries
    new_full_list = preserved_hidden + visited_countries
    
    if sorted(current_full_list) != sorted(new_full_list):
        cookie_manager.set("visited_countries", new_full_list)
    
    # Create DataFrame for plotting
    df_countries = pd.DataFrame({"Country": countries_show})
    df_countries['Visited'] = df_countries['Country'].apply(lambda x: 1 if x in visited_countries else 0)
    
    # Plot World Map
    fig = px.choropleth(
        df_countries,
        locations='Country',
        locationmode='country names',
        color='Visited',
        color_continuous_scale=["#f0f2f6", "#636efa"], # Light grey to Blue
        range_color=(0, 1),
        scope="europe" if map_type == SCOPE_EU else "world",
        title="Countries I Have Visited",
        height=800,
        hover_name="Country",
        hover_data={'Visited': False, 'Country': False}
    )
    fig.update_layout(coloraxis_showscale=False, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    st.info(f"You have visited **{len(visited_countries)}** {'European' if map_type == SCOPE_EU else ''} countries.")
