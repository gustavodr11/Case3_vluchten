import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# sidebar
with st.sidebar: 
  selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], icons=["play", "airplane", "bezier"], menu_icon="list")

# --------------------------------------------------------------------------

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

# --------------------------------------------------------------------------

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
                               index=[0, 10000, 20000, 30000, 40000],
                               vmin=df1['[3d Altitude Ft]'].min(), 
                               vmax=df1['[3d Altitude Ft]'].max(),
                               caption='Hoogte in ft.')

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

  # --------------------------------------

  # Voeg 'ALL' toe aan de opties voor het dropdownmenu
  selected_vlucht = st.selectbox("Selecteer een vlucht", options=['ALL'] + [f'vlucht {i}' for i in range(1, 8)])

  # Als 'ALL' is geselecteerd, combineer de data van alle vluchten en voeg een kolom toe om de vlucht te labelen
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

  # Maak de lijnplot met verschillende kleuren per vlucht
  fig = px.line(df1, x='Time (hours)', y='[3d Altitude Ft]', 
                title='Hoogte vs Tijd',  
                labels={"Time (hours)": "Tijd (uren)", "[3d Altitude Ft]": "Hoogte (ft)"},
                color='vlucht',  
                color_discrete_map=kleuren_map  
               )

  # Toon de grafiek in Streamlit
  st.plotly_chart(fig)

# --------------------------------------------------------------------------
# Vluchten pagina
if selected == 'Luchthavens':
  st.title("Luchthavens") 
  st.subheader("Top 20 luchthavens") 
  df = (DatasetLuchthaven_murged2.csv)
  # Tellen van de meest voorkomende luchthavens
  luchthaven_frequentie = df['luchthaven'].value_counts().nlargest(20).reset_index()

# Hernoem de kolommen voor duidelijkheid
  luchthaven_frequentie.columns = ['Luchthaven', 'Aantal_vluchten']

# Maak een interactieve bar plot met plotly express
  fig = px.bar(luchthaven_frequentie, x='Luchthaven', y='Aantal_vluchten', 
             title='Top 20 Meest Voorkomende Luchthavens',
             labels={'Aantal_vluchten': 'Aantal vluchten'},
             color='Aantal_vluchten', color_continuous_scale='Blues')

# Toon de plot in Streamlit
  st.plotly_chart(fig)
  st.supheader(Luchthavens zijn optijd?)
  
# Groeperen per luchthaven en status
  grouped = df.groupby(['City', 'status'])['vluchten'].sum().unstack(fill_value=0)

# Berekenen van het percentage per luchthaven
  grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

# Voor plotly moeten we het DataFrame omzetten naar een lang formaat
  grouped_percentage_reset = grouped_percentage.reset_index().melt(id_vars='City', value_vars=['Te laat', 'Op tijd', 'Te vroeg'],
                                                                 var_name='status', value_name='percentage')

# Maak een gestapelde bar plot met plotly express
  fig = px.bar(grouped_percentage_reset, x='City', y='percentage', color='status',
             title='Percentage vluchten die te laat, op tijd of te vroeg zijn per luchthaven',
             labels={'percentage': 'Percentage (%)', 'City': 'Luchthaven'},
             color_discrete_map={'Te laat': 'red', 'Op tijd': 'green', 'Te vroeg': 'blue'})

# Pas de lay-out van de grafiek aan
  fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})

# Toon de plot in Streamlit
  st.plotly_chart(fig)
  
  # Gemiddelde vertraging per luchthaven en jaar berekenen
  gemiddelde_vertraging = merged_df.groupby(['City', 'Jaartal'])['verschil_minuten'].mean().reset_index()

# Aantal vluchten per luchthaven en jaar tellen
  aantal_vluchten = df.groupby(['City', 'Jaartal']).size().reset_index(name='aantal_vluchten')

# De resultaten samenvoegen
  gemiddelde_vertraging = gemiddelde_vertraging.merge(aantal_vluchten, on=['City', 'Jaartal'])

# Split de data op basis van jaartal
  df_2019 = gemiddelde_vertraging[gemiddelde_vertraging['Jaartal'] == 2019]
  df_2020 = gemiddelde_vertraging[gemiddelde_vertraging['Jaartal'] == 2020]

# Bepaal de maximale waarde voor de y-as
  max_vertraging = max(gemiddelde_vertraging['verschil_minuten'].max(), 0)
  min_vertraging = min(gemiddelde_vertraging['verschil_minuten'].min(), 0)

