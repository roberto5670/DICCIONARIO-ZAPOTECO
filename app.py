import os
import sys
import sqlite3
import unicodedata
import webbrowser
from threading import Timer
from flask import Flask, jsonify, render_template, request

def obtener_ruta_base():
    """Obtiene la ruta base absoluta tanto en desarrollo como en el ejecutable PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Configurar Flask para que encuentre las carpetas de diseño (templates y static) compiladas
ruta_base = obtener_ruta_base()
app = Flask(
    __name__,
    template_folder=os.path.join(ruta_base, 'templates'),
    static_folder=os.path.join(ruta_base, 'static')
)

def obtener_conexion():
    """Conecta a la base de datos en la ruta empaquetada."""
    ruta_db = os.path.join(obtener_ruta_base(), 'diccionario_zapoteco.db')
    conn = sqlite3.connect(ruta_db)
    conn.row_factory = sqlite3.Row
    return conn

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("'", "").replace("’", "").replace("`", "")
    return texto.strip()

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/api/buscar', methods=['GET'])
def buscar():
    busqueda = request.args.get('q', '').strip()
    
    if not busqueda:
        return jsonify([])
    
    busqueda_norm = normalizar_texto(busqueda)
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    sql = '''
        SELECT 
            id, zapoteco, espaniol, categoria, ejemplo_zapoteco, ejemplo_españiol, audio 
        FROM palabras 
        WHERE zapoteco_normalizado LIKE ? 
           OR espaniol_normalizado LIKE ? 
           OR zapoteco LIKE ? 
           OR espaniol LIKE ?
        LIMIT 30
    '''
    param_like = f"%{busqueda_norm}%"
    param_orig = f"%{busqueda}%"
    
    cursor.execute(sql, (param_like, param_like, param_orig, param_orig))
    filas = cursor.fetchall()
    
    resultados = [dict(fila) for fila in filas]
    conn.close()
    
    return jsonify(resultados)

def abrir_navegador():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1.5, abrir_navegador).start()
    app.run(port=5000)