#!/usr/bin/env python3
"""
Script para popular o banco com dados de exemplo
Execute: python populate.py
"""

import sys
from database import init_db, criar_produto

def main():
    print("🔧 Inicializando banco de dados...")
    init_db()
    print("✓ Banco de dados inicializado\n")
    
    print("📦 Adicionando produtos de exemplo...\n")
    
    produtos_exemplo = [
        {
            'codigo_barras': '7891234567890',
            'nome': 'Coca-Cola 350ml',
            'marca': 'Coca-Cola',
            'linha': 'Refrigerantes',
            'tipo': 'Bebida',
            'preco': 5.50,
            'estoque': 50
        },
        {
            'codigo_barras': '7891234567891',
            'nome': 'Suco Natural 1L',
            'marca': 'Suco Integral',
            'linha': 'Bebidas',
            'tipo': 'Bebida',
            'preco': 8.90,
            'estoque': 30
        },
        {
            'codigo_barras': '7891234567892',
            'nome': 'Batata Ruffles Original 60g',
            'marca': 'Ruffles',
            'linha': 'Salgadinhos',
            'tipo': 'Alimento',
            'preco': 3.50,
            'estoque': 80
        },
        {
            'codigo_barras': '7891234567893',
            'nome': 'Chocolate Ao Leite 200g',
            'marca': 'Nestlé',
            'linha': 'Chocolates',
            'tipo': 'Doce',
            'preco': 7.90,
            'estoque': 40
        },
        {
            'codigo_barras': '7891234567894',
            'nome': 'Água Mineral 500ml',
            'marca': 'Crystal',
            'linha': 'Bebidas',
            'tipo': 'Bebida',
            'preco': 2.50,
            'estoque': 100
        },
        {
            'codigo_barras': '7891234567895',
            'nome': 'Saboneteira Dove',
            'marca': 'Dove',
            'linha': 'Higiene',
            'tipo': 'Higiene',
            'preco': 4.50,
            'estoque': 25
        },
        {
            'codigo_barras': '7891234567896',
            'nome': 'Detergente Neutro 500ml',
            'marca': 'Neutro',
            'linha': 'Limpeza',
            'tipo': 'Limpeza',
            'preco': 3.20,
            'estoque': 60
        },
        {
            'codigo_barras': '7891234567897',
            'nome': 'Café Premium 500g',
            'marca': 'Pilao',
            'linha': 'Bebidas',
            'tipo': 'Alimento',
            'preco': 12.90,
            'estoque': 20
        },
        {
            'codigo_barras': '7891234567898',
            'nome': 'Pão de Queijo 400g',
            'marca': 'Bimbo',
            'linha': 'Padaria',
            'tipo': 'Alimento',
            'preco': 6.80,
            'estoque': 35
        },
        {
            'codigo_barras': '7891234567899',
            'nome': 'Iogurte Natural 500ml',
            'marca': 'Integral',
            'linha': 'Laticínios',
            'tipo': 'Alimento',
            'preco': 9.50,
            'estoque': 28
        }
    ]
    
    contador = 0
    for produto in produtos_exemplo:
        try:
            id_novo = criar_produto(
                produto['codigo_barras'],
                produto['nome'],
                produto['marca'],
                produto['linha'],
                produto['tipo'],
                produto['preco'],
                produto['estoque']
            )
            
            if id_novo:
                contador += 1
                print(f"✓ {produto['nome']} (ID: {id_novo})")
            else:
                print(f"✗ {produto['nome']} (Código de barras duplicado)")
        except Exception as e:
            print(f"✗ {produto['nome']} - Erro: {e}")
    
    print(f"\n✅ {contador} produtos adicionados com sucesso!")
    print("\nPróximas etapas:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://localhost:5000")
    print("3. Você verá os produtos na página de 'Produtos'")
    print("4. Use os códigos de barras para fazer vendas na 'Caixa'")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
