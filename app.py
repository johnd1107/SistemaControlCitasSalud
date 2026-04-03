from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from conexion.conexion import obtener_conexion, inicializar_db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'saludplus_final_2026'

# Crear tablas si no existen
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced, pw = request.form['cedula'], request.form['password']
        # Acceso Admin
        if ced == 'admin' and pw == '1234':
            session.update({'user_id': 0, 'nombre': 'Administrador', 'rol': 'admin'})
            return redirect(url_for('index'))

        db = obtener_conexion()
        user = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if user:
            session.update({'user_id': user['id_usuario'], 'nombre': user['nombre'], 'rol': user['rol']})
            return redirect(url_for('index'))
        flash("Credenciales incorrectas", "danger")
    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?,?,?,'medico')",
                       (request.form['cedula'], request.form['nombre'], request.form['password']))
            db.commit()
            flash("Médico registrado exitosamente", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: Cédula ya existe", "danger")
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
    lista = db.execute("SELECT * FROM pacientes").fetchall()
    db.close()
    return render_template('pacientes.html', pacientes=lista)


@app.route('/eliminar_paciente/<int:id_p>')
def eliminar_paciente(id_p):
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    db = obtener_conexion()
    db.execute("DELETE FROM pacientes WHERE id_paciente=?", (id_p,))
    db.commit()
    db.close()
    return redirect(url_for('pacientes'))


@app.route('/historial/<int:id_p>', methods=['GET', 'POST'])
def historial(id_p):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO historial (id_paciente, id_medico, diagnostico, receta) VALUES (?,?,?,?)",
                   (id_p, session['user_id'], request.form['diag'], request.form['rece']))
        db.commit()
    paciente = db.execute("SELECT * FROM pacientes WHERE id_paciente=?", (id_p,)).fetchone()
    entradas = db.execute(
        "SELECT h.*, u.nombre as med FROM historial h JOIN usuarios u ON h.id_medico = u.id_usuario WHERE h.id_paciente=? ORDER BY fecha DESC",
        (id_p,)).fetchall()
    db.close()
    return render_template('historial.html', paciente=paciente, entradas=entradas)


@app.route('/medicos')
def lista_medicos():
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    db = obtener_conexion()
    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('medicos.html', medicos=medicos)


@app.route('/imprimir_reporte/<string:tipo>')
def imprimir_reporte(tipo):
    db = obtener_conexion()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(100, 800, f"REPORTE DE {tipo.upper()}")
    y = 750
    data = db.execute("SELECT * FROM pacientes").fetchall() if tipo == 'pacientes' else db.execute(
        "SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    for i in data:
        p.drawString(100, y, f"- {i[1]} | {i[2]}")
        y -= 20
    p.showPage();
    p.save();
    db.close();
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Reporte_{tipo}.pdf")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
