from conexion.conexion import obtener_conexion

class PacienteService:
    @staticmethod
    def listar_todos():
        db = obtener_conexion()
        cursor = db.cursor(dictionary=True)
        # Ajustado a tus columnas: id_paciente, nombre, apellido, cedula, telefono, email
        cursor.execute("SELECT * FROM pacientes")
        resultado = cursor.fetchall()
        db.close()
        return resultado

    @staticmethod
    def crear(n, a, c, t, e):
        db = obtener_conexion()
        cursor = db.cursor()
        sql = "INSERT INTO pacientes (nombre, apellido, cedula, telefono, email) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (n, a, c, t, e))
        db.commit()
        db.close()