from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('hotdog.db')

# Rota para a página inicial que exibe as vendas e estoque
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vendas')
    vendas = cursor.fetchall()

    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()

    conn.close()
    return render_template('index.html', vendas=vendas, produtos=produtos)

# Rota para registrar uma nova venda
@app.route('/vender', methods=['POST'])
def vender():
    produto_id = request.form['produto_id']
    quantidade = int(request.form['quantidade'])

    conn = connect_db()
    cursor = conn.cursor()

    # Obter o preço do produto
    cursor.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,))
    produto = cursor.fetchone()

    if produto:
        preco = produto[2]  # preço é o terceiro campo na tabela
        total = preco * quantidade

        # Atualizar a venda
        cursor.execute('INSERT INTO vendas (produto_id, quantidade, total) VALUES (?, ?, ?)',
                       (produto_id, quantidade, total))

        # Atualizar o estoque
        cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, produto_id))

        conn.commit()

    conn.close()
    return redirect(url_for('index'))

# Rota para adicionar um novo produto
@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome = request.form['nome']
    preco = float(request.form['preco'])
    estoque = int(request.form['estoque'])

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Função para inicializar o banco de dados
def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Criar a tabela de produtos
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        preco REAL NOT NULL,
                        estoque INTEGER NOT NULL)''')

    # Criar a tabela de vendas
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_id INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        total REAL NOT NULL,
                        FOREIGN KEY (produto_id) REFERENCES produtos(id))''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados
    app.run(debug=True)
