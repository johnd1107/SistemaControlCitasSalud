import sqlite3

def obtener_conexion():
    conn = sqlite3.connect('salud_plus.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    # Usuarios: Admin, Médicos y Pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            especialidad TEXT
        )
    ''')
    # Citas: Conecta Paciente con Médico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER,
            id_medico INTEGER,
            especialidad TEXT,
            fecha TEXT,
            hora TEXT,
            estado TEXT DEFAULT 'Pendiente',
            FOREIGN KEY(id_paciente) REFERENCES usuarios(id_usuario),
            FOREIGN KEY(id_medico) REFERENCES usuarios(id_usuario)
        )
    ''')
    conn.commit()
    conn.close()