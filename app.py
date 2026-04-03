from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from conexion.conexion import obtener_conexion, inicializar_db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'saludplus_final_fix_2026'

# Inicializar Base de Datos (Crea tablas si no existen)
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced, pw = request.form['cedula'], request.form['password']
        if ced == 'admin' and pw == '1234':
            session.update({'user_id': 0, 'nombre': 'Administrador', 'rol': 'admin'})
            return redirect(url_for('index'))

        db = obtener_conexion()
        u = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if u:
            session.update({'user_id': u['id_usuario'], 'nombre': u['nombre'], 'rol': u['rol']})
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
            return redirect(url_for('login'))
        except:
            flash("Cédula ya registrada", "danger")
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


@app.route('/editar_paciente/<int:id>', methods=['POST'])
def editar_paciente(id):
    db = obtener_conexion()
    db.execute("UPDATE pacientes SET cedula_p=?, nombre_p=?, telefono=? WHERE id_paciente=?",
               (request.form['ced'], request.form['nom'], request.form['tel'], id))
    db.commit()
    db.close()
    return redirect(url_for('pacientes'))


@app.route('/eliminar_paciente/<int:id>')
def eliminar_paciente(id):
    if session.get('rol') == 'admin':
        db = obtener_conexion()
        db.execute("DELETE FROM pacientes WHERE id_paciente=?", (id,))
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

    p = db.execute("SELECT * FROM pacientes WHERE id_paciente=?", (id_p,)).fetchone()
    h = db.execute("""SELECT h.*, u.nombre as med FROM historial h 
                      JOIN usuarios u ON h.id_medico=u.id_usuario 
                      WHERE h.id_paciente=? ORDER BY fecha DESC""", (id_p,)).fetchall()
    db.close()
    return render_template('historial.html', paciente=p, entradas=h)


# --- RUTAS DE ADMINISTRADOR (SOLUCIONAN EL BUILDERROR) ---
@app.route('/medicos')
def lista_medicos():  # Nombre exacto que pide tu dashboard
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    db = obtener_conexion()
    lista = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('medicos.html', medicos=lista)


@app.route('/imprimir/<tipo>')  # Nombre exacto que pide tu pacientes.html
def imprimir(tipo):
    db = obtener_conexion()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.drawString(100, 800, f"REPORTE DE {tipo.upper()}")
    y = 750
    items = db.execute("SELECT * FROM pacientes").fetchall() if tipo == 'pacientes' else db.execute(
        "SELECT * FROM usuarios").fetchall()
    for i in items:
        pdf.drawString(100, y, f"- {i[1]} | {i[2]}")
        y -= 20
    pdf.showPage();
    pdf.save();
    db.close();
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"reporte_{tipo}.pdf")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)