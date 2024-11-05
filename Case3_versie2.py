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

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️', layout='wide', initial_sidebar_state='expanded')

# Sidebar
with st.sidebar: 
    st.sidebar.header('Dashboard `versie 2`')
    # Hoofdmenu-opties
    selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], 
                           icons=["play", "airplane", "bezier"], menu_icon="list")

    # Submenu voor "Vluchten"
    if selected == "Vluchten":
        vlucht_selected = option_menu(
            menu_title="Kies een vlucht",
            options=["Vlucht 1", "Vlucht 2", "Vlucht 3", "Vlucht 4", "Vlucht 5", "Vlucht 6", "Vlucht 7"],
            menu_icon="airplane",
            default_index=0
        )
        # Sla de geselecteerde vlucht op in de sessiestatus
        st.session_state.selected_vlucht = vlucht_selected.lower()

# --------------------------------------------------------------------------

# INTRO pagina
if selected == 'Intro':
    st.title("Case 3 Vluchten - Groep 3")
    st.write("""
        (uitleg...)
    """)
    st.write("#### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
        - [Uitstoot data](https://ecotree.green/nl/calculate-flight-co2#result)
        - [Max. aantal passagiers (KLM - Boeing 737)](https://www.klm.nl/information/travel-class-extra-options/aircraft-types/boeing-737-800)
    """)

# --------------------------------------------------------------------------
    
# VLUCHTEN pagina
elif selected == "Vluchten": 
    st.title("Vluchten")
    st.header("De 7 vluchten van AMS naar BCN")
    st.subheader("    ")
    # Controleer of er al een geselecteerde vlucht is opgeslagen in de sessie
    if "selected_vlucht" not in st.session_state:
        st.session_state.selected_vlucht = "vlucht 1"  # Standaard selecteren we de eerste vlucht 

    vlucht_info = {
        'vlucht 1': {'afstand': '1323', 'duur': '2.14'},
        'vlucht 2': {'afstand': '1314', 'duur': '1.75'},
        'vlucht 3': {'afstand': '1339', 'duur': '2.19'},
        'vlucht 4': {'afstand': '1289', 'duur': '1.93'},
        'vlucht 5': {'afstand': '1292', 'duur': '2.02'},
        'vlucht 6': {'afstand': '1290', 'duur': '1.74'},
        'vlucht 7': {'afstand': '1281', 'duur': '1.81'}
    }

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

    # Parameters voor uitstootberekening
    emissiefactor = 0.190    # kg CO₂ per passagier per km
    aantal_passagiers = 186

    # Haal de geselecteerde dataframe op uit sessiestatus
    selected_vlucht = st.session_state.selected_vlucht
    df1 = vluchten_data[selected_vlucht]
    afstand = int(vlucht_info[selected_vlucht]['afstand']) 
    duur = vlucht_info[selected_vlucht]['duur']
    uitstoot = afstand * emissiefactor * aantal_passagiers

    # Zorg ervoor dat de kolom 'TRUE AIRSPEED (derived)' numeriek is
    df1['TRUE AIRSPEED (derived)'] = pd.to_numeric(df1['TRUE AIRSPEED (derived)'], errors='coerce')

    # Bereken metrics
    max_hoogte = df1['[3d Altitude Ft]'].max()
    max_snelheid = df1['TRUE AIRSPEED (derived)'].max()

    # Plaats metrics en kaart naast elkaar
    metrics_col, map_col = st.columns([1, 2])

    with metrics_col:
        st.metric("Maximale Hoogte (ft)", max_hoogte)
        st.metric("Maximale Snelheid (kts)", max_snelheid)
        st.metric("Totale Afstand (km)", afstand)
        st.metric("Totale Tijd (uur)", duur)
        st.metric("Uitstoot (kg CO₂)", f"{uitstoot:.2f}")

    with map_col:
        # Maak een lijst van coördinaten (Latitude, Longitude) en de hoogte
        coordinates = list(zip(df1['[3d Latitude]'], df1['[3d Longitude]'], df1['[3d Altitude Ft]']))
        #mid_lat = df1['[3d Latitude]'].mean()
        #mid_lon = df1['[3d Longitude]'].mean()
        m = folium.Map(location=[48.0666, 3.1462], zoom_start=5, tiles='CartoDB positron')

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
            tooltip="AMSTERDAM (AMS)",
            icon=folium.Icon(icon="plane", prefix="fa")
        ).add_to(m)

        folium.Marker(
            location=[df1['[3d Latitude]'].iloc[-1], df1['[3d Longitude]'].iloc[-1]],
            popup="BARCELONA (BCN)",
            tooltip="BARCELONA (BCN)",
            icon=folium.Icon(icon="plane", prefix="fa")
        ).add_to(m)

        colormap.add_to(m)
        st_folium(m, width=600, height=550) 


    # --------------------------------------

    # Voeg 'ALL' toe aan de opties voor het dropdownmenu
    selected_vlucht = st.selectbox("Selecteer een vlucht", options=['ALL'] + [f'vlucht {i}' for i in range(1, 8)])

    # Combineer data van alle vluchten indien 'ALL' is geselecteerd en voeg een kolom toe om de vlucht te labelen
    if selected_vlucht == 'ALL':
        df_all = pd.concat([df.assign(vlucht=vlucht) for vlucht, df in vluchten_data.items()], ignore_index=True)
        df1 = df_all
    else:
        df1 = vluchten_data[selected_vlucht]
        df1['vlucht'] = selected_vlucht  # Voeg een kolom toe om de vlucht te labelen

    # Tijd omzetten van seconden naar uren
    df1['Time (hours)'] = df1['Time (secs)'] / 3600

    # Specifieke kleuren toewijzen aan elke vlucht
    kleuren_map = {
        'vlucht 1': 'red',
        'vlucht 2': 'green',
        'vlucht 3': 'blue',
        'vlucht 4': 'orange',
        'vlucht 5': 'purple',
        'vlucht 6': 'brown',
        'vlucht 7': 'pink'
    }

    # Maak de lijnplot met verbeteringen
    fig = px.line(
        df1, 
        x='Time (hours)', 
        y='[3d Altitude Ft]', 
        title='Hoogte vs Tijd',  
        labels={"Time (hours)": "Tijd (uren)", "[3d Altitude Ft]": "Hoogte (ft)"},
        color='vlucht',  
        color_discrete_map=kleuren_map
    )

    fig.update_yaxes(range=[0, 40000], dtick=5000)

    # Interactieve legenda
    fig.update_layout(
        legend_title_text="Vlucht",
        legend=dict(
            itemclick="toggleothers",
            itemdoubleclick="toggle"
        )
    )
    # Toon de grafiek in Streamlit
    st.plotly_chart(fig)

# --------------------------------------------------------------------------
if selected == 'Luchthavens':
    st.title("Luchthavens") 

    # Maak drie kolommen voor de metrics
    col1, col2, col3 = st.columns(3)
    
    # Fictieve percentages
    te_vroeg_percentage = 15  # Fictief percentage voor "Te vroeg"
    op_tijd_percentage = 70   # Fictief percentage voor "Op tijd"
    te_laat_percentage = 15   # Fictief percentage voor "Te laat"
    
    # Toon de metrics
    with col1:
        st.metric(label="Te vroeg", value=f"{te_vroeg_percentage}%", delta="5%", delta_color="inverse")  # Blauw
    with col2:
        st.metric(label="Op tijd", value=f"{op_tijd_percentage}%", delta="0%", delta_color="normal")  # Groen
    with col3:
        st.metric(label="Te laat", value=f"{te_laat_percentage}%", delta="-3%", delta_color="inverse")  # Rood
   