# Bar plot voor 2019
  fig_2019 = px.bar(
      df_2019, 
      x='City', 
      y='verschil_minuten', 
      title='Gemiddelde vertraging van vluchten per luchthaven in 2019 (in minuten)', 
      labels={'City': 'Luchthaven', 'verschil_minuten': 'Gemiddelde vertraging (minuten)'},
      color='verschil_minuten',
      text='aantal_vluchten',  # Aantal vluchten als tekstlabel
      color_continuous_scale=px.colors.sequential.Viridis
  )

# Y-as instellen voor 2019
  fig_2019.update_yaxes(range=[min_vertraging, max_vertraging])

# Bar plot voor 2020
  fig_2020 = px.bar(
      df_2020, 
      x='City', 
      y='verschil_minuten', 
      title='Gemiddelde vertraging van vluchten per luchthaven in 2020 (in minuten)', 
      labels={'City': 'Luchthaven', 'verschil_minuten': 'Gemiddelde vertraging (minuten)'},
      color='verschil_minuten',
      text='aantal_vluchten',  # Aantal vluchten als tekstlabel
      color_continuous_scale=px.colors.sequential.Viridis
  )

# Y-as instellen voor 2020
  fig_2020.update_yaxes(range=[min_vertraging, max_vertraging])

# Plotten van beide figuren in Streamlit
  st.plotly_chart(fig_2019)
  st.plotly_chart(fig_2020)
  st.subheader("Drukte op luchthavens in de tijd")


# Bereken het aantal vliegtuigen op elke luchthaven op een bepaald moment
  def calculate_aircraft_on_airport(selected_time):
      landed = df[(merged_df['LSV'] == 'L') & (merged_df['STD'] <= selected_time)]
      departed = df[(merged_df['LSV'] == 'S') & (merged_df['STD'] <= selected_time)]
    
      landed_count = landed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vliegtuigen')
      departed_count = departed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vertrokken')

      airport_traffic = pd.merge(landed_count, departed_count, on='luchthaven', how='left').fillna(0)
      airport_traffic['Aantal_vliegtuigen'] = airport_traffic['Aantal_vliegtuigen'] - airport_traffic['Aantal_vertrokken']

      return airport_traffic

# Streamlit interface
  st.title("Vliegtuigen op luchthavens")
  st.write("Selecteer een datum om het aantal vliegtuigen per luchthaven te zien.")

# Datumkeuze
  selected_date = st.date_input("Kies een datum:", value=pd.to_datetime('2019-07-15'))

# Bereken het aantal vliegtuigen voor de geselecteerde datum
  airport_traffic = calculate_aircraft_on_airport(selected_date)

# Bar plot weergeven
  fig = px.bar(
      airport_traffic, 
      x='luchthaven', 
      y='Aantal_vliegtuigen', 
      title=f"Aantal vliegtuigen per luchthaven op {selected_date}",
      labels={'luchthaven': 'Luchthaven', 'Aantal_vliegtuigen': 'Aantal Vliegtuigen'},
      color='Aantal_vliegtuigen',
      color_continuous_scale=px.colors.sequential.Viridis
  )

  st.plotly_chart(fig)

