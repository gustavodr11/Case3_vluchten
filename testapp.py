import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error, mean_squared_error

df = pd.read_csv("DatasetLuchthaven_murged2.csv")
df.drop(['Unnamed: 0'], axis = 1)

# Zorg ervoor dat de kolom 'STD' datetime objecten zijn en groepeer de data per maand en luchthaven
df['STD'] = pd.to_datetime(df['STD'])
df['Maand'] = df['STD'].dt.to_period('M')  # Gebruik 'M' voor maand als periode

# Groepeer per maand en luchthaven om de werkelijke data te verkrijgen
df_grouped = df.groupby(['Maand', 'luchthaven']).agg(
    aantal_vluchten=('FLT', 'count')
).reset_index()

# Maak een datetime-index aan voor de toekomstige voorspellingen
df_grouped['Maand'] = df_grouped['Maand'].dt.to_timestamp()  # Zet de periode terug naar timestamp
df_grouped.set_index('Maand', inplace=True)

# Unieke luchthavens ophalen
luchthavens = df_grouped['luchthaven'].unique()

# Maak de figuur aan met dropdown-opties
fig = go.Figure()

# Loop door elke luchthaven en train een SARIMA-model
for luchthaven in luchthavens:
    # Filter data per luchthaven
    data_per_luchthaven = df_grouped[df_grouped['luchthaven'] == luchthaven]

    # Splits de gegevens in training en test (80% training, 20% test)
    train_size = int(len(data_per_luchthaven) * 0.8)
    train, test = data_per_luchthaven.iloc[:train_size], data_per_luchthaven.iloc[train_size:]

    # Pas een SARIMA-model toe op de trainingsdata
    model = sm.tsa.statespace.SARIMAX(train['aantal_vluchten'], 
                                       order=(1, 1, 1),  # ARIMA parameters (p, d, q)
                                       seasonal_order=(1, 1, 1, 12),  # SARIMA parameters (P, D, Q, s)
                                       enforce_stationarity=False, 
                                       enforce_invertibility=False)
    results = model.fit(disp=False)

    # Voorspel op de testset
    voorspellingen = results.get_forecast(steps=len(test))
    predicted_mean = voorspellingen.predicted_mean

    # Evaluatiemetrieken
    mae = mean_absolute_error(test['aantal_vluchten'], predicted_mean)
    mse = mean_squared_error(test['aantal_vluchten'], predicted_mean)
    rmse = mean_squared_error(test['aantal_vluchten'], predicted_mean, squared=False)

    print(f'{luchthaven} - MAE: {mae}, MSE: {mse}, RMSE: {rmse}')

    # Voeg de voorspellingen toe aan de oorspronkelijke dataframe voor visualisatie
    data_per_luchthaven['voorspeld_aantal_vluchten'] = None
    data_per_luchthaven.iloc[train_size:, data_per_luchthaven.columns.get_loc('voorspeld_aantal_vluchten')] = predicted_mean.values

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
