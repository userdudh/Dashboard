import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np

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
        dcc.Graph(id='box-graph',figure={}),
        className="box-container"
    ),

    html.Div(
        dcc.Graph(id='profundidade-mes',figure={}),
        className="profundidade-container"
    ),

    html.Div(
        id="info_box",
        className="info-box",
        children=[
            html.P(id="text_info", className="text-info"),
            html.P(id="terremotos", className="terremotos"),
            html.P(id="text_info2", className="text-info"),
        ]),
        
    html.Div(
        html.Img(src="assets/box.png", id="box"),
    ), 

    html.Div(
        dcc.Graph(id='bar-graph',figure={}),
        className="bar-container"
    ),


])

# Callback
#-----------------------------------------------------------------------------
@app.callback(
    [Output('mapa', 'figure'),
     Output('text_info', 'children'),
     Output('terremotos', 'children'),
     Output('text_info2', 'children'),
     Output('donut-graph', 'figure'),
     Output('box-graph', 'figure'),
     Output('profundidade-mes', 'figure'),
     Output('bar-graph', 'figure')],
    [Input('slct_year', 'value')]
)

# Filtra o DataFrame pelo ano selecionado
#-----------------------------------------------------------------------------
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
#caixa   
    fig_box = px.box(
        dff,
        x="Month",
        y="Magnitude",
        labels={"Month": "Mês", "Magnitude": "Magnitude"},
        title=f"Distribuição de Magnitudes por Mês em {dff['Year'].iloc[0]}",
        color_discrete_sequence=["#00ffc8"],  
        width=915,
        height=450
    )

    fig_box.update_layout(
        plot_bgcolor="#0a0a0a",  
        paper_bgcolor="rgba(0,0,0,0)",  
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],  # Rótulos
            tickfont=dict(color="white"), 
            gridcolor="#1c1c1c"  
        ),
        yaxis=dict(
            tickfont=dict(color="white"), 
            gridcolor="#1c1c1c"  
        ),
        title=dict(
            text=f"Distribuição de Magnitudes por Mês em {dff['Year'].iloc[0]}",  
            font=dict(size=22, color="white", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
        ),
        xaxis_title_font=dict(color="white"),  
        yaxis_title_font=dict(color="white"),  
    )

#-----------------------------------------------------------------------------
# Gráfico linha

    df_ano_grouped = (
        dff.groupby('Month')['Depth']
        .apply(lambda x: np.exp(np.log(x).mean()))  # Média logarítmica por mês
        .reset_index(name='Profundidade_Log_Media')
    )

    df_ano_grouped['Log_Std_Dev'] = (
        dff.groupby('Month')['Depth']
        .apply(lambda x: np.exp(np.log(x).std()))  # Desvio padrão logarítmico por mês
        .reset_index(name='Log_Std_Dev')['Log_Std_Dev']
    )

    fig_profundidade = px.line(
        df_ano_grouped,
        x='Month',
        y='Profundidade_Log_Media',
        labels={"Month": "Mês", "Profundidade_Log_Media": "Profundidade (km)"},
        title=f'Profundidade Média Logarítmica dos Terremotos por Mês em {option_slctd}',
        color_discrete_sequence=["#00ffc8"],
        width=850,
        height=350
    )

    fig_profundidade.update_traces(
        error_y=dict(
            type='data',
            array=df_ano_grouped['Log_Std_Dev'], 
            visible=True,
            color="white",
            thickness=1.5,
            width=4
        )
    )


    fig_profundidade.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], 
            tickfont=dict(color="white"),  
            gridcolor="#1c1c1c" 
        ),
        yaxis=dict(
            tickfont=dict(color="white"),  
            gridcolor="#1c1c1c" 
        ),
        plot_bgcolor="#0a0a0a",  
        paper_bgcolor="rgba(0,0,0,0)", 
        xaxis_title_font=dict(color="white"), 
        yaxis_title_font=dict(color="white"),  
        margin=dict(l=5, r=50, t=50, b=20),
    )


    fig_profundidade.update_layout(
        title=dict(
            text=f"Profundidade Média dos Terremotos por Mês em {option_slctd}",
            font=dict(size=22, color="white", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
        )
    )
#-----------------------------------------------------------------------------
# Gráfico barra
    month_counts = dff['Month'].value_counts().reset_index(name='Count')
    month_counts.columns = ['Month', 'Count']
    month_counts = month_counts.sort_values(by='Month')


    meses_nomes = ['Jan ', 'Fev ', 'Mar ', 'Abr ', 'Mai ', 'Jun ', 'Jul ', 'Ago ', 'Set ', 'Out ', 'Nov ', 'Dez ']
    month_counts['Month'] = month_counts['Month'].apply(lambda x: meses_nomes[x - 1])

    fig_bar = px.bar(
        month_counts,
        x='Count', 
        y='Month', 
        orientation='h',
        text='Count',
        labels={"Month": "Mês", "Count": "Casos"},
        title=f"Número de Terremotos por Mês em {option_slctd}",
        width=500,
        height=400,
    )

    fig_bar.update_layout(
        xaxis_title="",
        yaxis_title="Mês",
        title=dict(
            text=f"Número de Terremotos por Mês em {option_slctd}",
            font=dict(size=16, color="white", family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", 
        xaxis_title_font=dict(color="white"), 
        yaxis_title_font=dict(color="white"),
    )


    fig_bar.update_traces(
        texttemplate='%{text}', 
        textposition='outside', 
        marker=dict(color='#00ffc8', line=dict(color='white', width=1)) 
    )

    fig_bar.update_yaxes(
        tickfont=dict(color="white", size=14)
    )
    fig_bar.update_xaxes(
        showticklabels=False,
        showgrid=False
    )

    fig_bar.update_traces(textfont=dict(color='white'))

#-----------------------------------------------------------------------------

    return fig, text_info, terremotos_info, text_info2, fig_donut,fig_box,fig_profundidade, fig_bar

if __name__ == '__main__':
    app.run_server(debug=True)

