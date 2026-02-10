#!/usr/bin/env python3
"""
StockMaster - Inicializador do Sistema
Cria a estrutura de pastas e inicializa o banco de dados
"""

import os
import sys
from pathlib import Path

def criar_estrutura():
    """Cria a estrutura de pastas necessária"""
    
    print("🚀 Inicializando StockMaster...\n")
    
    # Criar pasta templates
    templates_dir = Path("templates")
    if not templates_dir.exists():
        templates_dir.mkdir()
        print(f"✓ Pasta '{templates_dir}' criada")
    else:
        print(f"✓ Pasta '{templates_dir}' já existe")
    
    # Verificar se index.html existe
    index_path = templates_dir / "index.html"
    if not index_path.exists():
        print(f"⚠️  Arquivo 'templates/index.html' não encontrado!")
        print("   Certifique-se de colocar o arquivo HTML na pasta templates/")
    else:
        print(f"✓ Arquivo 'templates/index.html' encontrado")
    
    # Verificar se app.py existe
    if not Path("app.py").exists():
        print(f"⚠️  Arquivo 'app.py' não encontrado!")
        sys.exit(1)
    else:
        print(f"✓ Arquivo 'app.py' encontrado")
    
    # Verificar se database.py existe
    if not Path("database.py").exists():
        print(f"⚠️  Arquivo 'database.py' não encontrado!")
        sys.exit(1)
    else:
        print(f"✓ Arquivo 'database.py' encontrado")
    
    print("\n✅ Estrutura de pastas pronta!\n")

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    
    print("📦 Verificando dependências...\n")
    
    dependencias = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'reportlab': 'ReportLab',
    }
    
    faltando = []
    
    for modulo, nome in dependencias.items():
        try:
            __import__(modulo)
            print(f"✓ {nome}")
        except ImportError:
            print(f"✗ {nome} (NÃO INSTALADO)")
            faltando.append(nome)
    
    if faltando:
        print(f"\n⚠️  Dependências faltando: {', '.join(faltando)}")
        print("\nInstale com:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    else:
        print(f"\n✅ Todas as dependências estão instaladas!\n")

if __name__ == "__main__":
    criar_estrutura()
    verificar_dependencias()
    
    print("=" * 50)
    print("🎉 Sistema pronto para iniciar!")
    print("=" * 50)
    print("\nPara iniciar o servidor, execute:\n")
    print("  python app.py")
    print("\nDados salvos em: stockmaster.db")
    print("Acesse em: http://localhost:5000")
    print("\n" + "=" * 50)
