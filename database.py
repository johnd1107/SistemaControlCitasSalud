import sqlite3

def init_db():
    conn = sqlite3.connect('clinica.db')
    cursor = conn.cursor()
    # Tabla de Inventario de Insumos Médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada con éxito.")

if __name__ == '__main__':
    init_db()