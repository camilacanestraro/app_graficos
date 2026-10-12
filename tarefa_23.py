import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px


# ==========================================
# 1. FUNÇÃO DE CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================
def carregar_e_tratar_dados(caminho_csv: str) -> pd.DataFrame:
    """Carrega o arquivo CSV e faz as conversões de tipos necessárias."""
    df = pd.read_csv(caminho_csv)

    # Conversão de colunas numéricas
    df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce').fillna(0)
    df['Desconto'] = pd.to_numeric(df['Desconto'], errors='coerce').fillna(0)
    df['Qtd_Vendidos'] = pd.to_numeric(df['Qtd_Vendidos'], errors='coerce').fillna(0)
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce').fillna(0)

    # Tratar valores ausentes em categóricas
    df['Gênero'] = df['Gênero'].fillna('Não Especificado')
    df['Marca'] = df['Marca'].fillna('Outros')

    return df


# Instanciar dados globais
df_dados = carregar_e_tratar_dados('ecommerce_estatistica.csv')

# ==========================================
# 2. INICIALIZAÇÃO DA APLICAÇÃO DASH
# ==========================================
app = dash.Dash(__name__)
app.title = "Dashboard e-Commerce - Análise Estatística"


# ==========================================
# 3. CONSTRUÇÃO DO LAYOUT
# ==========================================
def criar_layout(df: pd.DataFrame):
    """Gera a estrutura HTML e componentes visuais do aplicativo."""
    generos_disponiveis = [{'label': 'Todos os Gêneros', 'value': 'TODOS'}] + [
        {'label': g, 'value': g} for g in sorted(df['Gênero'].unique())
    ]

    return html.Div([
        html.H1("Dashboard e-Commerce - Análise Estatística", style={'textAlign': 'center'}),
        html.P("Painel dinâmico e interativo para análise de vendas e produtos.", style={'textAlign': 'center'}),

        # --- Painel de Filtros / Controles Interativos ---
        html.Div([
            html.Div([
                html.Label("Selecione o Gênero:"),
                dcc.Dropdown(
                    id='filtro-genero',
                    options=generos_disponiveis,
                    value='TODOS',
                    clearable=False
                )
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Faixa de Preço Máxima (R$):"),
                dcc.Slider(
                    id='filtro-preco',
                    min=int(df['Preço'].min()),
                    max=int(df['Preço'].max()),
                    step=10,
                    value=int(df['Preço'].max()),
                    marks={i: f'R${i}' for i in range(0, int(df['Preço'].max()) + 1, 100)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ], style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px', 'borderRadius': '8px'}),

        # --- Grade de Gráficos ---
        html.Div([
            dcc.Graph(id='grafico-histograma'),
            dcc.Graph(id='grafico-pizza'),
            dcc.Graph(id='grafico-bolhas'),
            dcc.Graph(id='grafico-linhas'),
            dcc.Graph(id='grafico-3d'),
            dcc.Graph(id='grafico-barras'),
        ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'})
    ], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


app.layout = criar_layout(df_dados)


# ==========================================
# 4. CALLBACKS PARA ATUALIZAÇÃO DINÂMICA
# ==========================================
@app.callback(
    [
        Output('grafico-histograma', 'figure'),
        Output('grafico-pizza', 'figure'),
        Output('grafico-bolhas', 'figure'),
        Output('grafico-linhas', 'figure'),
        Output('grafico-3d', 'figure'),
        Output('grafico-barras', 'figure'),
    ],
    [
        Input('filtro-genero', 'value'),
        Input('filtro-preco', 'value')
    ]
)
def atualizar_graficos(genero_selecionado, preco_maximo):
    """Atualiza automaticamente todas as figuras quando os filtros mudam."""
    # Filtrar os dados com base na interação do usuário
    df_filtrado = df_dados[df_dados['Preço'] <= preco_maximo]

    if genero_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['Gênero'] == genero_selecionado]

    # 1. Histograma
    fig_hist = px.histogram(
        df_filtrado, x='Preço', nbins=30,
        title='Distribuição de Preços (Histograma)'
    )

    # 2. Pizza
    fig_pie = px.pie(
        df_filtrado, names='Gênero',
        title='Proporção de Produtos por Gênero (Pizza)'
    )

    # 3. Bolhas
    fig_bubble = px.scatter(
        df_filtrado, x='Preço', y='Desconto', size='Qtd_Vendidos',
        color='Gênero', hover_name='Título',
        title='Relação Preço x Desconto (Bolhas)'
    )

    # 4. Linhas
    fig_line = px.line(
        df_filtrado, y='Qtd_Vendidos',
        title='Tendência de Vendas (Linhas)'
    )

    # 5. 3D
    fig_3d = px.scatter_3d(
        df_filtrado, x='Preço', y='Nota', z='Desconto', color='Gênero',
        title='Análise Tridimensional: Preço, Nota e Desconto (3D)'
    )

    # 6. Barras (Top 10 Marcas)
    df_bar = df_filtrado.groupby('Marca')['Qtd_Vendidos'].sum().reset_index()
    df_bar = df_bar.sort_values(by='Qtd_Vendidos', ascending=False).head(10)
    fig_bar = px.bar(
        df_bar, x='Marca', y='Qtd_Vendidos',
        title='Total de Vendas por Marca - Top 10 (Barras)'
    )

    return fig_hist, fig_pie, fig_bubble, fig_line, fig_3d, fig_bar


# ==========================================
# 5. EXECUÇÃO DA APLICAÇÃO
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)