from conexion.conexion import obtener_conexion

class PacienteService:
    @staticmethod
    def listar_todos():
        db = obtener_conexion()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pacientes") # Nombre exacto de tu tabla
            resultado = cursor.fetchall()
            db.close()
            return resultado
        return []

    @staticmethod
    def crear(nombre, apellido, cedula, telefono, email):
        db = obtener_conexion()
        if db:
            cursor = db.cursor()
            # SQL ajustado a tus columnas: nombre, apellido, cedula, telefono, email
            sql = "INSERT INTO pacientes (nombre, apellido, cedula, telefono, email) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, apellido, cedula, telefono, email))
            db.commit()
            db.close()