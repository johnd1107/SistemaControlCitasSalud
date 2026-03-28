from conexion.conexion import obtener_conexion

class HistorialService:
    @staticmethod
    def obtener_por_paciente(id_paciente):
        db = obtener_conexion()
        cursor = db.cursor(dictionary=True)
        # Nombre exacto de tu tabla según la imagen
        sql = "SELECT * FROM historial_clinico WHERE id_paciente = %s"
        cursor.execute(sql, (id_paciente,))
        res = cursor.fetchall()
        db.close()
        return res