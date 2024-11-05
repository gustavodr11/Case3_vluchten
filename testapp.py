import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
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

# Maak een dropdown menu in Streamlit voor de luchthaven selectie
selected_luchthaven = st.selectbox("Selecteer een luchthaven", luchthavens)

# Filter de data per geselecteerde luchthaven
data_per_luchthaven = df_grouped[df_grouped['luchthaven'] == selected_luchthaven].set_index('Maand')
X = data_per_luchthaven.index.values.reshape(-1, 1)
y = data_per_luchthaven['aantal_vluchten']

# Model selectie
model_type = st.selectbox("Selecteer een model", ["SARIMA", "Lineaire Regressie", "Random Forest"])

# SARIMA Model
if model_type == "SARIMA":
    model = SARIMAX(data_per_luchthaven['aantal_vluchten'], 
                    order=(1, 1, 1),  # ARIMA parameters (p, d, q)
                    seasonal_order=(1, 1, 1, 12),  # SARIMA parameters (P, D, Q, s)
                    enforce_stationarity=False, 
                    enforce_invertibility=False)
    results = model.fit(disp=False)
    data_per_luchthaven['voorspeld_aantal_vluchten'] = results.predict(start=1, end=len(data_per_luchthaven))
    
    # Evaluatiemaatstaven
    r2 = r2_score(y, data_per_luchthaven['voorspeld_aantal_vluchten'][1:])
    mae = mean_absolute_error(y, data_per_luchthaven['voorspeld_aantal_vluchten'][1:])

    st.write("### SARIMA Model Resultaten")
    st.write(f"R²-score: {r2:.2f}")
    st.write(f"Mean Absolute Error (MAE): {mae:.2f}")

# Lineaire Regressie Model
elif model_type == "Lineaire Regressie":
    model = LinearRegression()
    model.fit(X, y)
    data_per_luchthaven['voorspeld_aantal_vluchten'] = model.predict(X)

    # Evaluatiemaatstaven
    r2 = r2_score(y, data_per_luchthaven['voorspeld_aantal_vluchten'])
    mae = mean_absolute_error(y, data_per_luchthaven['voorspeld_aantal_vluchten'])

    st.write("### Lineaire Regressie Model Resultaten")
    st.write(f"Intercept (snijpunt met de y-as): {model.intercept_:.2f}")
    st.write(f"Maandcoëfficiënt: {model.coef_[0]:.2f}")
    st.write(f"R²-score: {r2:.2f}")
    st.write(f"Mean Absolute Error (MAE): {mae:.2f}")

# Random Forest Model
elif model_type == "Random Forest":
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    data_per_luchthaven['voorspeld_aantal_vluchten'] = model.predict(X)

    # Evaluatiemaatstaven
    r2 = r2_score(y, data_per_luchthaven['voorspeld_aantal_vluchten'])
    mae = mean_absolute_error(y, data_per_luchthaven['voorspeld_aantal_vluchten'])

    st.write("### Random Forest Model Resultaten")
    st.write(f"R²-score: {r2:.2f}")
    st.write(f"Mean Absolute Error (MAE): {mae:.2f}")

# Plot de resultaten
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
    name=f'Voorspeld aantal vluchten ({model_type})',
    line=dict(color='red'),
))

# Update layout van de figuur
fig.update_layout(
    title=f"Voorspelling en werkelijke gegevens voor {selected_luchthaven} met {model_type}",
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

