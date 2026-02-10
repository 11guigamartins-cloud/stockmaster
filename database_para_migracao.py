import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / 'stockmaster.db'

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Produtos
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigobarras TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        marca TEXT,
        linha TEXT,
        tipo TEXT,
        preco REAL NOT NULL,
        estoque INTEGER NOT NULL,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de Vendedores
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        cpf TEXT UNIQUE NOT NULL,
        ativo INTEGER DEFAULT 1,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de Clientes (NOVA)
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        whatsapp TEXT,
        cpf TEXT UNIQUE NOT NULL,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de Vendas
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
        id TEXT PRIMARY KEY,
        data TIMESTAMP NOT NULL,
        itensjson TEXT NOT NULL,
        subtotal REAL NOT NULL,
        descontopercentual REAL DEFAULT 0,
        total REAL NOT NULL,
        metodopagamento TEXT NOT NULL,
        vendedor_id INTEGER,
        cliente_id INTEGER,
        criadoem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(vendedor_id) REFERENCES vendedores(id),
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')
    
    # Migração segura para adicionar coluna cliente_id se não existir
    try:
        cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_id INTEGER REFERENCES clientes(id)")
    except sqlite3.OperationalError:
        pass # Coluna já existe
    
    # Tabela de Itens de Venda
    cursor.execute('''CREATE TABLE IF NOT EXISTS itensvenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendaid TEXT NOT NULL,
        produtoid INTEGER NOT NULL,
        nomeproduto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        precounitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY(vendaid) REFERENCES vendas(id),
        FOREIGN KEY(produtoid) REFERENCES produtos(id)
    )''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== FUNÇÕES DE PRODUTOS ====================

def criar_produto(codigobarras, nome, marca, linha, tipo, preco, estoque):
    """Cria um novo produto"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO produtos (codigobarras, nome, marca, linha, tipo, preco, estoque)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (codigobarras, nome, marca, linha, tipo, preco, estoque))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def listar_produtos(nome=None, marca=None, linha=None, tipo=None, codigo=None):
    """Lista produtos com filtros opcionais"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM produtos WHERE 1=1'
    params = []
    
    if nome:
        query += ' AND nome LIKE ?'
        params.append(f'%{nome}%')
    if marca:
        query += ' AND marca LIKE ?'
        params.append(f'%{marca}%')
    if linha:
        query += ' AND linha LIKE ?'
        params.append(f'%{linha}%')
    if tipo:
        query += ' AND tipo LIKE ?'
        params.append(f'%{tipo}%')
    if codigo:
        query += ' AND codigobarras = ?'
        params.append(codigo)
        
    query += ' ORDER BY nome'
    cursor.execute(query, params)
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def buscar_produto_por_codigo(codigo):
    """Busca produto comparando no Python (Infalível)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM produtos')
    todos_produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    codigo_buscado = str(codigo).strip().upper()
    
    for produto in todos_produtos:
        codigo_no_banco = str(produto['codigobarras']).strip().upper()
        if codigo_buscado == codigo_no_banco:
            return produto
            
    return None

def atualizar_produto_completo(id, dados):
    """Atualiza todos os campos de um produto"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE produtos SET 
            codigobarras = ?, nome = ?, marca = ?, linha = ?, 
            tipo = ?, preco = ?, estoque = ?, atualizadoem = CURRENT_TIMESTAMP 
            WHERE id = ?''',
            (dados['codigobarras'], dados['nome'], dados['marca'], 
             dados['linha'], dados['tipo'], dados['preco'], dados['estoque'], id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao editar: {e}")
        return False
    finally:
        conn.close()

def deletar_produto(id):
    """Deleta um produto"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return True

# ==================== FUNÇÕES DE VENDEDORES ====================

def criar_vendedor(nome, telefone, cpf):
    """Cria um novo vendedor"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO vendedores (nome, telefone, cpf)
                        VALUES (?, ?, ?)''',
                      (nome, telefone, cpf))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def listar_vendedores():
    """Lista todos os vendedores ativos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vendedores WHERE ativo = 1 ORDER BY nome')
    vendedores = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return vendedores

def deletar_vendedor(id):
    """Deleta (soft delete) um vendedor"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE vendedores SET ativo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return True

# ==================== FUNÇÕES DE CLIENTES (NOVO) ====================

def criar_cliente(nome, whatsapp, cpf):
    """Cria um novo cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO clientes (nome, whatsapp, cpf)
                        VALUES (?, ?, ?)''',
                      (nome, whatsapp, cpf))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def listar_clientes():
    """Lista todos os clientes"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY nome')
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes

def buscar_cliente_por_cpf(cpf):
    """Busca cliente pelo CPF"""
    conn = get_connection()
    cursor = conn.cursor()
    # Remove pontos e traços para busca flexível, se desejar, mas aqui faremos busca exata no que foi salvo
    cursor.execute('SELECT * FROM clientes WHERE cpf = ?', (cpf,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return dict(resultado)
    return None

def deletar_cliente(id):
    """Deleta um cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return True

# ==================== FUNÇÕES DE VENDAS ====================

def criar_venda(idvenda, itens, subtotal, descontopercentual, total, metodopagamento, vendedor_id=None, cliente_id=None):
    """Cria uma nova venda"""
    conn = get_connection()
    cursor = conn.cursor()
    data = datetime.now().isoformat()
    itensjson = json.dumps(itens)
    
    try:
        cursor.execute('''INSERT INTO vendas (id, data, itensjson, subtotal, descontopercentual, total, metodopagamento, vendedor_id, cliente_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (idvenda, data, itensjson, subtotal, descontopercentual, total, metodopagamento, vendedor_id, cliente_id))
        
        # Inserir itens e atualizar estoque
        for item in itens:
            cursor.execute('''INSERT INTO itensvenda (vendaid, produtoid, nomeproduto, quantidade, precounitario, subtotal)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                          (idvenda, item['id'], item['nome'], item['quantidade'], item['preco'], 
                           item['preco'] * item['quantidade']))
            
            # Atualizar estoque
            cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?',
                          (item['quantidade'], item['id']))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f'Erro ao criar venda: {e}')
        return False
    finally:
        conn.close()

