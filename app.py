from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'saludplus_secret_2026'

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Por ahora, aceptamos cualquier usuario para que puedas ver la página
        session['usuario'] = request.form.get('username')
        return redirect(url_for('index'))
    return render_template('login.html')

# --- PÁGINA PRINCIPAL ---
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    # Lista de prueba para que no salga error si la base de datos falla
    pacientes_prueba = [
        {'id_paciente': 1, 'nombre': 'Juan', 'apellido': 'Pérez', 'cedula': '1712345678', 'telefono': '09999999'},
        {'id_paciente': 2, 'nombre': 'Ana', 'apellido': 'García', 'cedula': '1787654321', 'telefono': '08888888'}
    ]
    return render_template('productos/index.html', pacientes=pacientes_prueba)

# --- MÉDICOS ---
@app.route('/medicos')
def medicos():
    if 'usuario' not in session: return redirect(url_for('login'))
    return render_template('medicos.html')

# --- FACTURA ---
@app.route('/factura')
def factura():
    if 'usuario' not in session: return redirect(url_for('login'))
    f = {"nro": "001-001", "fecha": "27/03/2026", "total": 50.40}
    return render_template('factura.html', f=f)

# --- PERFIL ---
@app.route('/perfil')
def perfil():
    return render_template('perfil_paciente.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)