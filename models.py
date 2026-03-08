import sqlite3


class Inventario:

    def __init__(self):

        self.db = "clinica.db"

        self.crear_tabla()


    def conectar(self):

        return sqlite3.connect(self.db)


    def crear_tabla(self):

        conn = self.conectar()

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            cantidad INTEGER,
            precio REAL
        )
        """)

        conn.commit()

        conn.close()


    def añadir(self, nombre, categoria, cantidad, precio):

        conn = self.conectar()

        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO productos (nombre,categoria,cantidad,precio) VALUES (?,?,?,?)",
        (nombre,categoria,cantidad,precio)
        )

        conn.commit()

        conn.close()


    def obtener_todo(self):

        conn = self.conectar()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM productos")

        filas = cursor.fetchall()

        conn.close()

        inventario = {}

        for f in filas:

            inventario[f[0]] = {
                "nombre":f[1],
                "categoria":f[2],
                "cantidad":f[3],
                "precio":f[4]
            }

        return inventario


    def eliminar(self,id):

        conn = self.conectar()

        cursor = conn.cursor()

        cursor.execute("DELETE FROM productos WHERE id=?",(id,))

        conn.commit()

        conn.close()