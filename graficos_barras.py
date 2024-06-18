import pandas as pd
import plotly.express as px

# Seus dados
# data = pd.read_csv('clientes.csv')

def gerar_grafico(data):

    df = data.describe()

    colunas = [col for col in df.columns if col != 'count']

    # Configurações do gráfico
    fig = px.bar(df, x=colunas, y=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'],
                # title="Resumo Estatístico por Coluna",
                labels={'value': 'Valor', 'variable': 'Métrica', 'x': 'Coluna'},
                height=335)
    
    # Girar os rótulos do eixo x para facilitar a leitura
    fig.update_xaxes(categoryorder='total ascending')
    fig.update_xaxes(tickangle=45)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto, sans-serif", color="white", size=10),
        # bargap=0.2,
        # margin=dict(l=50, r=50, t=30, b=100),
        # width=900,  # Definindo a largura do gráfico
        legend=dict(
            font=dict(size=10),  # Ajustando o tamanho da fonte da legenda
            orientation="h",  # Colocando a legenda verticalmente
            # traceorder="normal",  # Exibir todas as entradas da legenda
            yanchor="top",
            y=1.3,
            xanchor="left",
            x=0, # Ajustando a posição horizontal da legenda
            title='',
            itemsizing='constant'             
        )
    )

    fig.write_html(f'./static/grafico_barras.html')
    # Mostrar o gráfico
    # fig.show()

def gerar_grafico_agrupado(data):
    df = data.describe().T.reset_index()  # Transforma e reseta o índice para facilitar a manipulação
    df_melted = df.melt(id_vars='index', value_vars=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'])
    
    # Configurações do gráfico de barras agrupadas
    fig = px.bar(df_melted, x='index', y='value', color='variable',
                #  title="Resumo Estatístico por Coluna",
                 labels={'value': 'Valor', 'variable': 'Coluna', 'index': 'Métrica'},
                 height=335,
                 barmode='group')

    # Girar os rótulos do eixo x para facilitar a leitura
    fig.update_xaxes(tickangle=45)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto, sans-serif", color="white", size=9),
        # bargap=0.2,
        # margin=dict(l=50, r=50, t=30, b=100),
        # width=600,  # Definindo a largura do gráfico
        legend=dict(
            font=dict(size=10),  # Ajustando o tamanho da fonte da legenda
            orientation="h",  # Colocando a legenda verticalmente
            # traceorder="normal",  # Exibir todas as entradas da legenda
            yanchor="top",
            y=1.3,
            xanchor="left",
            x=0,  # Ajustando a posição horizontal da legenda
            title='',
            itemsizing='constant'             
        )
    )

    fig.write_html('./static/grafico_barras_agrupado.html')

def gerar_grafico_boxplot(data):
    df_melted = data.melt(var_name='Coluna', value_name='Valor')

    # Configurações do gráfico de caixas
    fig = px.box(df_melted, x='Coluna', y='Valor',
                #  title="Resumo Estatístico por Coluna",
                 labels={'Valor': 'Valor', 'Coluna': 'Coluna'},
                 height=330)

    # Girar os rótulos do eixo x para facilitar a leitura
    fig.update_xaxes(tickangle=45)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto, sans-serif", color="white", size=9),
        margin=dict(l=20, r=20, t=30, b=50)
        # width=600  # Definindo a largura do gráfico
    )


    fig.write_html(f'./static/grafico_caixas.html')


# # Dados fornecidos
# dados = {
#     "Column": ["ID", "No_Pation", "Gender", "AGE", "Urea", "Cr", "HbA1c", "Chol", "TG", "HDL", "LDL", "VLDL", "BMI", "CLASS"],
#     "Distincts": [800, 961, 3, 50, 110, 113, 111, 77, 69, 48, 65, 60, 64, 5],
#     "Representativity (%)": [80.0, 96.1, 0.3, 5.0, 11.0, 11.3, 11.1, 7.7, 6.9, 4.8, 6.5, 6.0, 6.4, 0.5],
#     "Nulls": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# }

# def gerar_grafico_repres_barras_dist(data):

#     df = pd.DataFrame(data)

#     # Gráfico de Barras para Distintos
#     fig_distincts = px.bar(df, x="Column", y="Distincts", title="Número de Valores Distintos por Coluna")
#     fig_distincts.show()

#     # Gráfico de Barras para Representatividade
#     fig_representativity = px.bar(df, x="Column", y="Representativity (%)", title="Representatividade Percentual por Coluna")
#     fig_representativity.show()

# # def graf_barras_emp_repres(data)


# def gerar_grafico_repres_barras_dist(data):

#     df = pd.DataFrame(data)

#     # Prepare data for stacked bar chart
#     df_melted = df.melt(id_vars="Column", value_vars=["Distincts", "Representativity (%)"], var_name="Metric", value_name="Value")

#     # Stacked bar chart
#     fig_stacked = px.bar(df_melted, x="Column", y="Value", color="Metric", title="Valores Distintos e Representatividade Percentual por Coluna")
#     fig_stacked.show()

# # gerar_grafico_repres_barras_dist(dados)

# import plotly.graph_objects as go

# def heatmap(data):

#     df = pd.DataFrame(data)

#     # Heatmap para Distintos
#     fig_heatmap_distincts = go.Figure(data=go.Heatmap(
#         z=df["Distincts"],
#         x=df["Column"],
#         y=["Distincts"],
#         colorscale='Viridis'
#     ))
#     fig_heatmap_distincts.update_layout(title="Heatmap de Valores Distintos por Coluna")
#     fig_heatmap_distincts.show()

#     # Heatmap para Representatividade
#     fig_heatmap_representativity = go.Figure(data=go.Heatmap(
#         z=df["Representativity (%)"],
#         x=df["Column"],
#         y=["Representativity (%)"],
#         colorscale='Viridis'
#     ))
#     fig_heatmap_representativity.update_layout(title="Heatmap de Representatividade Percentual por Coluna")
#     fig_heatmap_representativity.show()

# # heatmap(dados)