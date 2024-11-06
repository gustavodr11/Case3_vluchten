import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

# Laad de dataset
df = pd.read_csv("DatasetLuchthaven_murged2.csv")
df.drop(['Unnamed: 0'], axis=1, inplace=True)

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
mae = mean_absolute_error(y, data_per_luchthaven['voorspeld_aantal_vluchten'])
rmse = np.sqrt(mean_squared_error(y, data_per_luchthaven['voorspeld_aantal_vluchten']))

# Print modelresultaten in Streamlit
st.write("##### Resultaten van Random Forest Regressie")
st.write(f"R²-score: {r2:.2f}")
st.write(f"Mean Absolute Error (MAE): {mae:.2f}")
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
