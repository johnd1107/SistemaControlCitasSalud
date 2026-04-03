from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from conexion.conexion import obtener_conexion, inicializar_db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'saludplus_final_2026_master'

# Inicializa las tablas al comenzar
inicializar_db()


# --- ACCESO PRINCIPAL ---
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# --- SISTEMA DE LOGIN Y REGISTRO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form['cedula']
        pw = request.form['password']

        # Login para Administrador
        if ced == 'admin' and pw == '1234':
            session.update({'user_id': 0, 'nombre': 'Administrador', 'rol': 'admin'})
            return redirect(url_for('index'))

        # Login para Médicos
        db = obtener_conexion()
        u = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()

        if u:
            session.update({'user_id': u['id_usuario'], 'nombre': u['nombre'], 'rol': u['rol']})
            return redirect(url_for('index'))

        flash("Datos incorrectos. Intente de nuevo.", "danger")
    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?,?,?,'medico')",
                       (request.form['cedula'], request.form['nombre'], request.form['password']))
            db.commit()
            flash("Cuenta de médico creada con éxito", "success")
            return redirect(url_for('login'))
        except:
            flash("La cédula ya está registrada", "danger")
        finally:
            db.close()
    return render_template('registro.html')


# --- CRUD DE PACIENTES ---
@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'user_id' not in session: return redirect(url_for('login'))

    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO pacientes (cedula_p, nombre_p, telefono) VALUES (?,?,?)",
                   (request.form['ced'], request.form['nom'], request.form['tel']))
        db.commit()
        flash("Paciente registrado", "success")

    lista = db.execute("SELECT * FROM pacientes").fetchall()
    db.close()
    return render_template('pacientes.html', pacientes=lista)


@app.route('/editar_paciente/<int:id>', methods=['POST'])
def editar_paciente(id):
    db = obtener_conexion()
    db.execute("UPDATE pacientes SET cedula_p=?, nombre_p=?, telefono=? WHERE id_paciente=?",
               (request.form['ced'], request.form['nom'], request.form['tel'], id))
    db.commit()
    db.close()
    flash("Datos actualizados correctamente", "info")
    return redirect(url_for('pacientes'))


@app.route('/eliminar_paciente/<int:id>')
def eliminar_paciente(id):
    if session.get('rol') == 'admin':
        db = obtener_conexion()
        db.execute("DELETE FROM pacientes WHERE id_paciente=?", (id,))
        db.commit()
        db.close()
        flash("Paciente eliminado", "warning")
    else:
        flash("Acceso denegado: Solo administradores", "danger")
    return redirect(url_for('pacientes'))


# --- HISTORIAL CLÍNICO (RELACIÓN MÉDICO-PACIENTE) ---
@app.route('/historial/<int:id_p>', methods=['GET', 'POST'])
def historial(id_p):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()

    if request.method == 'POST':
        db.execute("INSERT INTO historial (id_paciente, id_medico, diagnostico, receta) VALUES (?,?,?,?)",
                   (id_p, session['user_id'], request.form['diag'], request.form['rece']))
        db.commit()
        flash("Consulta guardada", "success")

    paciente = db.execute("SELECT * FROM pacientes WHERE id_paciente=?", (id_p,)).fetchone()
    entradas = db.execute("""
        SELECT h.*, u.nombre as med FROM historial h 
        JOIN usuarios u ON h.id_medico = u.id_usuario 
        WHERE h.id_paciente=? ORDER BY fecha DESC""", (id_p,)).fetchall()
    db.close()
    return render_template('historial.html', paciente=paciente, entradas=entradas)


# --- PANEL ADMINISTRATIVO (MÉDICOS) ---
@app.route('/medicos')
def lista_medicos():
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    db = obtener_conexion()
    meds = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('medicos.html', medicos=meds)


@app.route('/eliminar_medico/<int:id>')
def eliminar_medico(id):
    if session.get('rol') == 'admin':
        db = obtener_conexion()
        db.execute("DELETE FROM usuarios WHERE id_usuario=?", (id,))
        db.commit()
        db.close()
    return redirect(url_for('lista_medicos'))


# --- GENERACIÓN DE REPORTES PDF ---
@app.route('/reporte/<tipo>')
def reporte_lista(tipo):
    if session.get('rol') != 'admin': return redirect(url_for('index'))

    db = obtener_conexion()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Reporte SaludPlus - {tipo}")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, f"CENTRO MÉDICO SALUDPLUS - REPORTE DE {tipo.upper()}")
    pdf.line(100, 790, 500, 790)

    y = 750
    pdf.setFont("Helvetica", 11)

    if tipo == 'pacientes':
        items = db.execute("SELECT * FROM pacientes").fetchall()
        for i in items:
            pdf.drawString(100, y, f"CI: {i['cedula_p']} | Nombre: {i['nombre_p']} | Tel: {i['telefono']}")
            y -= 25
    else:
        items = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
        for i in items:
            pdf.drawString(100, y, f"CI: {i['cedula']} | Médico: {i['nombre']}")
            y -= 25

    pdf.showPage()
    pdf.save()
    db.close()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"reporte_{tipo}.pdf")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)