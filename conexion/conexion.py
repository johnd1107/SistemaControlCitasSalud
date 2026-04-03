import sqlite3

def obtener_conexion():
    conn = sqlite3.connect('saludplus.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, cedula TEXT UNIQUE, nombre TEXT, password TEXT, rol TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS pacientes (id_paciente INTEGER PRIMARY KEY AUTOINCREMENT, cedula_p TEXT UNIQUE, nombre_p TEXT, telefono TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS historial (id_h INTEGER PRIMARY KEY AUTOINCREMENT, id_paciente INTEGER, id_medico INTEGER, diagnostico TEXT, receta TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute("INSERT OR IGNORE INTO usuarios (cedula, nombre, password, rol) VALUES ('0000', 'Admin', '123', 'admin')")
    conn.commit()
    conn.close()