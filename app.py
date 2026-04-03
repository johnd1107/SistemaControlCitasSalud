from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from conexion.conexion import obtener_conexion, inicializar_db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'saludplus_2026_final_fix'

# Inicializamos la DB al cargar
inicializar_db()

# --- ACCESO Y SEGURIDAD ---
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
        flash("Cédula o contraseña incorrecta", "danger")
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        ced, nom, pw = request.form['cedula'], request.form['nombre'], request.form['password']
        db = obtener_conexion()
        try:
            # Por defecto registramos como médico
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?, ?, ?, 'medico')", (ced, nom, pw))
            db.commit()
            flash("Registro exitoso. Ya puede iniciar sesión.", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: La cédula ya existe.", "danger")
        finally:
            db.close()
    return render_template('registro.html')

# --- VISTA ADMINISTRADOR: LISTA DE MÉDICOS ---
@app.route('/medicos')
def lista_medicos():
    if session.get('rol') != 'admin':
        flash("Acceso denegado: Se requiere rol de Administrador", "danger")
        return redirect(url_for('index'))
    db = obtener_conexion()
    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('medicos.html', medicos=medicos)

# --- GESTIÓN DE PACIENTES ---
@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO pacientes (cedula_p, nombre_p, telefono) VALUES (?,?,?)",
                   (request.form['ced'], request.form['nom'], request.form['tel']))
        db.commit()
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
    paciente = db.execute("SELECT * FROM pacientes WHERE id_paciente=?", (id_p,)).fetchone()
    entradas = db.execute("""
        SELECT h.*, u.nombre as medico_nom 
        FROM historial h 
        JOIN usuarios u ON h.id_medico = u.id_usuario 
        WHERE h.id_paciente=? ORDER BY fecha DESC""", (id_p,)).fetchall()
    db.close()
    return render_template('historial.html', paciente=paciente, entradas=entradas)

# --- SISTEMA DE IMPRESIÓN (PDF) ---
@app.route('/imprimir_factura/<int:id_h>')
def imprimir_factura(id_h):
    db = obtener_conexion()
    data = db.execute("""
        SELECT h.*, p.nombre_p, p.cedula_p FROM historial h 
        JOIN pacientes p ON h.id_paciente = p.id_paciente WHERE h.id_h = ?""", (id_h,)).fetchone()
    db.close()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A5)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(210, 550, "FACTURA - SALUDPLUS")
    p.setFont("Helvetica", 10)
    p.drawString(50, 500, f"PACIENTE: {data['nombre_p']}")
    p.drawString(50, 485, f"CI: {data['cedula_p']}")
    p.line(50, 475, 370, 475)
    p.drawString(50, 450, "Consulta Médica Especializada")
    p.drawRightString(370, 450, "$ 20.00")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 400, "TOTAL CANCELADO: $ 20.00")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Factura.pdf")

@app.route('/imprimir_receta/<int:id_h>')
def imprimir_receta(id_h):
    db = obtener_conexion()
    data = db.execute("""
        SELECT h.*, p.nombre_p, u.nombre as med FROM historial h 
        JOIN pacientes p ON h.id_paciente = p.id_paciente 
        JOIN usuarios u ON h.id_medico = u.id_usuario WHERE h.id_h = ?""", (id_h,)).fetchone()
    db.close()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A5)
    p.drawString(50, 550, f"PACIENTE: {data['nombre_p']}")
    p.drawString(50, 530, f"DIAGNÓSTICO: {data['diagnostico']}")
    p.drawString(50, 500, "RECETA:")
    p.drawString(60, 485, data['receta'])
    p.drawCentredString(210, 100, f"Firma: Dr. {data['med']}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Receta.pdf")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)