import json
import csv
import os
from database import db


# 2.4. Definir el modelo de datos (SQLAlchemy)
class Joya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)


# 2.2. Persistencia con Archivos TXT, JSON y CSV
def guardar_persistencia_multiple(n, m, c, p):
    # Crear carpeta data si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    # Creamos un diccionario para el formato JSON
    datos_dict = {
        "nombre": n,
        "material": m,
        "cantidad": c,
        "precio": p
    }

    # --- PERSISTENCIA EN TXT (usando open) ---
    with open('data/datos.txt', 'a', encoding='utf-8') as f:
        f.write(f"JOYERIA: {n} | MAT: {m} | CANT: {c} | PVP: {p}\n")

    # --- PERSISTENCIA EN JSON (librería json) ---
    json_path = 'data/datos.json'
    lista_temporal = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                lista_temporal = json.load(f)
            except:
                lista_temporal = []

    lista_temporal.append(datos_dict)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(lista_temporal, f, indent=4)

    # --- PERSISTENCIA EN CSV (librería csv) ---
    csv_path = 'data/datos.csv'
    escribir_cabecera = not os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if escribir_cabecera:
            writer.writerow(['Nombre', 'Material', 'Cantidad', 'Precio'])
        writer.writerow([n, m, c, p])