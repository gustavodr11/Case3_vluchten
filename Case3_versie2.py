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
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
  
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
    st.title("Case 3 Vluchten `versie 2` - Gustavo & Stievy")
    st.write("""
        Voor deze VA-opdracht hebben we het dashboard van Casus 3 Vluchten verbeterd. 
        We hebben verschillende elementen aangepast om er meer een dashboard van te maken en het geheel compacter te maken dan de vorige versie.
    """)
    st.write("#### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
        - [Uitstoot data](https://ecotree.green/nl/calculate-flight-co2#result)
        - [Max. aantal passagiers (KLM - Boeing 737)](https://www.klm.nl/information/travel-class-extra-options/aircraft-types/boeing-737-800)
        - [Random Forest Regression Explained](https://medium.com/@theclickreader/random-forest-regression-explained-with-implementation-in-python-3dad88caf165)
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
    st.write("#### Zijn luchthavens op tijd?")

    # Maak drie kolommen voor de metrics
    col1, col2, col3 = st.columns(3)
    
    # Toon de metrics
    with col1:
        st.metric(label="Rome", value=f"38%", delta="Te vroeg")
    with col2:
        st.metric(label="Stockholm", value=f"11%", delta="Op Tijd")
    with col3:
        st.metric(label="Stockholm", value=f"69%", delta="Te laat", delta_color="inverse")

    st.write("##### ")
# --------------------------------------------------
    
    df = pd.read_csv("DatasetLuchthaven_murged2.csv")
    luchthaven_frequentie = pd.read_csv("luchthaven_frequentie.csv")
    
    # Groeperen per luchthaven en status
    grouped = df.groupby(['City', 'status']).size().unstack(fill_value=0)

    # Berekenen van het percentage per luchthaven
    grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # DataFrame omzetten naar lang formaat voor Plotly
    grouped_percentage_reset = grouped_percentage.reset_index().melt(id_vars='City', value_vars=['Te laat', 'Op tijd', 'Te vroeg'],
                                                                 var_name='status', value_name='percentage')

    # Maak een gestapelde bar plot met Plotly Express
    fig = px.bar(
        grouped_percentage_reset,
        x='City',
        y='percentage',
        color='status',
        title='Percentage Vluchten Te Laat, Op Tijd, en Te Vroeg per Luchthaven',
        labels={'percentage': 'Percentage (%)', 'City': 'Luchthaven'},
        color_discrete_map={'Te laat': '#FF4B4B', 'Op tijd': '#4CAF50', 'Te vroeg': '#4B7BFF'}
    )

    # Pas de layout van de grafiek aan
    fig.update_layout(
        barmode='stack',
        xaxis={'categoryorder': 'total descending'},
        yaxis=dict(tickformat=".0f"),  # Geen decimalen in y-as
    )

    # Voeg percentages toe boven de bars
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='inside', insidetextanchor='middle')

    # Pas de lettergrootte aan voor betere leesbaarheid
    fig.update_layout(
        font=dict(size=12),
        xaxis_title="Luchthavens",
        yaxis_title="Percentage (%)"
    )

    # Toon de plot in Streamlit
    st.plotly_chart(fig)


# -------------------------------------------------------------------

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
    st.write("#### Aantal vluchten per luchthaven per maand")

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
 
    # --------------------------------------------------------------
  
    # Zorg ervoor dat de kolom 'STD' datetime objecten zijn en voeg de maand toe
    df['STD'] = pd.to_datetime(df['STD'])
    df['Maand'] = df['STD'].dt.month

    # Groepeer per maand en luchthaven om de werkelijke data te verkrijgen
    df_grouped = df.groupby(['Maand', 'luchthaven']).agg(
        aantal_vluchten=('FLT', 'count')
    ).reset_index()

    # Unieke luchthavens ophalen
    luchthavens = df_grouped['luchthaven'].unique()

    st.write("#### Model")

    # Maak een dropdown menu in Streamlit voor de luchthaven selectie
    selected_luchthaven = st.selectbox("Selecteer een luchthaven", luchthavens)

    # Filter de data per geselecteerde luchthaven
    data_per_luchthaven = df_grouped[df_grouped['luchthaven'] == selected_luchthaven]

    # Voorbereiding voor Random Forest: de maand als input en aantal vluchten als output
    X = data_per_luchthaven['Maand'].values.reshape(-1, 1)
    y = data_per_luchthaven['aantal_vluchten']

    # Pas Random Forest toe
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Voorspellingen genereren
    data_per_luchthaven['voorspeld_aantal_vluchten'] = model.predict(X)

    # Bereken evaluatiemaatstaven
    r2 = r2_score(y, data_per_luchthaven['voorspeld_aantal_vluchten'])
    rmse = np.sqrt(mean_squared_error(y, data_per_luchthaven['voorspeld_aantal_vluchten']))

    # Print modelresultaten in Streamlit
    st.write("##### Resultaten van Random Forest Regressie")
    st.write(f"R²-score: {r2:.2f}")
    st.write(f"Root Mean Squared Error (RMSE): {rmse:.2f}")

    # Maak de plot voor werkelijke en voorspelde gegevens
    fig = go.Figure()

    # Werkelijke gegevens (blauwe lijnen)
    fig.add_trace(go.Scatter(
        x=data_per_luchthaven['Maand'], 
        y=data_per_luchthaven['aantal_vluchten'], 
        mode='lines+markers', 
        name=f'Werkelijk aantal vluchten ({selected_luchthaven})',
        line=dict(color='blue'),
    ))

    # Voorspelde gegevens (rode lijnen)
    fig.add_trace(go.Scatter(
        x=data_per_luchthaven['Maand'], 
        y=data_per_luchthaven['voorspeld_aantal_vluchten'], 
        mode='lines+markers', 
        name=f'Voorspeld aantal vluchten ({selected_luchthaven})',
        line=dict(color='red'),
    ))

    # Update layout van de figuur
    fig.update_layout(
        title=f"Voorspelling en werkelijke gegevens voor {selected_luchthaven}",
        xaxis_title="Maand",
        yaxis_title="Aantal vluchten",
        height=600,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),  # Maandnummers van 1 tot 12
            ticktext=[str(i) for i in range(1, 13)],  # Weergeven als 1, 2, ..., 12
        )
    )

    # Toon de plot in Streamlit
    st.plotly_chart(fig)






