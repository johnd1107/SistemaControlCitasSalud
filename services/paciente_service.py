from conexion.conexion import obtener_conexion

class PacienteService:
    @staticmethod
    def listar_todos():
        db = obtener_conexion()
        if db is None: return []
        cursor = db.cursor(dictionary=True)
        # Usamos nombres en español como en tu DB
        cursor.execute("SELECT id_paciente, nombre, apellido, cedula FROM pacientes")
        res = cursor.fetchall()
        db.close()
        return res

    @staticmethod
    def obtener_por_id(id_p):
        db = obtener_conexion()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes WHERE id_paciente = %s", (id_p,))
        res = cursor.fetchone()
        db.close()
        return res

    @staticmethod
    def guardar(n, a, c, t, e, id_p=None):
        db = obtener_conexion()
        cursor = db.cursor()
        if id_p:
            sql = "UPDATE pacientes SET nombre=%s, apellido=%s, cedula=%s, telefono=%s, email=%s WHERE id_paciente=%s"
            cursor.execute(sql, (n, a, c, t, e, id_p))
        else:
            sql = "INSERT INTO pacientes (nombre, apellido, cedula, telefono, email) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (n, a, c, t, e))
        db.commit()
        db.close()