import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
# Zorg ervoor dat de kolom 'STD' datetime objecten zijn en groepeer de data per maand en luchthaven
df['STD'] = pd.to_datetime(df['STD'])
df['Maand'] = df['STD'].dt.month
# Groepeer per maand en luchthaven om de werkelijke data te verkrijgen
df_grouped = df.groupby(['Maand', 'luchthaven']).agg(
    aantal_vluchten=('FLT', 'count')
).reset_index()
# Unieke luchthavens ophalen
luchthavens = df_grouped['luchthaven'].unique()
# Maak de figuur aan met dropdown-opties
fig = go.Figure()
# Loop door elke luchthaven en train een SARIMA-model
for luchthaven in luchthavens:
    # Filter data per luchthaven
    data_per_luchthaven = df_grouped[df_grouped['luchthaven'] == luchthaven].set_index('Maand')
    # Pas een SARIMA-model toe om het aantal vluchten te voorspellen
    model = sm.tsa.statespace.SARIMAX(data_per_luchthaven['aantal_vluchten'], 
                                      order=(1, 1, 1),  # ARIMA parameters (p, d, q)
                                      seasonal_order=(1, 1, 1, 12),  # SARIMA parameters (P, D, Q, s)
                                      enforce_stationarity=False, 
                                      enforce_invertibility=False)
    results = model.fit(disp=False)
    # Voorspellingen genereren voor het aantal maanden in de dataset
    voorspellingen = results.predict(start=0, end=len(data_per_luchthaven) - 1)
    data_per_luchthaven['voorspeld_aantal_vluchten'] = voorspellingen.values
    # Werkelijke gegevens (blauwe lijnen)
    fig.add_trace(go.Scatter(
        x=data_per_luchthaven.index, 
        y=data_per_luchthaven['aantal_vluchten'], 
        mode='lines+markers', 
        name=f'Werkelijk aantal vluchten ({luchthaven})',
        line=dict(color='blue'),
        visible=False,
    ))
    # Voorspelde gegevens (rode lijnen)
    fig.add_trace(go.Scatter(
        x=data_per_luchthaven.index, 
        y=data_per_luchthaven['voorspeld_aantal_vluchten'], 
        mode='lines+markers', 
        name=f'Voorspeld aantal vluchten ({luchthaven})',
        line=dict(color='red'),
        visible=False,
    ))
# Dropdown menu-opties configureren
dropdown_buttons = []
for i, luchthaven in enumerate(luchthavens):
    # Elke luchthaven wordt slechts één keer weergegeven als actief in de dropdown
    visible_trace_indices = [False] * len(fig.data)
    visible_trace_indices[i * 2: i * 2 + 2] = [True] * 2  # Toon alleen de twee sporen voor de geselecteerde luchthaven
    dropdown_buttons.append(
        dict(
            label=str(luchthaven),  # Zorg ervoor dat label een string is
            method="update",
            args=[{"visible": visible_trace_indices},
                  {"title": f"Voorspelling en werkelijke data voor {luchthaven}"}],
        )
    )
# Voeg dropdown toe aan layout
fig.update_layout(
    updatemenus=[dict(
        active=0,
        buttons=dropdown_buttons,
        x=1,
        y=1.15,
    )],
    title="Maandelijkse voorspelling en werkelijke gegevens per luchthaven",
    xaxis_title="Maand",
    yaxis_title="Aantal vluchten",
    height=600,
)
# Begin met de eerste luchthaven zichtbaar
fig.data[0].visible = True
fig.data[1].visible = True
fig.show()
