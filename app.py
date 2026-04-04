from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_pichincha_2026_final'

# Inicialización de la base de datos
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    citas_p = []
    if session['rol'] == 'paciente':
        citas_p = db.execute("""
            SELECT c.*, u.nombre as medico 
            FROM citas c JOIN usuarios u ON c.id_medico = u.id_usuario 
            WHERE c.id_paciente=? ORDER BY c.fecha, c.hora
        """, (session['user_id'],)).fetchall()
    db.close()
    return render_template('dashboard.html', citas=citas_p)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced, pw = request.form.get('cedula'), request.form.get('password')
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


@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    if request.method == 'POST':
        ced, nom, pw = request.form.get('ced'), request.form.get('nom'), request.form.get('pass')
        ed, di = request.form.get('edad'), request.form.get('dir')
        db = obtener_conexion()
        try:
            db.execute(
                "INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                (ced, nom, pw, ed, di))
            db.commit()
            return redirect(url_for('login'))
        except:
            flash("Error: El usuario ya existe", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()

    # GUARDAR MÉDICO (CORREGIDO)
    if request.method == 'POST' and session['rol'] == 'admin':
        ced, nom, esp = request.form.get('ced_m'), request.form.get('nom_m'), request.form.get('esp_m')
        db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                   (ced, nom, ced, esp))
        db.commit()

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()

    citas_m = []
    if session['rol'] == 'medico':
        citas_m = db.execute("""
            SELECT c.*, u.nombre as paciente FROM citas c 
            JOIN usuarios u ON c.id_paciente = u.id_usuario 
            WHERE c.id_medico=? ORDER BY c.estado DESC, c.hora ASC
        """, (session['user_id'],)).fetchall()

    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, citas_medico=citas_m)


@app.route('/eliminar_usuario/<int:id_u>')
def eliminar_usuario(id_u):
    if session.get('rol') == 'admin':
        db = obtener_conexion()
        db.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_u,))
        db.commit()
        db.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        id_m, fec, hor = request.form.get('id_medico'), request.form.get('fecha'), request.form.get('hora')
        m = db.execute("SELECT especialidad FROM usuarios WHERE id_usuario=?", (id_m,)).fetchone()
        esp = m['especialidad'] if m else "General"
        db.execute(
            "INSERT INTO citas (id_paciente, id_medico, especialidad, fecha, hora, estado) VALUES (?,?,?,?,?,'Pendiente')",
            (session['user_id'], id_m, esp, fec, hor))
        db.commit();
        db.close()
        return redirect(url_for('index'))

    medicos = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=medicos, hoy=date.today())


@app.route('/atender/<int:id_cita>')
def atender(id_cita):
    db = obtener_conexion()
    db.execute("UPDATE citas SET estado='Atendido' WHERE id_cita=?", (id_cita,))
    db.commit();
    db.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/logout')
def logout():
    session.clear();
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)