import sqlite3
from pathlib import Path

# Tenta achar o banco na mesma pasta deste script
DB_PATH = Path(__file__).parent / 'stockmaster.db'

print(f"📂 Analisando banco de dados em: {DB_PATH}")

if not DB_PATH.exists():
    print("❌ ERRO GRAVE: O arquivo stockmaster.db NÃO existe nesta pasta!")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n--- LISTA DE PRODUTOS NO BANCO ---")
        cursor.execute('SELECT id, codigobarras, nome FROM produtos')
        produtos = cursor.fetchall()
        
        if not produtos:
            print("⚠️ O banco existe, mas a tabela de produtos está VAZIA.")
        
        for p in produtos:
            id_prod, codigo, nome = p
            # Mostra o código entre aspas para vermos se tem espaços escondidos
            print(f"ID: {id_prod} | Código: '{codigo}' | Nome: {nome}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao ler o banco: {e}")

print("\n--- FIM DO RELATÓRIO ---")
input("Pressione ENTER para fechar...")