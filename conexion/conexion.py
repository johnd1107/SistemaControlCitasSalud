import sqlite3

def obtener_conexion():
    conn = sqlite3.connect('sistema_salud.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    db = obtener_conexion()
    # Usuarios: Admin, Médico, Paciente
    db.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        especialidad TEXT,
        edad INTEGER,
        domicilio TEXT
    )""")
    # Citas
    db.execute("""CREATE TABLE IF NOT EXISTS citas (
        id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        id_medico INTEGER NOT NULL,
        especialidad TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente'
    )""")
    # Historial Clínico (Consultas)
    db.execute("""CREATE TABLE IF NOT EXISTS consultas (
        id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cita INTEGER NOT NULL,
        diagnostico TEXT,
        receta TEXT,
        fecha_atencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(id_cita) REFERENCES citas(id_cita)
    )""")
    db.commit()
    db.close()