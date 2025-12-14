import streamlit as st
import plotly.express as px
import pandas as pd

# Set page configuration
st.set_page_config(page_title="My Travel Map", page_icon="🌎", layout="wide")

st.title("🌎 My Travel Tracker")
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

# 2. List of Countries (using ISO-3 code for better mapping, or standard names)
# Plotly Express's 'gapminder' dataset is a quick way to get country names/ISOs
all_countries = px.data.gapminder()['country'].unique().tolist()

# -- SIDEBAR SELECTION --
map_type = st.sidebar.radio("Select Map Scope", ["USA States", "World Countries"])

if map_type == "USA States":
    st.sidebar.header("🇺🇸 Select States Visited")
    # Multi-select for states
    visited_states = st.sidebar.multiselect(
        "Choose states:", 
        options=us_states,
        default=["MA", "NY", "CA"] # Pre-selected examples
    )
    
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
        hover_name="State",
        hover_data={'Visited': False, 'State': False}
    )
    fig.update_layout(coloraxis_showscale=False, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    st.info(f"You have visited **{len(visited_states)}** out of 50 states ({len(visited_states)/50:.1%}).")


elif map_type == "World Countries":
    st.sidebar.header("🌍 Select Countries Visited")
    # Multi-select for countries
    visited_countries = st.sidebar.multiselect(
        "Choose countries:", 
        options=all_countries,
        default=["United States", "Austria", "Denmark"] # Pre-selected examples
    )
    
    # Create DataFrame for plotting
    df_countries = pd.DataFrame({"Country": all_countries})
    df_countries['Visited'] = df_countries['Country'].apply(lambda x: 1 if x in visited_countries else 0)
    
    # Plot World Map
    fig = px.choropleth(
        df_countries,
        locations='Country',
        locationmode='country names',
        color='Visited',
        color_continuous_scale=["#f0f2f6", "#636efa"], # Light grey to Blue
        range_color=(0, 1),
        title="Countries I Have Visited",
        hover_name="Country",
        hover_data={'Visited': False, 'Country': False}
    )
    fig.update_layout(coloraxis_showscale=False, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    st.info(f"You have visited **{len(visited_countries)}** countries.")