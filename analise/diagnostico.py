import os
import sqlite3

# 1. Descobrir onde estamos e onde o banco deveria estar
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_banco = os.path.abspath(os.path.join(diretorio_atual, '..', 'iot_agro.db'))

print(f"📍 Diretório do script: {diretorio_atual}")
print(f"🔍 Procurando banco em: {caminho_banco}")

# 2. Verificar se o arquivo existe fisicamente
if not os.path.exists(caminho_banco):
    print("❌ ERRO FATAL: O arquivo 'iot_agro.db' NÃO existe nesse caminho.")
    print("📂 Arquivos encontrados na pasta pai:")
    print(os.listdir(os.path.join(diretorio_atual, '..')))
else:
    print("✅ Arquivo de banco encontrado!")
    
    # 3. Tentar conectar e ler dados
    try:
        conn = sqlite3.connect(caminho_banco)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print(f"📋 Tabelas no banco: {tabelas}")

        # Verificar contagem de linhas
        if len(tabelas) > 0:
            cursor.execute("SELECT count(*) FROM leitura_solo")
            contagem = cursor.fetchone()[0]
            print(f"📊 Total de registros de solo: {contagem}")
            
            if contagem == 0:
                print("⚠️ O banco existe, as tabelas existem, mas está VAZIO. Rode a simulação mais tempo.")
            elif contagem < 50:
                print("⚠️ O banco tem dados, mas POUCOS (menos de 50). O script de treino bloqueia isso.")
            else:
                print("🚀 Tudo pronto para treinar! O problema deve estar no script de treino original.")
        else:
            print("❌ O banco existe mas não tem tabelas. O app.py não criou a estrutura (db.create_all).")

        conn.close()
    except Exception as e:
        print(f"❌ Erro ao ler o banco: {e}")