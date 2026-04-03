import sqlite3


def obtener_conexion():
    conn = sqlite3.connect('sistema_salud.db')
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    db = obtener_conexion()
    # Tabla de Usuarios completa
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

    # Tabla de Citas con relación al médico
    db.execute("""CREATE TABLE IF NOT EXISTS citas (
        id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        id_medico INTEGER NOT NULL,
        especialidad TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente',
        FOREIGN KEY(id_paciente) REFERENCES usuarios(id_usuario),
        FOREIGN KEY(id_medico) REFERENCES usuarios(id_usuario)
    )""")

    # Tabla de Historial para diagnósticos y recetas
    db.execute("""CREATE TABLE IF NOT EXISTS historial (
        id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        id_medico INTEGER NOT NULL,
        fecha_atencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        diagnostico TEXT,
        receta TEXT,
        FOREIGN KEY(id_paciente) REFERENCES usuarios(id_usuario)
    )""")
    db.commit()
    db.close()