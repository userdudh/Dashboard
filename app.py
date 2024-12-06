import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#------------------------------------------------------------------------------
# Inicializando app
app = Dash(__name__, external_stylesheets=['style.css'])

# Pré-processamento
#------------------------------------------------------------------------------
df = pd.read_csv("data/database.csv")

colunas = ['Date', 'Time', 'Latitude', 'Longitude', 'Type', 'Depth', 'Magnitude']
df = df[colunas]

df['Date'] = df['Date'].str.replace('-', '/', regex=False)
df = df[~df['Date'].str.contains(':', na=False)]
df = df[df['Type'] == 'Earthquake']

df = df[df['Type'] == 'Earthquake']

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
df['Hour'] = df['Time'].dt.hour

df['Hemisferio'] = df['Latitude'].apply(lambda x: 'Norte' if x > 0 else 'Sul')

# Layout
#------------------------------------------------------------------------------
app.layout = html.Div([
    html.H1("Cenário Sísmico Global: 1965-2016", className="title"),

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
            html.Img(src="assets/icon.png", id="logo"),
        ),

    html.Div(
        dcc.Graph(id='mapa', figure={}),
        className="map-container"
    ),

    html.Div(
        dcc.Graph(id='donut-graph', figure={}),
        className="donut-container"
    ),

    html.Div(
        dcc.Graph(id='frequencia-mes',figure={}),
        className="frequencia-container"
    ),

    html.Div(
        id="info_box",
        className="info-box",
        children=[
            html.P(id="text_info", className="text-info"),
            html.P(id="terremotos", className="terremotos"),
            html.P(id="text_info2", className="text-info"),
        ])
])

# Callback
#------------------------------------------------------------------------------
@app.callback(
    [Output('mapa', 'figure'),
     Output('text_info', 'children'),
     Output('terremotos', 'children'),
     Output('text_info2', 'children'),
     Output('donut-graph', 'figure'),
     Output('frequencia-mes', 'figure')],
    [Input('slct_year', 'value')]
)
# Filtra o DataFrame pelo ano selecionado
#------------------------------------------------------------------------------
def update_graph(option_slctd):
    dff = df[df["Year"] == option_slctd]
#-----------------------------------------------------------------------------
# Gráficos
#-----------------------------------------------------------------------------
    # Mapa
    fig = px.scatter_mapbox(
        dff,
        lat="Latitude",
        lon="Longitude",
        color="Magnitude",
        color_continuous_scale=[(0.00, "#C8FDFA"), (0.25, "#C8FDFA"),
                                (0.25, "#00E6B4"), (0.5, "#00E6B4"),
                                (0.5, "#004738"), (0.75, "#004738"),
                                (0.75, "#001A17"), (1.00, "#001A17")],
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
            center={"lat": 2.0931761494473418, "lon": -159.6797112855866},
            accesstoken="pk.eyJ1IjoibWR1YXJkYSIsImEiOiJjbTQ5cWV3MzkwNnJhMmtwdWpiN2Jpeng3In0.QS-vzhYh3pCS8CT6m9vc-g"
        )
    )

    fig.update_traces(marker=dict(size=20, opacity=0.7))
#-----------------------------------------------------------------------------
# Contagem de terremotos
    num_terremotos = len(dff)
    text_info = f"Em {option_slctd} ocorreram"
    terremotos_info = f"{num_terremotos}"
    text_info2 = "terremotos"
#-----------------------------------------------------------------------------
# Gráfico de donut
    hemisphere_counts = dff['Hemisferio'].value_counts().reset_index()
    hemisphere_counts.columns = ['Hemisferio', 'Casos']

    fig_donut = px.pie(
        hemisphere_counts,
        names='Hemisferio',
        values='Casos',
        hole=0.4,
        width=340,
        height=340,
        color_discrete_sequence=["#008266", "#001A17"]

    )
    fig_donut.update_traces(
        textfont=dict(color="white"),
        marker=dict(
            line=dict(color="white", width=1)
        )
    )
    fig_donut.update_layout(
            title=dict(
        text='Número de Terremotos por Hemisfério',
        font=dict(color='white'),
        x=0.5
    ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(color='white')
        )
    )
#-----------------------------------------------------------------------------
# Gráfico de donut
    df_ano_grouped = dff.groupby('Month').size().reset_index(name='Frequência')

    media_frequencia = df_ano_grouped['Frequência'].mean()

    fig_frequencia = px.line(
        df_ano_grouped,
        x='Month',
        y='Frequência',
        labels={"Month": "Mês", "Frequência": "Frequência"},
        title=f'Frequência de Terremotos por Mês em {option_slctd}',
        color_discrete_sequence=["#00ffc8"],
        width=1300,
        height=500
    )

    fig_frequencia.add_hline(
        y=media_frequencia,
        line=dict(color="white", dash="dash", width=2.5),
        annotation_text=f"Média: {media_frequencia:.2f}",
        annotation_position="top right",
        annotation=dict(
            font_size=16, 
            font_color="white", 
        ),
    )

    fig_frequencia.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
            tickfont=dict(color="white"),
            gridcolor="#2e2e2e"
        ),
        yaxis=dict(
            tickfont=dict(color="white"),
            gridcolor="#2e2e2e"
        ),
        plot_bgcolor="#191a1a",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title_font=dict(color="white"),
        yaxis_title_font=dict(color="white"),
    )

    fig_frequencia.update_layout(
        title=dict(
            text=f"Frequência de Terremotos por Mês em {option_slctd}",
            font=dict(size=22, color="white", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
        )
    )

#-----------------------------------------------------------------------------
    return fig, text_info, terremotos_info, text_info2, fig_donut,fig_frequencia

if __name__ == '__main__':
    app.run_server(debug=True)
