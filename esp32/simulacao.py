import requests
import random
import time
import json

URL = "http://localhost:5000/api/solo"

print(f"📡 Iniciando simulação de sensores ESP32 -> Enviando para {URL}")

def gerar_dados():
    # Simula variações realistas
    return {
        "ph": round(random.uniform(5.5, 7.5), 2),
        "umidade": round(random.uniform(20.0, 45.0), 2),
        "ec": round(random.uniform(0.5, 2.5), 2),
        "n": round(random.uniform(10, 50), 2),
        "p": round(random.uniform(5, 30), 2),
        "k": round(random.uniform(10, 40), 2),
        "temp_solo": round(random.uniform(20, 30), 2),
        "temp_ar": round(random.uniform(25, 35), 2),
        "umidade_ar": round(random.uniform(40, 80), 2),
        "chuva": 0 if random.random() > 0.1 else random.uniform(1, 5)
    }

while True:
    try:
        dados = gerar_dados()
        resp = requests.post(URL, json=dados)
        print(f"✅ Enviado: pH={dados['ph']} | Umidade={dados['umidade']}% | Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    time.sleep(2) # Envia a cada 2 segundos