# Interactieve grafiek met een slider
  def create_aircraft_slider_plot():
      start_date = pd.to_datetime('2019-01-01')
      end_date = pd.to_datetime('2020-12-31')
      days = pd.date_range(start=start_date, end=end_date, freq='D')

      frames = []

      for day in days:
          filtered_data = calculate_aircraft_on_airport(day)
          fig = px.bar(filtered_data, x='luchthaven', y='Aantal_vliegtuigen', title=f"Aantal vliegtuigen per luchthaven op {day.date()}")
          frames.append(go.Frame(data=fig.data, name=str(day.date())))

    # Initiële figuur
      initial_fig = calculate_aircraft_on_airport(days[0])
      fig = px.bar(initial_fig, x='luchthaven', y='Aantal_vliegtuigen', title=f"Aantal vliegtuigen per luchthaven op {days[0].date()}")

      fig = go.Figure(
          data=fig.data,
          layout=go.Layout(
              sliders=[{
                  'steps': [{
                      'args': [[str(day.date())], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                      'label': str(day.date()),
                      'method': 'animate'
                  } for day in days],
                  'currentvalue': {'prefix': 'Datum: '},
                  'pad': {'b': 10},
              }]
          ),
          frames=frames
      )

      st.plotly_chart(fig)

# Aanroepen van de slider grafiek
  if st.checkbox("Toon interactieve grafiek met slider"):
      create_aircraft_slider_plot()

  st.subheader("Hitte kaart europa")
  df['Latitude'] = merged_df['Latitude'].astype(str).str.replace(',', '.').astype(float)
  df['Longitude'] = merged_df['Longitude'].astype(str).str.replace(',', '.').astype(float)

# Voeg een nieuwe kolom toe voor de tijdstippen van de gebeurtenissen
  df['STD'] = pd.to_datetime(merged_df['STD'])  # Zorg dat STD als datetime is

# Bereken het aantal vliegtuigen op elke luchthaven op een bepaald moment
  def calculate_aircraft_on_airport(selected_time):
    # Filter de data voor alle vluchten die al geland zijn, maar nog niet vertrokken op het gekozen tijdstip
      landed = merged_df[(merged_df['LSV'] == 'L') & (merged_df['STD'] <= selected_time)]
      departed = merged_df[(merged_df['LSV'] == 'S') & (merged_df['STD'] <= selected_time)]
    
    # Groepeer de vluchten per luchthaven en tel het aantal vliegtuigen dat er nog is
      landed_count = landed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vliegtuigen')
      departed_count = departed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vertrokken')

    # Voeg de twee datasets samen en bereken het aantal vliegtuigen dat nog aanwezig is
      airport_traffic = pd.merge(landed_count, departed_count, on='luchthaven', how='left').fillna(0)
      airport_traffic['Aantal_vliegtuigen'] = airport_traffic['Aantal_vliegtuigen'] - airport_traffic['Aantal_vertrokken']

    # Voeg de coördinaten van de luchthavens toe
      airports = merged_df[['luchthaven', 'Latitude', 'Longitude']].drop_duplicates()
      airport_traffic = airport_traffic.merge(airports, on='luchthaven')

      return airport_traffic

# Maak een functie om de kaart te genereren, inclusief een heatmap
  def create_aircraft_traffic_map(selected_time):
    # Bereken het aantal vliegtuigen op de luchthavens op de geselecteerde tijd
      airport_traffic = calculate_aircraft_on_airport(selected_time)

    # Maak de kaart met een centraal punt in Europa
      traffic_map = folium.Map(location=[50, 10], zoom_start=4)

    # Voeg markers toe aan de kaart voor elke luchthaven
      for idx, row in airport_traffic.iterrows():
        # Bepaal de grootte van de marker op basis van het aantal vliegtuigen
          folium.CircleMarker(
              location=[row['Latitude'], row['Longitude']],
              radius=row['Aantal_vliegtuigen'] / 10,  # Maak de marker afhankelijk van het aantal vliegtuigen
              color='red',  # Rode markers voor het aantal vliegtuigen op de luchthaven
              fill=True,
              fill_opacity=0.6,
              tooltip=f"Luchthaven: {row['luchthaven']}, Aantal vliegtuigen: {row['Aantal_vliegtuigen']}"
          ).add_to(traffic_map)

    # Voeg heatmap toe gebaseerd op het aantal vliegtuigen op elke luchthaven
      heat_data = [[row['Latitude'], row['Longitude'], row['Aantal_vliegtuigen']] for idx, row in airport_traffic.iterrows()]
      HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(traffic_map)

      return traffic_map

# Streamlit-app
  def main():
      st.title("Interactieve Luchtvaartkaart")

    # Datumselector
      start_date = pd.to_datetime('2019-01-01')
      end_date = pd.to_datetime('2020-12-31')
      selected_day = st.date_input("Selecteer een datum", value=start_date)

    # Controleer of de geselecteerde datum binnen het bereik ligt
      if start_date <= pd.Timestamp(selected_day) <= end_date:
        # Genereer de kaart voor de geselecteerde datum en tijd
          selected_date_time = pd.Timestamp(selected_day)
          traffic_map = create_aircraft_traffic_map(selected_date_time)
        
        # Toon de kaart met st_folium
          st.subheader(f"Luchtvaartverkeer op {selected_day}")
          st_folium(traffic_map)  # Gebruik st_folium in plaats van folium_static
      else:
          st.warning("Selecteer een datum tussen 2019-01-01 en 2020-12-31.")
    
  

