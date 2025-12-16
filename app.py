import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Configuração
app = Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
CORS(app)

# Banco de dados SQLite para velocidade (cria arquivo iot_agro.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iot_agro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DE DADOS (ORM) ---
class LeituraSolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    # Solo
    ph = db.Column(db.Float)
    umidade = db.Column(db.Float)
    ec = db.Column(db.Float) # Condutividade
    n = db.Column(db.Float)  # Nitrogênio
    p = db.Column(db.Float)  # Fósforo
    k = db.Column(db.Float)  # Potássio
    temp_solo = db.Column(db.Float)
    # Ambiente
    temp_ar = db.Column(db.Float)
    umidade_ar = db.Column(db.Float)
    chuva = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'ph': self.ph, 'umidade': self.umidade, 'ec': self.ec,
            'n': self.n, 'p': self.p, 'k': self.k,
            'temp_solo': self.temp_solo, 'temp_ar': self.temp_ar,
            'umidade_ar': self.umidade_ar, 'chuva': self.chuva
        }

# Inicializa o banco ao rodar
with app.app_context():
    db.create_all()

# --- API ENDPOINTS ---

@app.route('/api/solo', methods=['POST'])
def receber_dados():
    data = request.json
    nova_leitura = LeituraSolo(
        ph=data.get('ph'), umidade=data.get('umidade'), ec=data.get('ec'),
        n=data.get('n'), p=data.get('p'), k=data.get('k'),
        temp_solo=data.get('temp_solo'), temp_ar=data.get('temp_ar'),
        umidade_ar=data.get('umidade_ar'), chuva=data.get('chuva', 0)
    )
    db.session.add(nova_leitura)
    db.session.commit()
    return jsonify({"message": "Dados salvos com sucesso", "id": nova_leitura.id}), 201

@app.route('/api/solo', methods=['GET'])
def listar_dados():
    # Retorna os últimos 100 registros para o gráfico não ficar pesado
    leituras = LeituraSolo.query.order_by(LeituraSolo.timestamp.desc()).limit(100).all()
    # Inverte para o gráfico mostrar cronologicamente (antigo -> novo)
    return jsonify([l.to_dict() for l in reversed(leituras)])

@app.route('/api/predicao', methods=['GET'])
def predicao_real():
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        modelo_path = os.path.join(basedir, 'modelos', 'modelo_producao.pkl')

        if not os.path.exists(modelo_path):
           return jsonify({"produtividade_estimada_kg": 0, "status": "Modelo não encontrado"}), 200

        with open(modelo_path, 'rb') as f:
            modelo = pickle.load(f)

        # 2. Pegar a última leitura do banco
        ultima = LeituraSolo.query.order_by(LeituraSolo.timestamp.desc()).first()
        
        if not ultima:
            return jsonify({"erro": "Sem dados de solo para prever"}), 404

        # 3. Preparar o DataFrame (A ordem das colunas DEVE ser igual ao treino)
        # O script de treino usou: ph, umidade, ec, n, p, k, temp_solo, temp_ar, chuva
        dados_input = pd.DataFrame([{
            'ph': ultima.ph, 
            'umidade': ultima.umidade, 
            'ec': ultima.ec,
            'n': ultima.n, 
            'p': ultima.p, 
            'k': ultima.k,
            'temp_solo': ultima.temp_solo, 
            'temp_ar': ultima.temp_ar, 
            'chuva': ultima.chuva
        }])

        # 4. Fazer a previsão
        predicao = modelo.predict(dados_input)[0]

        return jsonify({
            "produtividade_estimada_kg": round(predicao, 2),
            "confianca": "Alta (Random Forest Real)"
        })

    except Exception as e:
        print(f"Erro na predicao: {e}") # Mostra no terminal se der erro
        return jsonify({"erro": str(e)}), 500

# --- DASHBOARD ROUTES ---
@app.route('/')
def dashboard():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)