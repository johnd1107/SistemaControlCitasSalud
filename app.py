from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/acerca-de')
def acerca_de():
    return render_template('about.html')

@app.route('/clientes')
def clientes():
    # Lista profesional de pacientes
    pacientes = [
        {"id": "P001", "nombre": "Juan Pérez", "cita": "10:30 AM", "estado": "Confirmado"},
        {"id": "P002", "nombre": "María García", "cita": "11:15 AM", "estado": "Pendiente"},
        {"id": "P003", "nombre": "Carlos Ruiz", "cita": "12:00 PM", "estado": "Confirmado"}
    ]
    return render_template('clientes.html', lista=pacientes)

@app.route('/factura')
def factura():
    # Diccionario 'datos' corregido para factura.html
    datos_pago = {
        "nro": "FAC-2026-001",
        "fecha": "20 de febrero, 2026",
        "paciente": "Juan Pérez",
        "servicio": "Consulta General + Laboratorio",
        "total": 75.00
    }
    return render_template('factura.html', datos=datos_pago)

if __name__ == '__main__':
    app.run(debug=True)