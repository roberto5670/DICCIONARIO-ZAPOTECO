from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import unicodedata

app = Flask(__name__)

def normalizar_texto(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("'", "").replace("’", "").replace("`", "")
    return texto.strip()

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

    q_norm = normalizar_texto(q)
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT zapoteco, espaniol, categoria, audio
        FROM palabras
        WHERE zapoteco_normalizado LIKE ? 
           OR espaniol_normalizado LIKE ?
           OR zapoteco LIKE ?
           OR espaniol LIKE ?
        LIMIT 50
    '''
    param = f'%{q_norm}%'
    param_raw = f'%{q}%'
    
    try:
        resultados = cursor.execute(query, (param, param, param_raw, param_raw)).fetchall()
        conn.close()

        data = []
        for row in resultados:
            item = dict(row)
            # Garantizar compatibilidad con el JS del HTML
            item['español'] = item.get('espaniol', '')
            data.append(item)

        return jsonify(data)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)