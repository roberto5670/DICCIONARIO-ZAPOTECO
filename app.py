from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    dir_proyecto = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(dir_proyecto, 'diccionario_zapoteco.db')
    conn = sqlite3.connect(ruta_db)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta directa a la tabla palabras
    query = '''
        SELECT zapoteco, espaniol, categoria, audio
        FROM palabras
        WHERE zapoteco LIKE ? OR espaniol LIKE ? OR zapoteco_normalizado LIKE ? OR espaniol_normalizado LIKE ?
        LIMIT 50
    '''
    param = f'%{q}%'
    resultados = cursor.execute(query, (param, param, param, param)).fetchall()
    conn.close()

    return jsonify([dict(row) for row in resultados])

if __name__ == '__main__':
    app.run(debug=True)