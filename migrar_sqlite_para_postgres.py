import sqlite3
import psycopg2
import psycopg2.extras
import json

# ===============================
# CONFIGURAÇÕES
# ===============================

# 🔹 BANCO LOCAL (ESCOLHA UM)

USAR_SQLITE = True   # True = SQLite | False = PostgreSQL local

SQLITE_PATH = "stockmaster.db"  # se for SQLite

POSTGRES_LOCAL = {               # se for PostgreSQL local
    "host": "localhost",
    "database": "stockmaster",
    "user": "postgres",
    "password": "pSQL2026",
    "port": 5432
}

# 🔹 SUPABASE (DESTINO)
SUPABASE = {
    "host": "aws-1-sa-east-1.pooler.supabase.com",
    "database": "postgres",
    "user": "postgres.dfcmibsztfmzvtheaeoh",
    "password": "sBASE2026!data",
    "port": 5432
}

# ===============================
# CONEXÕES
# ===============================

def conectar_local():
    if USAR_SQLITE:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        return psycopg2.connect(**POSTGRES_LOCAL)

def conectar_supabase():
    return psycopg2.connect(
        host=SUPABASE["host"],
        database=SUPABASE["database"],
        user=SUPABASE["user"],
        password=SUPABASE["password"],
        port=SUPABASE["port"],
        sslmode="require"
    )

# ===============================
# MIGRAÇÃO
# ===============================

def migrar_tabela(nome):
    print(f"🔄 Migrando {nome}...")
    src = conectar_local()
    dst = conectar_supabase()

    cur_src = src.cursor()
    cur_dst = dst.cursor()

    cur_src.execute(f"SELECT * FROM {nome}")
    colunas = [desc[0] for desc in cur_src.description]

    for row in cur_src.fetchall():
        valores = [row[c] for c in colunas]

        placeholders = ",".join(["%s"] * len(colunas))
        cols = ",".join(colunas)

        cur_dst.execute(
            f"INSERT INTO {nome} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
            valores
        )

    dst.commit()
    cur_src.close()
    cur_dst.close()
    src.close()
    dst.close()

    print(f"✅ {nome} migrada")

# ===============================
# EXECUÇÃO
# ===============================

if __name__ == "__main__":
    print("🚀 Iniciando migração para Supabase...\n")

    for tabela in [
        "produtos",
        "vendedores",
        "clientes",
        "vendas",
        "itensvenda"
    ]:
        migrar_tabela(tabela)

    print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO")