def listar_vendas(data_inicio=None, data_fim=None, vendedor_id=None, produto=None):
    """Lista vendas com filtros opcionais"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT v.*, vd.nome as vendedor_nome, c.nome as cliente_nome
               FROM vendas v
               LEFT JOIN vendedores vd ON v.vendedor_id = vd.id
               LEFT JOIN clientes c ON v.cliente_id = c.id
               WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(v.data) >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND DATE(v.data) <= ?'
        params.append(data_fim)
    
    if vendedor_id:
        query += ' AND v.vendedor_id = ?'
        params.append(int(vendedor_id))
    
    query += ' ORDER BY v.data DESC'
    cursor.execute(query, params)
    
    vendas = []
    for row in cursor.fetchall():
        venda = dict(row)
        venda['itens'] = json.loads(venda['itensjson'])
        
        # Filtro por produto se fornecido
        if produto:
            venda['itens'] = [item for item in venda['itens'] 
                            if produto.lower() in item['nome'].lower()]
            if not venda['itens']:
                continue
        
        vendas.append(venda)
    
    conn.close()
    return vendas

def buscar_venda(idvenda):
    """Busca uma venda específica"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT v.*, vd.nome as vendedor_nome, c.nome as cliente_nome
                     FROM vendas v
                     LEFT JOIN vendedores vd ON v.vendedor_id = vd.id
                     LEFT JOIN clientes c ON v.cliente_id = c.id
                     WHERE v.id = ?''', (idvenda,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        venda = dict(resultado)
        venda['itens'] = json.loads(venda['itensjson'])
        return venda
    return None

# ==================== FUNÇÕES DE DASHBOARD ====================

def obter_estatisticas(data_inicio=None, data_fim=None, vendedor_id=None):
    """Obtém estatísticas do dashboard"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT SUM(total) as total FROM vendas WHERE 1=1'
    params = []
    
    if data_inicio:
        query += ' AND DATE(data) >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND DATE(data) <= ?'
        params.append(data_fim)
    
    if vendedor_id:
        query += ' AND vendedor_id = ?'
        params.append(int(vendedor_id))
    
    cursor.execute(query, params)
    totalreceita = cursor.fetchone()[0] or 0
    
    query2 = 'SELECT COUNT(*) as total FROM vendas WHERE 1=1'
    params2 = []
    
    if data_inicio:
        query2 += ' AND DATE(data) >= ?'
        params2.append(data_inicio)
    
    if data_fim:
        query2 += ' AND DATE(data) <= ?'
        params2.append(data_fim)
    
    if vendedor_id:
        query2 += ' AND vendedor_id = ?'
        params2.append(int(vendedor_id))
    
    cursor.execute(query2, params2)
    totalvendas = cursor.fetchone()[0]
    
    query3 = 'SELECT SUM(quantidade) as total FROM itensvenda WHERE vendaid IN (SELECT id FROM vendas WHERE 1=1'
    params3 = []
    
    if data_inicio:
        query3 += ' AND DATE(data) >= ?'
        params3.append(data_inicio)
    
    if data_fim:
        query3 += ' AND DATE(data) <= ?'
        params3.append(data_fim)
    
    if vendedor_id:
        query3 += ' AND vendedor_id = ?'
        params3.append(int(vendedor_id))
    
    query3 += ')'
    cursor.execute(query3, params3)
    totalitens = cursor.fetchone()[0] or 0
    
    ticketmedio = totalreceita / totalvendas if totalvendas > 0 else 0
    
    conn.close()
    
    return {
        'totalreceita': round(totalreceita, 2),
        'totalvendas': totalvendas,
        'totalitens': totalitens,
        'ticketmedio': round(ticketmedio, 2)
    }

def obter_vendas_14dias(data_inicio=None, data_fim=None, vendedor_id=None):
    """Obtém vendas dos últimos 14 dias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT DATE(data) as data, SUM(total) as total FROM vendas WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(data) >= ?'
        params.append(data_inicio)
    else:
        query += ' AND DATE(data) >= DATE("now", "-14 days")'
    
    if data_fim:
        query += ' AND DATE(data) <= ?'
        params.append(data_fim)
    
    if vendedor_id:
        query += ' AND vendedor_id = ?'
        params.append(int(vendedor_id))
    
    query += ' GROUP BY DATE(data) ORDER BY data'
    
    cursor.execute(query, params)
    vendas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return vendas

def obter_top_produtos(limite=10, data_inicio=None, data_fim=None, vendedor_id=None):
    """Obtém os top produtos vendidos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT nomeproduto, SUM(quantidade) as totalvendido FROM itensvenda 
               WHERE vendaid IN (SELECT id FROM vendas WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(data) >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND DATE(data) <= ?'
        params.append(data_fim)
    
    if vendedor_id:
        query += ' AND vendedor_id = ?'
        params.append(int(vendedor_id))
    
    query += ''') GROUP BY nomeproduto ORDER BY totalvendido DESC LIMIT ?'''
    params.append(limite)
    
    cursor.execute(query, params)
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def obter_ranking_vendedores_valor(limite=10, data_inicio=None, data_fim=None):
    """Ranking de vendedores por valor de venda"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT COALESCE(vd.nome, 'Sem Vendedor') as vendedor_nome, SUM(v.total) as total FROM vendas v
               LEFT JOIN vendedores vd ON v.vendedor_id = vd.id
               WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(v.data) >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND DATE(v.data) <= ?'
        params.append(data_fim)
    
    query += ' GROUP BY v.vendedor_id ORDER BY total DESC LIMIT ?'
    params.append(limite)
    
    cursor.execute(query, params)
    ranking = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return ranking

def obter_ranking_vendedores_itens(limite=10, data_inicio=None, data_fim=None):
    """Ranking de vendedores por quantidade de itens"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT COALESCE(vd.nome, 'Sem Vendedor') as vendedor_nome, SUM(iv.quantidade) as total_itens 
               FROM itensvenda iv
               JOIN vendas v ON iv.vendaid = v.id
               LEFT JOIN vendedores vd ON v.vendedor_id = vd.id
               WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(v.data) >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND DATE(v.data) <= ?'
        params.append(data_fim)
    
    query += ' GROUP BY v.vendedor_id ORDER BY total_itens DESC LIMIT ?'
    params.append(limite)
    
    cursor.execute(query, params)
    ranking = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return ranking

def obter_vendas_vendedor_dia(data_inicio=None, data_fim=None):
    """Obtém vendas por vendedor por dia"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''SELECT DATE(v.data) as data, COALESCE(vd.nome, 'Sem Vendedor') as vendedor_nome, SUM(v.total) as total
               FROM vendas v
               LEFT JOIN vendedores vd ON v.vendedor_id = vd.id
               WHERE 1=1'''
    params = []
    
    if data_inicio:
        query += ' AND DATE(v.data) >= ?'
        params.append(data_inicio)
    else:
        query += ' AND DATE(v.data) >= DATE("now", "-14 days")'
    
    if data_fim:
        query += ' AND DATE(v.data) <= ?'
        params.append(data_fim)
    
    query += ' GROUP BY DATE(v.data), v.vendedor_id ORDER BY v.data, vendedor_nome'
    
    cursor.execute(query, params)
    dados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dados