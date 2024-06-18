# Importe as bibliotecas necessárias
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib  # para salvar modelos
# from dados_tratados import *


def divisao_conjunto(df,alvo):
    # Divida os dados em recursos (X) e rótulos (y)
    X = df.drop(alvo, axis=1)
    y = df[alvo]

    # Divida os dados em conjuntos de treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    return X_train, X_test, y_train, y_test


def modelo_regressao(X_train, X_test, y_train, y_test):

    # 1. Regressão Logística
    logistic_model = LogisticRegression(random_state=42, max_iter=1000,solver='lbfgs')
    # modelo = LogisticRegression() 
    # Dimensionamento dos dados: Em alguns casos, a falta de convergência pode ser devido a problemas 
    # de escala nos dados. Normalizar ou dimensionar seus dados pode ajudar a melhorar a convergência.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logistic_model.fit(X_train_scaled, y_train)
    logistic_predictions = logistic_model.predict(X_test_scaled)

    # Avalie o desempenho do modelo de Regressão Logística
    accuracy_logistic = accuracy_score(y_test, logistic_predictions)
    report_logistic = classification_report(y_test, logistic_predictions,zero_division=1)

    return accuracy_logistic, report_logistic, logistic_model

def modelo_arvore_desision(X_train, X_test, y_train, y_test):

    # 2. Árvore de Decisão
    decision_tree_model = DecisionTreeClassifier(random_state=42)
    decision_tree_model.fit(X_train, y_train)
    decision_tree_predictions = decision_tree_model.predict(X_test)

    # Avalie o desempenho do modelo de Árvore de Decisão
    accuracy_decision_tree = accuracy_score(y_test, decision_tree_predictions)
    report_decision_tree = classification_report(y_test, decision_tree_predictions,zero_division=1)

    return accuracy_decision_tree, report_decision_tree, decision_tree_model

def modelo_random_forest(X_train, X_test, y_train, y_test):

    # 3. Random Forest
    random_forest_model = RandomForestClassifier(random_state=42)
    random_forest_model.fit(X_train, y_train)
    random_forest_predictions = random_forest_model.predict(X_test)

    # Avalie o desempenho do modelo Random Forest
    accuracy_random_forest = accuracy_score(y_test, random_forest_predictions)
    report_random_forest = classification_report(y_test, random_forest_predictions,zero_division=1)

    return accuracy_random_forest, report_random_forest, random_forest_model

# # Imprima os resultados
# print("----------------------------------------Resultados da Regressão Logística:--------------------------------")
# print(f'Acurácia: {accuracy_logistic*100:.2f}%')
# print("Relatório de Classificação:")
# print(report_logistic)

# print("\n--------------------------------------Resultados da Árvore de Decisão:----------------------------------")
# print(f'Acurácia: {accuracy_decision_tree*100:.2f}%')
# print("Relatório de Classificação:")
# print(report_decision_tree)

# print("\n--------------------------------------Resultados do Random Forest:--------------------------------------")
# print(f'Acurácia: {accuracy_random_forest*100:.2f}%')
# print("Relatório de Classificação:")
# print(report_random_forest)
def importancia(pd, X_test,modelo):
    col = list(X_test.columns)
    relatividade_importancia = pd.DataFrame(index=col, data=modelo.feature_importances_)
    relatividade_importancia = relatividade_importancia * 100

    return relatividade_importancia
# print(relatividade_importancia)