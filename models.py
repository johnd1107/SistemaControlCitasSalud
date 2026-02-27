import sqlite3


class Producto:
    def __init__(self, id, nombre, categoria, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio
        }


class Inventario:
    def __init__(self):
        self.db_name = 'clinica.db'
        self._crear_tabla()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def _crear_tabla(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def añadir(self, nombre, categoria, cantidad, precio):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO productos (nombre, categoria, cantidad, precio) VALUES (?, ?, ?, ?)',
                       (nombre, categoria, cantidad, precio))
        conn.commit()
        conn.close()

    def obtener_todo(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos')
        filas = cursor.fetchall()
        conn.close()

        inventario_dict = {}
        for f in filas:
            p = Producto(f[0], f[1], f[2], f[3], f[4])
            inventario_dict[p.id] = p.to_dict()
        return inventario_dict

    def eliminar(self, id_prod):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM productos WHERE id = ?', (id_prod,))
        conn.commit()
        conn.close()