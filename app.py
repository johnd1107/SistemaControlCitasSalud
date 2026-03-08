from flask import Flask, render_template, request, redirect, url_for
from models import Inventario

from persistencia import (
    guardar_txt,
    guardar_json,
    guardar_csv,
    leer_txt,
    leer_json,
    leer_csv
)

app = Flask(__name__)
gestor = Inventario()


@app.route('/')
def inicio():
    return render_template('index.html')


# ---------- INVENTARIO ----------
@app.route('/inventario')
def mostrar_inventario():
    productos = gestor.obtener_todo()
    return render_template('inventario.html', lista=productos)


@app.route('/inventario/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cat = request.form['categoria']
    cant = int(request.form['cantidad'])
    prec = float(request.form['precio'])

    # Guardar en SQLite
    gestor.añadir(nombre, cat, cant, prec)

    # Guardar en archivos
    guardar_txt(nombre, cat, cant, prec)
    guardar_csv(nombre, cat, cant, prec)

    guardar_json({
        "nombre": nombre,
        "categoria": cat,
        "cantidad": cant,
        "precio": prec
    })

    return redirect(url_for('mostrar_inventario'))


@app.route('/inventario/eliminar/<int:id>')
def eliminar(id):
    gestor.eliminar(id)
    return redirect(url_for('mostrar_inventario'))


# ---------- DATOS GUARDADOS ----------
@app.route('/datos')
def ver_datos():
    txt = leer_txt()
    json_data = leer_json()
    csv_data = leer_csv()

    return render_template("datos.html",
                           txt=txt,
                           json=json_data,
                           csv=csv_data)


# ---------- OTRAS PAGINAS ----------
@app.route('/acerca-de')
def acerca_de():
    return render_template('about.html')


@app.route('/clientes')
def clientes():
    pacientes = [
        {"id": "P001", "nombre": "Juan Pérez", "cita": "10:30 AM", "estado": "Confirmado"}
    ]
    return render_template('clientes.html', lista=pacientes)


@app.route('/factura')
def factura():

    datos_pago = {
        "nro": "FAC-2026-001",
        "fecha": "26 de febrero, 2026",
        "paciente": "Juan Pérez",
        "servicio": "Consulta General",
        "total": 75.00
    }

    return render_template('factura.html', datos=datos_pago)


if __name__ == '__main__':
    app.run(debug=True)