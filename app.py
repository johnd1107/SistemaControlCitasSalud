from flask import Flask, render_template, request, redirect, url_for
from models import Inventario

app = Flask(__name__)
gestor = Inventario()

@app.route('/')
def inicio():
    return render_template('index.html')

# --- RUTAS DE INVENTARIO (CRUD) ---
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
    gestor.añadir(nombre, cat, cant, prec)
    return redirect(url_for('mostrar_inventario'))

@app.route('/inventario/eliminar/<int:id>')
def eliminar(id):
    gestor.eliminar(id)
    return redirect(url_for('mostrar_inventario'))

# --- RUTAS QUE FALTABAN (Para evitar el BuildError) ---
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