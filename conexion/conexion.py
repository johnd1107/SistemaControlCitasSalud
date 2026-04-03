import sqlite3

def obtener_conexion():
    conexion = sqlite3.connect('sistema_salud.db')
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_db():
    db = obtener_conexion()
    # Tabla de Usuarios
    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE,
            nombre TEXT,
            password TEXT,
            rol TEXT
        )
    """)
    # Tabla de Pacientes
    db.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula_p TEXT UNIQUE,
            nombre_p TEXT,
            telefono TEXT
        )
    """)
    # Tabla de Historial
    db.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id_h INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER,
            id_medico INTEGER,
            diagnostico TEXT,
            receta TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()