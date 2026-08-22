import os
import sqlite3
import unicodedata
import pandas as pd

def normalizar_texto(texto):
    """
    Convierte a minúsculas, remueve acentos y apóstrofes (saltillos)
    para permitir búsquedas más sencillas y flexibles.
    """
    if not isinstance(texto, str) or not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("'", "").replace("’", "").replace("`", "")
    return texto.strip()

def crear_e_importar_base_datos():
    # 1. Definir ruta del archivo CSV
    ruta_csv = os.path.join('datos', 'diccionario.csv')
    ruta_db = 'diccionario_zapoteco.db'

    # Verificar si el archivo CSV existe
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontró el archivo '{ruta_csv}'. Asegúrate de que esté en 'datos/diccionario.csv'.")
        return

    # 2. Conectar/Crear la base de datos SQLite
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # 3. Crear las tablas con soporte para audio
    print("Creando tablas en SQLite...")
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
        ejemplo_zapoteco TEXT,
        ejemplo_españiol TEXT,
        audio TEXT
    );

    -- Tabla FTS5 para búsquedas de texto completo
    CREATE VIRTUAL TABLE palabras_fts USING fts5(
        zapoteco,
        zapoteco_normalizado,
        espaniol,
        espaniol_normalizado,
        ejemplo_zapoteco,
        ejemplo_españiol,
        content='palabras',
        content_rowid='id'
    );
    ''')

    # 4. Leer el archivo CSV
    print(f"Leyendo datos desde {ruta_csv}...")
    try:
        df = pd.read_csv(ruta_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(ruta_csv, encoding='latin-1')

    df = df.fillna('') # Reemplazar vacíos con texto en blanco

    # 5. Insertar registros en la base de datos
    registros_insertados = 0
    for _, fila in df.iterrows():
        zap = str(fila.get('zapoteco', '')).strip()
        esp = str(fila.get('espaniol', '')).strip()
        cat = str(fila.get('categoria', '')).strip()
        ej_zap = str(fila.get('ejemplo_zapoteco', '')).strip()
        ej_esp = str(fila.get('ejemplo_españiol', '')).strip()
        aud = str(fila.get('audio', '')).strip()

        # Si no hay palabra en zapoteco ni en español, ignorar la fila
        if not zap and not esp:
            continue

        zap_norm = normalizar_texto(zap)
        esp_norm = normalizar_texto(esp)

        cursor.execute('''
            INSERT INTO palabras (
                zapoteco, zapoteco_normalizado, 
                espaniol, espaniol_normalizado, 
                categoria, ejemplo_zapoteco, ejemplo_españiol, audio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (zap, zap_norm, esp, esp_norm, cat, ej_zap, ej_esp, aud))
        
        registros_insertados += 1

    # Sincronizar la tabla de búsqueda rápida FTS5
    cursor.execute('''
        INSERT INTO palabras_fts(rowid, zapoteco, zapoteco_normalizado, espaniol, espaniol_normalizado, ejemplo_zapoteco, ejemplo_españiol)
        SELECT id, zapoteco, zapoteco_normalizado, espaniol, espaniol_normalizado, ejemplo_zapoteco, ejemplo_españiol FROM palabras;
    ''')

    conn.commit()
    conn.close()

    print(f"¡Éxito! Se han importado {registros_insertados} palabras a '{ruta_db}'.")

if __name__ == '__main__':
    crear_e_importar_base_datos()