import psycopg2
import psycopg2.extras
import json
from datetime import datetime

# ================= CONFIGURAÇÃO =================
DB_CONFIG = {
    "host": "aws-1-sa-east-1.pooler.supabase.com",
    "database": "postgres",
    "user": "postgres.dfcmibsztfmzvtheaeoh",
    "password": "sBASE2026!data",
    "port": 5432
}

print(">>> DB_CONFIG EM USO:", DB_CONFIG)

# ================= CONEXÃO =================
def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        sslmode="require"
    )

# ================= INIT DB =================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        codigobarras TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        marca TEXT,
        linha TEXT,
        tipo TEXT,
        preco NUMERIC(10,2) NOT NULL,
        estoque INTEGER NOT NULL,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendedores (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        telefone TEXT,
        cpf TEXT UNIQUE NOT NULL,
        ativo BOOLEAN DEFAULT TRUE,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        whatsapp TEXT,
        cpf TEXT UNIQUE NOT NULL,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id TEXT PRIMARY KEY,
        data TIMESTAMP NOT NULL,
        itensjson JSONB NOT NULL,
        subtotal NUMERIC(10,2) NOT NULL,
        descontopercentual NUMERIC(5,2) DEFAULT 0,
        total NUMERIC(10,2) NOT NULL,
        metodopagamento TEXT NOT NULL,
        vendedor_id INTEGER REFERENCES vendedores(id),
        cliente_id INTEGER REFERENCES clientes(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS itensvenda (
        id SERIAL PRIMARY KEY,
        vendaid TEXT REFERENCES vendas(id),
        produtoid INTEGER REFERENCES produtos(id),
        nomeproduto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        precounitario NUMERIC(10,2) NOT NULL,
        subtotal NUMERIC(10,2) NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================= PRODUTOS =================
def criar_produto(codigobarras, nome, marca, linha, tipo, preco, estoque):
    conn = get_connection()
    cur = conn.cursor()
    try:
        codigobarras = codigobarras.strip().upper()

        cur.execute("""
            INSERT INTO produtos
            (codigobarras, nome, marca, linha, tipo, preco, estoque)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (codigobarras, nome, marca, linha, tipo, preco, estoque))

        pid = cur.fetchone()[0]
        conn.commit()
        return pid

    except Exception as e:
        conn.rollback()
        print("❌ ERRO REAL AO CRIAR PRODUTO:", e)
        raise  # <-- MUITO IMPORTANTE

    finally:
        cur.close()
        conn.close()


def listar_produtos(nome=None, marca=None, linha=None, tipo=None, codigo=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if nome:
        query += " AND nome ILIKE %s"
        params.append(f"%{nome}%")
    if marca:
        query += " AND marca ILIKE %s"
        params.append(f"%{marca}%")
    if linha:
        query += " AND linha ILIKE %s"
        params.append(f"%{linha}%")
    if tipo:
        query += " AND tipo ILIKE %s"
        params.append(f"%{tipo}%")
    if codigo:
        query += " AND codigobarras = %s"
        params.append(codigo)

    query += " ORDER BY nome"
    cur.execute(query, params)
    dados = cur.fetchall()

    cur.close()
    conn.close()
    return dados

def buscar_produto_por_codigo(codigo):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM produtos WHERE codigobarras = %s", (codigo,))
    dado = cur.fetchone()
    cur.close()
    conn.close()
    return dado

def atualizar_produto_completo(id, dados):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE produtos SET
        codigobarras=%s, nome=%s, marca=%s, linha=%s,
        tipo=%s, preco=%s, estoque=%s,
        atualizadoem=CURRENT_TIMESTAMP
        WHERE id=%s
    """, (
        dados["codigobarras"], dados["nome"], dados["marca"],
        dados["linha"], dados["tipo"], dados["preco"],
        dados["estoque"], id
    ))
    conn.commit()
    cur.close()
    conn.close()
    return True

def deletar_produto(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ================= VENDEDORES =================
def criar_vendedor(nome, telefone, cpf):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO vendedores (nome, telefone, cpf)
            VALUES (%s,%s,%s)
            RETURNING id
        """, (nome, telefone, cpf))
        conn.commit()
        return cur.fetchone()[0]
    except:
        return None
    finally:
        cur.close()
        conn.close()

def listar_vendedores():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM vendedores WHERE ativo = TRUE ORDER BY nome")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados

def deletar_vendedor(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE vendedores SET ativo = FALSE WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ================= CLIENTES =================
def criar_cliente(nome, whatsapp, cpf):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO clientes (nome, whatsapp, cpf)
            VALUES (%s,%s,%s)
            RETURNING id
        """, (nome, whatsapp, cpf))
        conn.commit()
        return cur.fetchone()[0]
    except:
        return None
    finally:
        cur.close()
        conn.close()

def listar_clientes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clientes ORDER BY nome")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados

def buscar_cliente_por_cpf(cpf):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE cpf = %s", (cpf,))
    dado = cur.fetchone()
    cur.close()
    conn.close()
    return dado

def deletar_cliente(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ================= VENDAS =================
def criar_venda(idvenda, itens, subtotal, descontopercentual, total, metodopagamento, vendedor_id=None, cliente_id=None):
    conn = get_connection()
    cur = conn.cursor()
    data = datetime.now()
    itensjson = json.dumps(itens)

    try:
        cur.execute("""
            INSERT INTO vendas
            (id, data, itensjson, subtotal, descontopercentual, total, metodopagamento, vendedor_id, cliente_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (idvenda, data, itensjson, subtotal, descontopercentual, total, metodopagamento, vendedor_id, cliente_id))

        for item in itens:
            cur.execute("""
                INSERT INTO itensvenda
                (vendaid, produtoid, nomeproduto, quantidade, precounitario, subtotal)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                idvenda, item["id"], item["nome"], item["quantidade"],
                item["preco"], item["preco"] * item["quantidade"]
            ))

            cur.execute(
                "UPDATE produtos SET estoque = estoque - %s WHERE id = %s",
                (item["quantidade"], item["id"])
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Erro ao criar venda:", e)
        return False
    finally:
        cur.close()
        conn.close()
