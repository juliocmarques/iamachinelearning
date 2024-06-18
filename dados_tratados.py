from funcoes_tratamento import *
from flask import Flask, request, render_template, jsonify, send_file, send_from_directory
from graficos_barras import *
from modelos_treinamento import *
from io import BytesIO
import os
import csv
# import chardet

app = Flask(__name__)

uploaded_filename = None  # Variável global para armazenar o nome do arquivo enviado
uploaded_filename_previsao = None
avaliar = None
limiar = 0
limite_superior_volume = 0
colunas_para_excluir = [] 
nome_modelo = None  # Adicionamos essa variável para armazenar o nome do modelo
regression_model_file = None 
decision_model_file = None
forest_model_file = None
caminho_completo_arquivo = None # Armazenar o caminho completo do arquivo
df_distinto = ...

# # Defina o caminho da pasta onde os arquivos serão salvos
# UPLOAD_FOLDER = 'Bases'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/get_upload', methods=['POST'])
def get_upload():
    global uploaded_filename, caminho_completo_arquivo  # Use a variável global    
    uploaded_file = request.files['file']

# Detect encoding
    # with open(uploaded_file, 'rb') as f:
    #     result = chardet.detect(f.read())

    if uploaded_file.filename != '':

        # # Salvar o arquivo na pasta UPLOAD_FOLDER
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        # uploaded_file.save(file_path)

        uploaded_filename = uploaded_file.filename  # Armazene o nome do arquivo
        caminho_completo_arquivo = os.path.splitext(uploaded_file.filename)[0].lower() + os.path.splitext(uploaded_file.filename)[1].lower()  # Caminho completo do arquivo        
        file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
        
        if file_extension == '.csv':        
            # uploaded_filename = pd.read_csv(uploaded_file, encoding=result['encoding'])        
            uploaded_filename = pd.read_csv(uploaded_file)        
        elif file_extension in ['.xls','.xlsx']:
            if file_extension == '.xls':
                uploaded_filename = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                uploaded_filename = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_extension == '.parquet':
            uploaded_filename = pd.read_parquet(uploaded_file)
        elif file_extension == '.html':
            uploaded_filename = pd.read_html(uploaded_file)[0]  # pd.read_html retorna uma lista de DataFrames
        elif file_extension == '.json':
            uploaded_filename = pd.read_json(uploaded_file)
        elif file_extension == '.xml':
            uploaded_filename = pd.read_xml(uploaded_file)
        else:
            return "Formato de arquivo não suportado"
                 
        info_table = pd.DataFrame({
            'Colunas': uploaded_filename.columns,
            'Distintos': uploaded_filename.nunique().astype(str),
            'Representatividade (%)': round((uploaded_filename.nunique() / len(uploaded_filename) * 100), 2).astype(str),
            'Nulos': uploaded_filename.isna().sum().values.tolist()
        })

        df_describe = uploaded_filename.describe(include='all').T
        df_head = uploaded_filename.head().T

        info_string = f"<h3>Resumo</h3>"
        info_string += f"<p>Número de linhas: {len(uploaded_filename)}</p>" #\n
        info_string += f"<p>Número de colunas: {len(uploaded_filename.columns)}</p>" #\n\n
        info_string += info_table.to_html(classes='table table-bordered  table-custom', index=False)
        # info_string += f"{info_table}"
        info_string_statistic = f"<h3>Estatistícas</h3>" #\n
        # info_string_statistic += df_describe.to_string()
        info_string_statistic += df_describe.to_html(classes='table table-bordered  table-custom')
        info_string_amostra = f"<h3>5 Amostras</h3>" #:\n
        info_string_amostra += df_head.to_html(classes='table table-bordered  table-custom')        
        # info_string_amostra += df_head.to_string()        
        campos = uploaded_filename.columns.tolist()

        return jsonify({'resumo': info_string,'describe': info_string_statistic, 'amostra': info_string_amostra, 'campos': campos})
    else:
        return 'Nenhum arquivo foi enviado.'


