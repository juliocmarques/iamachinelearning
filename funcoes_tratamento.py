import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

# Campo alvo de previsão
# avaliar =  'score_credito' #'Cliente_Alvo'
# limiar = 0.1 # Limite % de nulos considerando exclusão da base (Ausentes)
# limite_superior_volume = 0.10  # Limite de cardinalidade (alta cardinalidade)

# Conversão para númerico
def converter_colunas_numericas(df):
    lista_colunas_convertidas = []
    for coluna in df.columns:
        # Verifica se a coluna é do tipo 'object'
        if df[coluna].dtype == 'object':
            # Tenta converter os valores da coluna para float, ignorando erros
            try:
                # Verifique se todos os valores na coluna podem ser convertidos para float
                if df[coluna].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().all():
                    df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
                    lista_colunas_convertidas.append(coluna)
            except ValueError:
                pass  # Não foi possível converter, mantenha como 'object'
    return df, lista_colunas_convertidas

# #tratamento de valores ausentes:
def tratar_valores_ausentes(df,campo_alvo,limiar):
    lista_ausentes_drop = []
    lista_ausentes_mode = []
    lista_ausentes_mean = []

    for coluna in df.columns:

        porcentagem_nulos = df[coluna].isnull().sum() / len(df) #* 100

        if coluna != campo_alvo and porcentagem_nulos > 0:
            if porcentagem_nulos < limiar: 
                # Exclua os registros nulos na coluna
                df = df.dropna(subset=[coluna])
                lista_ausentes_drop.append(coluna)

            elif df[coluna].dtype == 'object':
                # Preencha valores ausentes com o valor mais frequente (modo)
                df[coluna].fillna(df[coluna].mode()[0], inplace=True)
                lista_ausentes_mode.append(coluna)

            elif np.issubdtype(df[coluna].dtype, np.number):
                # Preencha valores ausentes com a média
                df[coluna].fillna(df[coluna].mean(), inplace=True)
                lista_ausentes_mean.append(coluna)
            else:
                print("Não há dados ausentes")                
    return df, lista_ausentes_drop, lista_ausentes_mean, lista_ausentes_mode

# ou remava uma lista de colunas com alta cardinalidade
def remove_alta_cardinalidade(df,campo_alvo,limite):
    
    # if len(df) > 99000: 
    #     limite_superior_volume = 0.10
    # else:
    #     limite_superior_volume = 1.10

    limite_superior = len(df) * limite # Calcula o limite superior de contagem distintos (10% do total de registros)
    colunas_para_excluir = [] # Lista para armazenar as colunas a serem excluídas
    contagem_distinta = df.nunique() # Calcula a contagem distintos para cada coluna
    lista_percentual = []
    # Itera pelas colunas e verifica se a contagem é superior ao limite
    for coluna, contagem in contagem_distinta.items():
        if contagem > limite_superior and coluna != campo_alvo:
            colunas_para_excluir.append(coluna)
            per_coluna =  (contagem / len(df)) * 100
            lista_percentual.append(per_coluna)

    df_x = df.drop(colunas_para_excluir, axis=1) # Remove as colunas com contagem alta
    return colunas_para_excluir, lista_percentual, df_x


# Ou converta todas as colunas object em númerico pois os modelos não trabalham com texto
def transforma_tipo_paramodelo(df,campo_alvo):
    tranforme = LabelEncoder()
    lista_campos_transformados = []
    for col in df.columns:
        if df[col].dtype == "object" and col != campo_alvo:
            df[col] = tranforme.fit_transform(df[col])            
            lista_campos_transformados.append(col)
            
    return lista_campos_transformados, df

