from models import Inventario

def menu():
    inv = Inventario()
    while True:
        print("\n--- MENÚ DE INVENTARIO (CONSOLA) ---")
        print("1. Ver todos los productos")
        print("2. Agregar nuevo producto")
        print("3. Eliminar por ID")
        print("4. Salir")
        op = input("Seleccione: ")

        if op == "1":
            datos = inv.obtener_todo()
            for id, p in datos.items():
                print(f"ID: {id} | {p['nombre']} | Stock: {p['cantidad']} | ${p['precio']}")
        elif op == "2":
            n = input("Nombre: ")
            c = input("Categoría: ")
            can = int(input("Cantidad: "))
            pre = float(input("Precio: "))
            inv.añadir(n, c, can, pre)
        elif op == "3":
            idx = int(input("ID a borrar: "))
            inv.eliminar(idx)
        elif op == "4":
            break

if __name__ == "__main__":
    menu()