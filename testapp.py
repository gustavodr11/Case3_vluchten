import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
import streamlit as st
import numpy as np


# Laad de dataset
df = pd.read_csv("DatasetLuchthaven_murged2.csv")
df.drop(['Unnamed: 0'], axis=1, inplace=True)

# Zorg ervoor dat de kolom 'STD' datetime objecten zijn en groepeer de data per maand en luchthaven
df['STD'] = pd.to_datetime(df['STD'])
df['Maand'] = df['STD'].dt.month

# Groepeer per maand en luchthaven om de werkelijke data te verkrijgen
df_grouped = df.groupby(['Maand', 'luchthaven']).agg(
    aantal_vluchten=('FLT', 'count')
).reset_index()

# Unieke luchthavens ophalen
luchthavens = df_grouped['luchthaven'].unique()

# Maak een dropdown menu in Streamlit voor de luchthaven selectie
selected_luchthaven = st.selectbox("Selecteer een luchthaven", luchthavens)

# Filter de data per geselecteerde luchthaven
data_per_luchthaven = df_grouped[df_grouped['luchthaven'] == selected_luchthaven].set_index('Maand')

# Pas een SARIMA-model toe om het aantal vluchten te voorspellen
model = sm.tsa.statespace.SARIMAX(data_per_luchthaven['aantal_vluchten'], 
                                  order=(1, 1, 1),  # ARIMA parameters (p, d, q)
                                  seasonal_order=(1, 1, 1, 12),  # SARIMA parameters (P, D, Q, s)
                                  enforce_stationarity=False, 
                                  enforce_invertibility=False)
results = model.fit(disp=False)

# Voorspellingen genereren voor het aantal maanden in de dataset
voorspellingen = results.predict(start=1, end=len(data_per_luchthaven) - 1)
predicted_mean = np.insert(voorspellingen.values, 0, None)
data_per_luchthaven['voorspeld_aantal_vluchten'] = predicted_mean

# Maak de plot voor werkelijke en voorspelde gegevens
fig = go.Figure()

# Werkelijke gegevens (blauwe lijnen)
fig.add_trace(go.Scatter(
    x=data_per_luchthaven.index, 
    y=data_per_luchthaven['aantal_vluchten'], 
    mode='lines+markers', 
    name=f'Werkelijk aantal vluchten ({selected_luchthaven})',
    line=dict(color='blue'),
))

# Voorspelde gegevens (rode lijnen)
fig.add_trace(go.Scatter(
    x=data_per_luchthaven.index, 
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

model_summary = results.summary().as_text()  # Zet de samenvatting om naar tekst
st.text(model_summary)
