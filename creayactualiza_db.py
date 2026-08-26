import os
import csv
import shutil
import sqlite3
import unicodedata

def normalizar_texto(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("'", "").replace("’", "").replace("`", "")
    return texto.strip()

def crear_e_importar_base_datos():
    # Carpeta raíz del proyecto en Python
    dir_proyecto = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Ruta del CSV en tu escritorio
    ruta_csv_escritorio = r"C:\Users\herna\Desktop\diccionario\diccionario.csv"
    
    # 2. Ruta destino en la carpeta 'datos' de tu proyecto
    carpeta_datos = os.path.join(dir_proyecto, 'datos')
    os.makedirs(carpeta_datos, exist_ok=True)
    ruta_csv_local = os.path.join(carpeta_datos, 'diccionario.csv')
    
    # 3. Ruta de la Base de Datos
    ruta_db = os.path.join(dir_proyecto, 'diccionario_zapoteco.db')

    # Verificar si existe el archivo exportado por Excel en el Escritorio
    if os.path.exists(ruta_csv_escritorio):
        shutil.copy2(ruta_csv_escritorio, ruta_csv_local)
        print(f"Copiado CSV desde Escritorio a carpeta datos/")
    elif not os.path.exists(ruta_csv_local):
        print(f"Error: No se encontró el CSV en '{ruta_csv_escritorio}' ni en '{ruta_csv_local}'")
        return

    # Conectar a SQLite
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    print("Recreando tablas en la base de datos...")
    cursor.executescript('''
    DROP TABLE IF EXISTS palabras;
    DROP TABLE IF EXISTS palabras_fts;

    CREATE TABLE palabras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zapoteco TEXT NOT NULL,
        zapoteco_normalizado TEXT NOT NULL,
        espaniol TEXT NOT NULL,
        espaniol_normalizado TEXT NOT NULL,
        categoria TEXT,
        audio TEXT
    );

    CREATE VIRTUAL TABLE palabras_fts USING fts5(
        zapoteco,
        zapoteco_normalizado,
        espaniol,
        espaniol_normalizado,
        content='palabras',
        content_rowid='id'
    );
    ''')

    print(f"Procesando datos...")
    registros_insertados = 0

    with open(ruta_csv_local, mode='r', encoding='utf-8-sig', errors='replace') as f:
        linea_muestra = f.readline()
        f.seek(0)
        delimitador = ';' if ';' in linea_muestra else ','

        lector = csv.DictReader(f, delimiter=delimitador)

        for fila in lector:
            zap = str(fila.get('zapoteco', '') or '').strip()
            esp = str(fila.get('español', fila.get('espaniol', '')) or '').strip()
            cat = str(fila.get('categoria', '') or '').strip()
            aud = str(fila.get('audio', '') or '').strip()

            if not zap and not esp:
                continue

            zap_norm = normalizar_texto(zap)
            esp_norm = normalizar_texto(esp)

            cursor.execute('''
                INSERT INTO palabras (
                    zapoteco, zapoteco_normalizado, 
                    espaniol, espaniol_normalizado, 
                    categoria, audio
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (zap, zap_norm, esp, esp_norm, cat, aud))

            registros_insertados += 1

    cursor.execute('''
        INSERT INTO palabras_fts(rowid, zapoteco, zapoteco_normalizado, espaniol, espaniol_normalizado)
        SELECT id, zapoteco, zapoteco_normalizado, espaniol, espaniol_normalizado FROM palabras;
    ''')

    conn.commit()
    conn.close()

    print(f"¡Éxito! Se importaron {registros_insertados} palabras a '{ruta_db}'.")

if __name__ == '__main__':
    crear_e_importar_base_datos()