import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# sidebar
with st.sidebar: 
  selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], icons=["play", "airplane", "bezier"], menu_icon="list")


# Intro pagina
if selected == 'Intro':
    st.title("Case 3 Vluchten - Groep 3")

    # Korte uitleg
    st.write("""
        Tekst
    """)
  
    # Bronnen
    st.write("### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
    """)

# Vluchten pagina
if selected == "Vluchten": 
  st.title("7 Vluchten (AMS - BCN)") 

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

  # Dropdownmenu in Streamlit om de vlucht te selecteren
  selected_vlucht = st.selectbox("Selecteer een vlucht", options=[f'vlucht {i}' for i in range(1, 8)])

  # Haal de geselecteerde dataframe op
  df1 = vluchten_data[selected_vlucht]

  # Maak een lijst van coördinaten (Latitude, Longitude) en de hoogte
  coordinates = list(zip(df1['[3d Latitude]'], df1['[3d Longitude]'], df1['[3d Altitude Ft]']))

  # Bereken het gemiddelde van de latitude en longitude om het midden van de vlucht te vinden
  mid_lat = df1['[3d Latitude]'].mean()
  mid_lon = df1['[3d Longitude]'].mean()

  # Creëer een Folium-kaart gecentreerd op het midden van de vlucht
  m = folium.Map(location=[mid_lat, mid_lon], zoom_start=5, tiles='CartoDB positron')

  # Creëer een colormap op basis van hoogte (gebaseerd op de gevraagde kleuren)
  colormap = cm.LinearColormap(colors=['yellow', 'green', 'turquoise', 'blue', 'purple'], 
                               vmin=df1['[3d Altitude Ft]'].min(), vmax=df1['[3d Altitude Ft]'].max())

  # Voeg de lijn toe, waarbij de kleur afhangt van de hoogte
  for i in range(1, len(coordinates)):
      start = coordinates[i-1]
      end = coordinates[i]
    
      # Kleur gebaseerd op de hoogte
      color = colormap(start[2])  # De derde waarde in 'coordinates' is de hoogte
    
      # Voeg polyline toe van het vorige naar het volgende punt met een tooltip voor extra informatie
      folium.PolyLine(
          locations=[[start[0], start[1]], [end[0], end[1]]],
          color=color, 
          weight=2.5, 
          opacity=1,
          tooltip=f"Time: {df1['Time (secs)'].iloc[i]} sec, Altitude: {df1['[3d Altitude Ft]'].iloc[i]} ft, Speed: {df1['TRUE AIRSPEED (derived)'].iloc[i]}"
      ).add_to(m)

  # Voeg een marker toe voor het vertrek vliegveld (AMS - Amsterdam)
  folium.Marker(
      location=[df1['[3d Latitude]'].iloc[0], df1['[3d Longitude]'].iloc[0]],
      popup="AMSTERDAM (AMS)",
      tooltip="AMSTERDAM (AMS)"
  ).add_to(m)

  # Voeg een marker toe voor het aankomst vliegveld (BCN - Barcelona)
  folium.Marker(
      location=[df1['[3d Latitude]'].iloc[-1], df1['[3d Longitude]'].iloc[-1]],
      popup="BARCELONA (BCN)",
      tooltip="BARCELONA (BCN)"
  ).add_to(m)

  # Toon de colormap als legenda op de kaart
  colormap.add_to(m)

  # Weergave van de kaart in Streamlit
  st_folium(m, width=700, height=600)

  

