import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

df = pd.read_csv("DatasetLuchthaven_murged2.csv")
luchthaven_frequentie = pd.read_csv("luchthaven_frequentie.csv")

# Bereken het totale aantal vluchten per luchthaven per maand
def calculate_flights_per_month(selected_month):
    # Zorg ervoor dat de STD-kolom correct is geformatteerd als datetime
    df['STD'] = pd.to_datetime(df['STD'], errors='coerce')
    
    # Filter de dataframe om alle vluchten binnen de geselecteerde maand op te nemen
    month_data = df[(df['STD'].dt.month == selected_month.month) & (df['STD'].dt.year == selected_month.year)]
    
    # Bereken het aantal inkomende en vertrekkende vluchten per luchthaven
    inbound_flights = month_data[month_data['LSV'] == 'L'].groupby('City').size().reset_index(name='Aantal_inbound')
    outbound_flights = month_data[month_data['LSV'] == 'S'].groupby('City').size().reset_index(name='Aantal_outbound')
    
    # Voeg de inkomende en vertrekkende vluchten samen per luchthaven
    airport_flights = pd.merge(inbound_flights, outbound_flights, on='City', how='outer').fillna(0)
    airport_flights['Totaal_aantal_vluchten'] = airport_flights['Aantal_inbound'] + airport_flights['Aantal_outbound']

    return airport_flights

# Streamlit interface
st.subheader("Aantal vluchten per luchthaven per maand")

# Slider voor maandselectie
selected_month = st.slider("Selecteer een maand:", 
                           min_value=datetime(2019, 1, 1), 
                           max_value=datetime(2020, 12, 31), 
                           value=datetime(2019, 7, 1), 
                           format="YYYY-MM")

# Bereken het aantal vluchten voor de geselecteerde maand
airport_flights = calculate_flights_per_month(selected_month)

# Bar plot weergeven
fig = px.bar(
    airport_flights,
    x='City',
    y='Totaal_aantal_vluchten',
    labels={'City': 'Luchthaven', 'Totaal_aantal_vluchten': 'Aantal Vluchten'},
    color='Totaal_aantal_vluchten',
    color_continuous_scale=px.colors.sequential.Viridis
)

st.plotly_chart(fig)
