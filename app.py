import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Inicialização do app
app = Dash(__name__, external_stylesheets=['style.css'])

# Leitura e processamento dos dados
df = pd.read_csv("data/database.csv")

colunas = ['Date', 'Time', 'Latitude', 'Longitude', 'Type', 'Depth', 'Magnitude']
df = df[colunas]

df['Date'] = df['Date'].str.replace('-', '/', regex=False)
df = df[~df['Date'].str.contains(':', na=False)]
df = df[df['Type'] == 'Earthquake']

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Date'] = df['Date'].dt.year
df = df.rename(columns={'Date': 'Year'})

df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
df['Time'] = df['Time'].dt.hour
df = df.rename(columns={'Time': 'Hour'})

# Adiciona a coluna do hemisfério
df['Hemisferio'] = df['Latitude'].apply(lambda x: 'Norte' if x > 0 else 'Sul')

# Contagem dos terremotos por hemisfério
hemisphere_counts = df['Hemisferio'].value_counts().reset_index()
hemisphere_counts.columns = ['Hemisferio', 'Count']

# Gráfico de donuts
fig_donut = px.pie(
    hemisphere_counts,
    names='Hemisferio',
    values='Count',
    hole=0.4,
    width=400,
    height=400
)

fig_donut.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        font=dict(color='white')
    )
)

# Layout do aplicativo
app.layout = html.Div([

    html.H1("Análise Visual dos Terremotos Globais (1965-2016)", className="title"),

    html.Div([
        html.Span("Ano Selecionado: ", className="year-label"),
        dcc.Dropdown(
            id="slct_year",
            options=[{"label": str(year), "value": year} for year in range(1965, 2017)],
            multi=False,
            value=1965,
            className="dropdown"
        ),
    ], className="dropdown-container"),

    html.Div(
        dcc.Graph(id='mapa', figure={}),
        className="map-container"
    ),

    html.Div(
        id="info_box",
        className="info-box",
        children=[
            html.P(id="text_info", children="Em {ano escolhido} ocorreram X terremotos", className="text-info"),
            html.P(id="terremotos", children="terremotos", className="terremotos"),
            html.P(id="text_info2", children="terremotos", className="text-info"),
        ]
    ),

    # Novo gráfico dentro de um retângulo
    html.Div(
        dcc.Graph(id='donut_chart', figure=fig_donut),
        className="info-box donut-box"
    )
])

# Callback para atualizar o gráfico principal e textos
@app.callback(
    [Output(component_id='mapa', component_property='figure'),
     Output(component_id='text_info', component_property='children'),
     Output(component_id='terremotos', component_property='children'),
     Output(component_id='text_info2', component_property='children')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    dff = df.copy()
    dff = dff[dff["Year"] == option_slctd]

    num_terremotos = len(dff)

    fig = px.scatter_mapbox(
        dff,
        lat="Latitude",
        lon="Longitude",
        color="Magnitude",
        color_continuous_scale=[(0.00, "#ffcc00"), (0.25, "#ffcc00"),
                                (0.25, "#fc9e0f"), (0.5, "#fc9e0f"),
                                (0.5, "#ff2a00"), (0.75, "#ff2a00"),
                                (0.75, "#4d0202"), (1.00, "#4d0202")],
        color_continuous_midpoint=6.5,
        width=915,
        height=580,
        zoom=1.5
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(
            title="Magnitude",
            titlefont=dict(color="white"),
            tickfont=dict(color="white"),
            orientation="h",
            x=0.5,
            y=0.05,
            xanchor="center",
            yanchor="bottom",
            thickness=15,
            len=0.5,
            bgcolor="rgba(0,0,0,0.5)"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            style="dark",
            accesstoken="pk.eyJ1IjoibWR1YXJkYSIsImEiOiJjbTQ5cWV3MzkwNnJhMmtwdWpiN2Jpeng3In0.QS-vzhYh3pCS8CT6m9vc-g"
        )
    )

    fig.update_traces(marker=dict(size=20, opacity=0.5))

    text_info = f"Em {option_slctd} ocorreram"
    terremotos_info = f"{num_terremotos}"
    text_info2 = "terremotos"

    return fig, text_info, terremotos_info, text_info2

if __name__ == '__main__':
    app.run_server(debug=True)
