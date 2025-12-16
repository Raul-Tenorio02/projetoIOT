import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pickle
import os

# Caminho do banco (ajuste se necessário dependendo de onde rodar)

DB_PATH = os.path.join('..', 'instance', 'iot_agro.db')

def treinar():
    if not os.path.exists(DB_PATH):
        print("Banco de dados ainda não criado ou vazio.")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Carrega dados
    query = "SELECT ph, umidade, ec, n, p, k, temp_solo, temp_ar, chuva FROM leitura_solo"
    df = pd.read_sql(query, conn)
    conn.close()

    if len(df) < 50:
        print(f"⚠️ Dados insuficientes para treino ({len(df)} registros). Rode a simulação mais tempo.")
        return

    # --- Feature Engineering (Criar Target Simulado para Exemplo) ---
    # Na vida real, teríamos uma coluna 'produtividade' medida. 
    # Aqui vamos criar uma fórmula sintética para o modelo 'aprender' algo coerente.
    # Produtividade = f(NPK, Umidade)
    df['produtividade_kg'] = (df['n']*1.5 + df['p']*1.2 + df['k']*0.8 + df['umidade']*2) * 10 

    X = df.drop(columns=['produtividade_kg'])
    y = df['produtividade_kg']

    # Treino
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)

    # Avaliação
    preds = model.predict(X_test)
    erro = mean_absolute_error(y_test, preds)
    print(f"✅ Modelo Treinado! MAE (Erro Médio Absoluto): {erro:.2f} kg")

    # Salvar
    if not os.path.exists('../modelos'):
        os.makedirs('../modelos')
    
    with open('../modelos/modelo_producao.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("💾 Modelo salvo em modelos/modelo_producao.pkl")

if __name__ == "__main__":
    treinar()