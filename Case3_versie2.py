import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from folium.plugins import HeatMap


st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# sidebar
with st.sidebar: 
  st.sidebar.header('Dashboard `versie 2`')
  selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], icons=["play", "airplane", "bezier"], menu_icon="list")

# --------------------------------------------------------------------------

# INTRO pagina
if selected == 'Intro':
    st.title("Case 3 Vluchten - Groep 3")

    # Korte uitleg
    st.write("""
        (uitleg...)
    """)
  
    # Bronnen
    st.write("#### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
    """)

# --------------------------------------------------------------------------

# VLUCHTEN pagina
# Controleer of er al een geselecteerde vlucht is opgeslagen in de sessie
if "selected_vlucht" not in st.session_state:
    st.session_state.selected_vlucht = "vlucht 1"  # Standaard selecteren we de eerste vlucht

# Laad de 7 Excel-bestanden in een dictionary
vluchten_data = {
    'vlucht 1': pd.read_excel('30Flight 1.xlsx'),
    'vlucht 2': pd.read_excel('cleaned_30Flight 2.xlsx'),
    'vlucht 3': pd.read_excel('cleaned_30Flight 3.xlsx'),
    'vlucht 4': pd.read_excel('cleaned_30Flight 4.xlsx'),
    'vlucht 5': pd.read_excel('30Flight 5.xlsx'),
    'vlucht 6': pd.read_excel('cleaned_30Flight 6.xlsx'),
    'vlucht 7': pd.read_excel('30Flight 7.xlsx')
}

# Maak knoppen voor elke vlucht en update sessiestatus bij klikken
vlucht_knoppen = st.columns([1, 1, 1, 1, 1, 1, 1])
for i, (label, data) in enumerate(vluchten_data.items()):
    if vlucht_knoppen[i].button(f"{label.capitalize()}"):
        st.session_state.selected_vlucht = label

# Haal de geselecteerde dataframe op uit sessiestatus
selected_vlucht = st.session_state.selected_vlucht
df1 = vluchten_data[selected_vlucht]

# Zorg ervoor dat de kolom 'TRUE AIRSPEED (derived)' numeriek is
df1['TRUE AIRSPEED (derived)'] = pd.to_numeric(df1['TRUE AIRSPEED (derived)'], errors='coerce')

# Bereken metrics
max_hoogte = df1['[3d Altitude Ft]'].max()
max_snelheid = df1['TRUE AIRSPEED (derived)'].max()
totale_afstand = "Totale afstand placeholder"  # Invullen met daadwerkelijke berekening
totale_tijd = "Totale tijd placeholder"  # Invullen met daadwerkelijke berekening

# Plaats metrics en kaart naast elkaar
metrics_col, map_col = st.columns([1, 2])

with metrics_col:
    st.metric("Maximale Hoogte (ft)", max_hoogte)
    st.metric("Maximale Snelheid (kts)", max_snelheid)
    st.metric("Totale Afstand", totale_afstand)
    st.metric("Totale Tijd", totale_tijd)

with map_col:
    # Maak een lijst van coördinaten (Latitude, Longitude) en de hoogte
    coordinates = list(zip(df1['[3d Latitude]'], df1['[3d Longitude]'], df1['[3d Altitude Ft]']))
    mid_lat = df1['[3d Latitude]'].mean()
    mid_lon = df1['[3d Longitude]'].mean()
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=5, tiles='CartoDB positron')

    # Creëer een colormap op basis van hoogte
    colormap = cm.LinearColormap(colors=['yellow', 'green', 'turquoise', 'blue', 'purple'], 
                                 index=[0, 10000, 20000, 30000, 40000],
                                 vmin=df1['[3d Altitude Ft]'].min(), 
                                 vmax=df1['[3d Altitude Ft]'].max(),
                                 caption='Hoogte in ft.')

    # Voeg de lijn toe, waarbij de kleur afhangt van de hoogte
    for i in range(1, len(coordinates)):
        start = coordinates[i-1]
        end = coordinates[i]
        color = colormap(start[2])
        folium.PolyLine(
            locations=[[start[0], start[1]], [end[0], end[1]]],
            color=color, 
            weight=2.5, 
            opacity=1,
            tooltip=f"Time: {df1['Time (secs)'].iloc[i]} sec, Altitude: {df1['[3d Altitude Ft]'].iloc[i]} ft, Speed: {df1['TRUE AIRSPEED (derived)'].iloc[i]} kts"
        ).add_to(m)

    # Marker voor AMS en BCN
    folium.Marker(
        location=[df1['[3d Latitude]'].iloc[0], df1['[3d Longitude]'].iloc[0]],
        popup="AMSTERDAM (AMS)",
        tooltip="AMSTERDAM (AMS)"
    ).add_to(m)

    folium.Marker(
        location=[df1['[3d Latitude]'].iloc[-1], df1['[3d Longitude]'].iloc[-1]],
        popup="BARCELONA (BCN)",
        tooltip="BARCELONA (BCN)"
    ).add_to(m)

    colormap.add_to(m)
    st_folium(m, width=700, height=600)


