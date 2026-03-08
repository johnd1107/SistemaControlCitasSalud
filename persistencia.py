import json
import csv
import os

carpeta = "data"

txt_file = os.path.join(carpeta, "datos.txt")
json_file = os.path.join(carpeta, "datos.json")
csv_file = os.path.join(carpeta, "datos.csv")


# TXT

def guardar_txt(nombre, categoria, cantidad, precio):

    with open(txt_file, "a") as f:
        f.write(f"{nombre},{categoria},{cantidad},{precio}\n")


def leer_txt():

    datos = []

    if os.path.exists(txt_file):

        with open(txt_file, "r") as f:

            for linea in f:

                datos.append(linea.strip().split(","))

    return datos


# JSON

def guardar_json(producto):

    try:

        with open(json_file, "r") as f:

            datos = json.load(f)

    except:

        datos = []

    datos.append(producto)

    with open(json_file, "w") as f:

        json.dump(datos, f, indent=4)


def leer_json():

    try:

        with open(json_file, "r") as f:

            return json.load(f)

    except:

        return []


# CSV

def guardar_csv(nombre, categoria, cantidad, precio):

    archivo_existe = os.path.exists(csv_file)

    with open(csv_file, "a", newline="") as f:

        writer = csv.writer(f)

        if not archivo_existe:

            writer.writerow(["Nombre", "Categoria", "Cantidad", "Precio"])

        writer.writerow([nombre, categoria, cantidad, precio])


def leer_csv():

    datos = []

    if os.path.exists(csv_file):

        with open(csv_file, "r") as f:

            reader = csv.reader(f)

            for row in reader:

                datos.append(row)

    return datos