@app.route('/get_describe', methods=['GET'])
def get_describe():
    global uploaded_filename  # Use a variável global
    global colunas_para_excluir    
    # global avaliar  # Use a variável global
    global df_distinto, avaliar, limiar, limite_superior_volume, caminho_completo_arquivo
    global regression_model_file, decision_model_file, forest_model_file

    # Obtenha o valor do parâmetro 'avaliar' da solicitação
    # avaliar = request.args.get('avaliar')
    # print("rota:", avaliar)
    # avaliar = 'score_credito'

    if avaliar != None:

        df_identifica_numericos, lista_conversao = converter_colunas_numericas(uploaded_filename)
        df_trata_ausentes, ausentes_drop, ausentes_media, ausentes_moda = tratar_valores_ausentes(df_identifica_numericos,avaliar,limiar)
        colunas_para_excluir, proporcao, df_trata_cardinalidade = remove_alta_cardinalidade(df_trata_ausentes,avaliar,limite_superior_volume)
        tipo_transformados, df_converte_oject_paranumerico = transforma_tipo_paramodelo(df_trata_cardinalidade,avaliar)
        df_distinto = df_converte_oject_paranumerico.drop_duplicates()

        gerar_grafico(df_distinto)        
        gerar_grafico_agrupado(df_distinto)               
        gerar_grafico_boxplot(df_distinto)

        info_tratado = f"<h3>Tratamento dos dados</h3>"
        info_tratado += f"<p>Colunas convertidas: {lista_conversao}</p>" #\n
        info_tratado += f"<p>Dados ausentes excluídas: {ausentes_drop}</p>" #\n
        info_tratado += f"<p>Colunas substituidas pela média: {ausentes_media}</p>" #\n    
        info_tratado += f"<p>Colunas substituidas pela moda: {ausentes_moda}</p>" #\n    
        info_tratado += f"<p>Colunas excluídas com alta cardinalidade: {colunas_para_excluir}</p>" #\n    
        info_tratado += f"<p>Colunas excluídas proporção da base: {proporcao}</p>" #\n    
        info_tratado += f"<p>Colunas categorizados one hot: {tipo_transformados}</p>" #\n

        info_table = pd.DataFrame({
            'Colunas': df_distinto.columns,
            'Distintos': df_distinto.nunique().astype(str),
            'Representatividade (%)': round((df_distinto.nunique() / len(df_distinto) * 100), 2).astype(str),
            'Nulos': df_distinto.isna().sum().values.tolist()
        })

        df_describe = df_distinto.describe(include='all').T
        df_head = df_distinto.head().T

        info_string = f"<h3>Resumo</h3>"
        info_string += f"<p>Número de linhas: {len(df_distinto)}</p>" #\n
        info_string += f"<p>Número de colunas: {len(df_distinto.columns)}</p>" #\n\n
        info_string += info_table.to_html(classes='table table-bordered table-custom', index=False)
        # info_string += f"{info_table}"
        info_string_statistic = f"<h3>Estatistícas</h3>" #/n
        info_string_statistic += df_describe.to_html(classes='table table-bordered table-custom')
        # info_string_statistic += df_describe.to_string()
        info_string_amostra = f"<h3>5 Amostras</h3>" #/n
        info_string_amostra += df_head.to_html(classes='table table-bordered table-custom')
        # info_string_amostra += df_head.to_string()        

