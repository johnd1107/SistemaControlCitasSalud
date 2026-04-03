from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from conexion.conexion import obtener_conexion, inicializar_db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'saludplus_ultimate_2026'

# Inicializamos la base de datos al arrancar
inicializar_db()

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced, pw = request.form['cedula'], request.form['password']
        db = obtener_conexion()
        user = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if user:
            session.update({'user_id': user['id_usuario'], 'nombre': user['nombre'], 'rol': user['rol']})
            return redirect(url_for('index'))
        flash("Credenciales incorrectas. Verifique su cédula y contraseña.", "danger")
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        ced, nom, pw = request.form['cedula'], request.form['nombre'], request.form['password']
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?, ?, ?, 'medico')", (ced, nom, pw))
            db.commit()
            flash("¡Usuario registrado exitosamente! Ya puede ingresar.", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: La cédula ya existe en el sistema.", "danger")
        finally:
            db.close()
    return render_template('registro.html')

@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO pacientes (cedula_p, nombre_p, telefono) VALUES (?,?,?)",
                   (request.form['ced'], request.form['nom'], request.form['tel']))
        db.commit()
        flash("Paciente registrado correctamente", "success")
    lista = db.execute("SELECT * FROM pacientes").fetchall()
    db.close()
    return render_template('pacientes.html', pacientes=lista)

@app.route('/historial/<int:id_p>', methods=['GET', 'POST'])
def historial(id_p):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO historial (id_paciente, id_medico, diagnostico, receta) VALUES (?,?,?,?)",
                   (id_p, session['user_id'], request.form['diag'], request.form['rece']))
        db.commit()
        flash("Consulta guardada", "info")
    paciente = db.execute("SELECT * FROM pacientes WHERE id_paciente=?", (id_p,)).fetchone()
    entradas = db.execute("SELECT * FROM historial WHERE id_paciente=? ORDER BY fecha DESC", (id_p,)).fetchall()
    db.close()
    return render_template('historial.html', paciente=paciente, entradas=entradas)

@app.route('/imprimir/<int:id_h>')
def imprimir(id_h):
    db = obtener_conexion()
    data = db.execute("""SELECT h.*, p.nombre_p, u.nombre as med 
                         FROM historial h 
                         JOIN pacientes p ON h.id_paciente=p.id_paciente 
                         JOIN usuarios u ON h.id_medico=u.id_usuario 
                         WHERE h.id_h=?""", (id_h,)).fetchone()
    db.close()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A5)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(210, 550, "CENTRO MÉDICO SALUDPLUS")
    p.line(30, 540, 390, 540)
    p.setFont("Helvetica", 10)
    p.drawString(50, 500, f"Paciente: {data['nombre_p']}")
    p.drawString(50, 480, f"Fecha: {data['fecha']}")
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 450, "DIAGNÓSTICO:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 435, data['diagnostico'])
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 400, "INDICACIONES:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 385, data['receta'])
    p.line(150, 100, 270, 100)
    p.drawCentredString(210, 85, f"Dr. {data['med']}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="receta.pdf", mimetype='application/pdf')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)