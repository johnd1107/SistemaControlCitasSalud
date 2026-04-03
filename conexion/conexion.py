import sqlite3
from sqlite3 import Error
import os


def obtener_conexion():
    """Establece la conexión con la base de datos SQLite."""
    try:
        # Crea la carpeta 'database' si no existe para mayor orden
        if not os.path.exists('database'):
            os.makedirs('database')

        # La base de datos se guardará en database/sistema_salud.db
        db_path = os.path.join('database', 'sistema_salud.db')

        conn = sqlite3.connect(db_path)
        # Esto permite acceder a las columnas por nombre: fila['nombre']
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def inicializar_db():
    """Crea las tablas necesarias y actualiza la estructura si es necesario."""
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()

        # 1. Tabla de Usuarios (Médicos y Admin)
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

        # 2. Tabla de Pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_p TEXT UNIQUE NOT NULL,
                nombre_p TEXT NOT NULL,
                telefono TEXT
            )
        ''')

        # 3. Tabla de Historial Clínico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                id_paciente INTEGER,
                id_medico INTEGER,
                diagnostico TEXT,
                receta TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente),
                FOREIGN KEY (id_medico) REFERENCES usuarios (id_usuario)
            )
        ''')

        # --- FUNCIÓN PROFESIONAL: ACTUALIZAR TABLA SI FALTA COLUMNA ---
        try:
            # Intentamos agregar la columna especialidad por si la DB es vieja
            cursor.execute("ALTER TABLE usuarios ADD COLUMN especialidad TEXT")
            print("Columna 'especialidad' añadida con éxito.")
        except sqlite3.OperationalError:
            # Si da error es porque la columna ya existe, lo cual está bien
            pass

        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")


# Al ejecutar este script directamente, se crea la base de datos
if __name__ == '__main__':
    inicializar_db()