#-------------------------------grava no arquivo de modelo
        # Caminho do arquivo CSV
        csv_file_path = os.path.join(os.path.dirname(__file__), 'dados.csv')

        # Ler os dados existentes no arquivo CSV
        dados_existentes = []
        file_exists = os.path.isfile(csv_file_path)
        if file_exists:
            with open(csv_file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                dados_existentes = list(reader)

        # Verificar se o nome do modelo já existe
        modelo_existente = next((item for item in dados_existentes if item['nome_modelo'] == nome_modelo), None)

        if modelo_existente:
            # Atualizar o registro existente
            modelo_existente['Avaliar'] = avaliar
            modelo_existente['limiar'] = limiar
            modelo_existente['limite_superior_volume'] = limite_superior_volume
            modelo_existente['colunas_para_excluir'] = ', '.join(colunas_para_excluir)  # Converta a lista para string
            modelo_existente['regression_model_file'] = regression_model_file
            modelo_existente['decision_model_file'] = decision_model_file
            modelo_existente['forest_model_file'] = forest_model_file
            modelo_existente['caminho_completo_arquivo'] = caminho_completo_arquivo
        else:
            # Adicionar um novo registro
            dados_existentes.append({
                'Avaliar': avaliar,
                'limiar': limiar,
                'limite_superior_volume': limite_superior_volume,
                'nome_modelo': nome_modelo,
                'colunas_para_excluir': ', '.join(colunas_para_excluir),  # Converta a lista para string
                'regression_model_file': regression_model_file,
                'decision_model_file': decision_model_file,
                'forest_model_file': forest_model_file,
                'caminho_completo_arquivo': caminho_completo_arquivo
            })

        # Escrever todos os dados de volta para o arquivo CSV
        with open(csv_file_path, mode='w', newline='') as file:
            fieldnames = ['Avaliar', 'limiar', 'limite_superior_volume', 'nome_modelo', 'colunas_para_excluir','regression_model_file','decision_model_file','forest_model_file','caminho_completo_arquivo']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Escrever o cabeçalho
            writer.writeheader()

            # Escrever os dados
            writer.writerows(dados_existentes)
#------------------fim da gravação do modelo

        return jsonify({'resumo': info_string,'describe': info_string_statistic,'amostra': info_string_amostra, 'tratamento': info_tratado})
    else:
        info_string = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_string_statistic = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_string_amostra = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_tratado = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        return jsonify({'resumo': info_string,'describe': info_string_statistic,'amostra': info_string_amostra, 'tratamento': info_tratado})

@app.route('/get_modelo', methods=['GET'])
def get_modelo():
    global uploaded_filename, nome_modelo  # Use a variável global    
    # global avaliar  # Use a variável global
    global df_distinto, logistic_model, decision_tree_model, random_forest_model
    global avaliar, limiar, limite_superior_volume, caminho_completo_arquivo
    global regression_model_file, decision_model_file, forest_model_file

    # Obtenha o valor do parâmetro 'avaliar' da solicitação
    # avaliar = request.args.get('avaliar')
    # print("rota:", avaliar)
    # avaliar = 'score_credito'
    if avaliar != None:
        X_train, X_test, y_train, y_test = divisao_conjunto(df_distinto,avaliar)
        accuracy_rl, report_rl, logistic_model = modelo_regressao(X_train, X_test, y_train, y_test)
        accuracy_dt, report_dt, decision_tree_model = modelo_arvore_desision(X_train, X_test, y_train, y_test)
        accuracy_rf, report_rf, random_forest_model = modelo_random_forest(X_train, X_test, y_train, y_test)

        # Salvar modelo treinado em arquivo
        joblib.dump(logistic_model, nome_modelo + '_logistic_regression_model.pkl')
        joblib.dump(decision_tree_model, nome_modelo + '_decision_tree_model.pkl')
        joblib.dump(random_forest_model, nome_modelo + '_random_forest_model.pkl')

        regression_model_file = nome_modelo + '_logistic_regression_model.pkl'
        decision_model_file = nome_modelo + '_decision_tree_model.pkl'
        forest_model_file = nome_modelo + '_random_forest_model.pkl'

    #--------------------------------------grava o nome do arquivo na lista de modelos
        # Caminho do arquivo CSV
        csv_file_path = os.path.join(os.path.dirname(__file__), 'dados.csv')

        # Ler os dados existentes no arquivo CSV
        dados_existentes = []
        file_exists = os.path.isfile(csv_file_path)
        if file_exists:
            with open(csv_file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                dados_existentes = list(reader)

        # Verificar se o nome do modelo já existe
        modelo_existente = next((item for item in dados_existentes if item['nome_modelo'] == nome_modelo), None)

        if modelo_existente:
            # Atualizar o registro existente
            modelo_existente['Avaliar'] = avaliar
            modelo_existente['limiar'] = limiar
            modelo_existente['limite_superior_volume'] = limite_superior_volume
            modelo_existente['colunas_para_excluir'] = ', '.join(colunas_para_excluir)  # Converta a lista para string
            modelo_existente['regression_model_file'] = regression_model_file
            modelo_existente['decision_model_file'] = decision_model_file
            modelo_existente['forest_model_file'] = forest_model_file
            modelo_existente['caminho_completo_arquivo'] = caminho_completo_arquivo
        else:
            # Adicionar um novo registro
            dados_existentes.append({
                'Avaliar': avaliar,
                'limiar': limiar,
                'limite_superior_volume': limite_superior_volume,
                'nome_modelo': nome_modelo,
                'colunas_para_excluir': ', '.join(colunas_para_excluir),  # Converta a lista para string
                'regression_model_file': regression_model_file,
                'decision_model_file': decision_model_file,
                'forest_model_file': forest_model_file,
                'caminho_completo_arquivo': caminho_completo_arquivo
            })

        # Escrever todos os dados de volta para o arquivo CSV
        with open(csv_file_path, mode='w', newline='') as file:
            fieldnames = ['Avaliar', 'limiar', 'limite_superior_volume', 'nome_modelo', 'colunas_para_excluir','regression_model_file','decision_model_file','forest_model_file','caminho_completo_arquivo']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Escrever o cabeçalho
            writer.writeheader()

            # Escrever os dados
            writer.writerows(dados_existentes)

    #--------------------------------------fim da gravação
        # imp_lm = importancia(pd, X_test,logistic_model)
        imp_dt = importancia(pd, X_test,decision_tree_model)
        imp_rf = importancia(pd, X_test,random_forest_model)

        df_report_rl = classification_report_to_dataframe(report_rl)

        info_regressao = f"<h2>Resultados da Regressão Logística:</h2>" # \n\n"
        info_regressao += f"<p>Acurácia: {accuracy_rl*100:.2f}%</p>" #\n
        info_regressao += f"<h3>Relatório de Classificação:</h3>" # \n"
        info_regressao += df_report_rl.to_html(classes='table table-bordered table-custom', index=False)
        # info_regressao += f" {report_rl} \n"

        df_report_dt = classification_report_to_dataframe(report_dt)

        info_arvore = f"<h2>Resultados da Árvore de Decisão:</h2>" #\n\n"
        info_arvore += f"<p>Acurácia: {accuracy_dt*100:.2f}%</p>" #\n"
        info_arvore += f"<h3>Relatório de Classificação:</h3>" # \n"
        info_arvore += df_report_dt.to_html(classes='table table-bordered table-custom', index=False)
        # info_arvore += f" {report_dt} \n"

        df_report_rf = classification_report_to_dataframe(report_rf)

        info_random = f"<h2>Resultados do Random Forest:</h2>" # \n\n"
        info_random += f"<p>Acurácia: {accuracy_rf*100:.2f}%</p>" #\n"
        info_random += f"<h3>Relatório de Classificação:</h3>" # \n"
        info_random += df_report_rf.to_html(classes='table table-bordered table-custom', index=False)
        # info_random += f" {report_rf} \n"
        
        # Renomear as colunas dos DataFrames para "Forest" e "Arvore decisão"
        imp_dt.columns = ['Decision Tree']
        imp_rf.columns = ['Random Forest']

        # Concatenar os DataFrames ao longo do eixo das colunas
        result = pd.concat([imp_dt, imp_rf], axis=1)

        info_importancia = "<h3>Importancia relativa:</h3>" # \n\n"
        info_importancia += result.to_html(classes='table table-bordered table-custom', index=True)
        # info_importancia += f" {result} \n"

        return jsonify({'regressao': info_regressao,'arvore': info_arvore,'forest': info_random, 'importancia': info_importancia})
    else:
        info_regressao = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_arvore = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_random = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        info_importancia = f"<h2>É preciso efetuar a configuração do alvo a ser previsto.</h2>"
        return jsonify({'regressao': info_regressao,'arvore': info_arvore,'forest': info_random, 'importancia': info_importancia})

# Função de conversão dos relatórios do modelo de string para dataframe
def classification_report_to_dataframe(report):
    report_data = []
    lines = report.split('\n')
    for line in lines[2:-3]:
        row = {}
        row_data = line.split()
        
        # Preencha com valores em branco se não houver elementos suficientes
        while len(row_data) < 5:
            row_data.append('')
        
        row['class'] = row_data[0]
        row['precision'] = row_data[1]
        row['recall'] = row_data[2]
        row['f1-score'] = row_data[3]
        row['support'] = row_data[4]
        report_data.append(row)
        
    dataframe = pd.DataFrame.from_dict(report_data)
    return dataframe

@app.route('/get_csv_data', methods=['GET'])
def get_csv_data():
    csv_file_path = os.path.join(os.path.dirname(__file__), 'dados.csv')
    
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    
    return jsonify(data)


@app.route('/get_previsao', methods=['POST'])
def get_previsao():
    global colunas_para_excluir, logistic_model, decision_tree_model, random_forest_model
    global avaliar, limiar, limite_superior_volume,regression_model_file,decision_model_file,forest_model_file
    global uploaded_filename_previsao # Use a variável global        
  
    if request.is_json:
        data = request.get_json()

        avaliar = data.get('avaliar')
        limiar = data.get('limiar')
        limite_superior_volume = data.get('limite_superior_volume')
        
        if data.get('colunas_para_excluir') == '':
            colunas_para_excluir = []
        else:    
            colunas_para_excluir = data.get('colunas_para_excluir').split(', ')  # Converta a string de volta para uma lista                    

        regression_model_file = data.get('regression_model_file')
        decision_model_file = data.get('decision_model_file')
        forest_model_file = data.get('forest_model_file')
        info_previsao = ''
        info_tratado = ''
        info_string = ''
        info_string_statistic = ''
        info_string_amostra = '' 

        print(f"Opção 1 -: Colunas para excluir: {colunas_para_excluir} , Avaliar:{avaliar} , Limiar: {limiar} , Limite_superior_volume {limite_superior_volume}")

        return jsonify(data)

    else:

        uploaded_file = request.files['file']

        uploaded_filename_previsao = uploaded_file.filename  # Armazene o nome do arquivo
        file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
        
        if file_extension == '.csv':        
            uploaded_filename_previsao = pd.read_csv(uploaded_file)        
        elif file_extension in ['.xls','.xlsx']:
            if file_extension == '.xls':
                uploaded_filename_previsao = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                uploaded_filename_previsao = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_extension == '.parquet':
            uploaded_filename_previsao = pd.read_parquet(uploaded_file)
        elif file_extension == '.html':
            uploaded_filename_previsao = pd.read_html(uploaded_file)[0]  # pd.read_html retorna uma lista de DataFrames
        elif file_extension == '.json':
            uploaded_filename_previsao = pd.read_json(uploaded_file)
        elif file_extension == '.xml':
            uploaded_filename_previsao = pd.read_xml(uploaded_file)
        else:
            return "Formato de arquivo não suportado"

        # Remover o campo alvo dos dados de previsão
        if avaliar in uploaded_filename_previsao.columns:
            uploaded_filename_previsao = uploaded_filename_previsao.drop(columns=[avaliar])
        else:
            uploaded_filename_previsao = uploaded_filename_previsao.copy()  # Se o campo alvo não estiver presente, usar todos os dados

        df_sem_colunas_altas = uploaded_filename_previsao.drop(colunas_para_excluir, axis=1) # Remove as colunas com contagem alta
        tipo_transformados, df_previsao = transforma_tipo_paramodelo(df_sem_colunas_altas,avaliar)


        # Condição para modelos selecionados ou não::::::::
        # if regression_model_file != '':
            # loaded_logistic_model = joblib.load(regression_model_file)
            # previsoes_logistic = loaded_logistic_model.predict(df_previsao)
        # else:
            # previsoes_logistic = logistic_model.predict(df_previsao)
        if decision_model_file != '':
            loaded_decision_tree_model = joblib.load(decision_model_file)
            previsoes_decision_tree = loaded_decision_tree_model.predict(df_previsao)
        else:
            previsoes_decision_tree = decision_tree_model.predict(df_previsao)

        if forest_model_file != '':    
            loaded_random_forest_model = joblib.load(forest_model_file)
            previsoes_random_forest = loaded_random_forest_model.predict(df_previsao)
        else:
            previsoes_random_forest = random_forest_model.predict(df_previsao)

        info_tratado = "<h3>Tratamento aplicado para previsão:</h3>" # \n\n"
        info_tratado += f"<p>Colunas excluídas com alta cardinalidade: {colunas_para_excluir}</p>" #\n"    
        info_tratado += f"<p>Colunas categorizados one hot: {tipo_transformados}<p/>" #\n"

        df_previsoes_decision_tree = pd.DataFrame(previsoes_decision_tree)
        info_previsao = "<h3>Previsões aplicando Árvore de Decisão:</h3>" # \n\n"
        info_previsao += df_previsoes_decision_tree.to_html(classes='table table-bordered table-custom', index=False)
        # info_previsao += f" {previsoes_decision_tree} \n\n\n"
        df_previsoes_random_forest = pd.DataFrame(previsoes_random_forest)
        info_previsao += "<h3>Previsões aplicando Random Forest:</h3>" # \n\n"
        info_previsao += df_previsoes_random_forest.to_html(classes='table table-bordered table-custom', index=False)
        # info_previsao += f" {previsoes_random_forest} \n"

        info_table = pd.DataFrame({
            # 'Colunas': uploaded_filename.columns,
            'Distintos': uploaded_filename_previsao.nunique().astype(str),
            'Representatividade (%)': round((uploaded_filename_previsao.nunique() / len(uploaded_filename_previsao) * 100), 2).astype(str),
            'Nulos': uploaded_filename_previsao.isna().sum().values.tolist()
        })

        df_describe = uploaded_filename_previsao.describe(include='all').T
        uploaded_filename_previsao[f"{avaliar}_random"] = previsoes_random_forest
        uploaded_filename_previsao[f"{avaliar}_arvore"] = previsoes_decision_tree      

        df_head = uploaded_filename_previsao.head().T

        info_string = f"<p>Número de linhas: {len(uploaded_filename_previsao)}</p>" #\n"
        info_string += f"<p>Número de colunas: {len(uploaded_filename_previsao.columns)}</p>" #\n\n"
        info_string += info_table.to_html(classes='table table-bordered table-custom', index=True)        
        # info_string += f"{info_table}"
        info_string_statistic = f"<h3>Estatistícas</h3>"
        info_string_statistic += df_describe.to_html(classes='table table-bordered table-custom', index=True)        
        # info_string_statistic += df_describe.to_string()
        info_string_amostra = f"<h3>5 Amostras</h3>" #\n"
        info_string_amostra += df_head.to_html(classes='table table-bordered table-custom', index=True)        
        # info_string_amostra += df_head.to_string()        

        print(f"Opção 2 -: Colunas para excluir: {colunas_para_excluir} , Avaliar:{avaliar} , Limiar: {limiar} , Limite_superior_volume {limite_superior_volume}")

    return jsonify({'previsao': info_previsao,'tratamento': info_tratado,'resumo': info_string,'describe': info_string_statistic, 'amostra': info_string_amostra})


@app.route('/download')
def download_file():
    global uploaded_filename_previsao

    csv_data = BytesIO()
    # TO DO
    uploaded_filename_previsao.to_csv(csv_data) #, index=False, encoding='utf-8')
    csv_data.seek(0)

    # Envie o arquivo CSV para download
    return send_file(csv_data,as_attachment=True, download_name='dados.csv',mimetype='application/octet-stream')

@app.route('/sua_rota', methods=['POST'])
def sua_funcao():
    global avaliar, limiar, limite_superior_volume, nome_modelo, colunas_para_excluir, caminho_completo_arquivo
    global regression_model_file, decision_model_file, forest_model_file
    # Receba os valores enviados pelo JavaScript
    data = request.get_json()

    # Acesse os valores do campo-select e dos input ranges
    avaliar = data.get('campoSelectValue')
    limiar = float(data.get('percentagem1Value'))/100
    limite_superior_volume = float(data.get('percentagem2Value'))/100
    nome_modelo = data.get('nomeModelo')  # Recebendo o nome do modelo

    # # Faça alguma ação com os valores
    # # Por exemplo, você pode imprimi-los para verificação:
    # print(f'Campo Select: {avaliar}')
    # print(f'Percentagem 1: {limiar}')
    # print(f'Percentagem 2: {limite_superior_volume}')
    # print(f'Nome do Modelo: {nome_modelo}')
    # print(f'Colunas para excluir: {colunas_para_excluir}')
    # print(f'Modelo regressão: {regression_model_file}')
    # print(f'Modelo Decision: {decision_model_file}')
    # print(f'Modelo Forest: {forest_model_file}')
    # print(f'caminho_completo_arquivo: {caminho_completo_arquivo}')

    # Caminho do arquivo CSV
    csv_file_path = os.path.join(os.path.dirname(__file__), 'dados.csv')

 # Ler os dados existentes no arquivo CSV
    dados_existentes = []
    file_exists = os.path.isfile(csv_file_path)
    if file_exists:
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            dados_existentes = list(reader)

    # Verificar se o nome do modelo já existe
    modelo_existente = next((item for item in dados_existentes if item['nome_modelo'] == nome_modelo), None)

    if modelo_existente:
        # Atualizar o registro existente
        modelo_existente['Avaliar'] = avaliar
        modelo_existente['limiar'] = limiar
        modelo_existente['limite_superior_volume'] = limite_superior_volume
        modelo_existente['colunas_para_excluir'] = colunas_para_excluir        
        modelo_existente['regression_model_file'] = regression_model_file
        modelo_existente['decision_model_file'] = decision_model_file
        modelo_existente['forest_model_file'] = forest_model_file
        modelo_existente['caminho_completo_arquivo'] = caminho_completo_arquivo
    else:
        # Adicionar um novo registro
        dados_existentes.append({
            'Avaliar': avaliar,
            'limiar': limiar,
            'limite_superior_volume': limite_superior_volume,
            'nome_modelo': nome_modelo,
            'colunas_para_excluir': colunas_para_excluir,
            'regression_model_file': regression_model_file,
            'decision_model_file': decision_model_file,
            'forest_model_file': forest_model_file,
            'caminho_completo_arquivo': caminho_completo_arquivo                                    
        })

    # Escrever todos os dados de volta para o arquivo CSV
    with open(csv_file_path, mode='w', newline='') as file:
        fieldnames = ['Avaliar', 'limiar', 'limite_superior_volume', 'nome_modelo','colunas_para_excluir','regression_model_file','decision_model_file','forest_model_file','caminho_completo_arquivo']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Escrever o cabeçalho
        writer.writeheader()

        # Escrever os dados
        writer.writerows(dados_existentes)

    # Responda com uma mensagem de sucesso (opcional)
    return jsonify({'message': 'Valores recebidos com sucesso!'})

# Rota para download de arquivos
@app.route('/download/<path:filename>', methods=['GET'])
def download_f(filename):
    # Verifica se o arquivo existe
    if os.path.exists(filename):
        return send_from_directory(directory='.', path=filename, as_attachment=True)
    else:
        return jsonify({"error": "Arquivo não encontrado"}), 404

if __name__ == '__main__':
    app.run()
