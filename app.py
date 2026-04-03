from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_2026_total_fix'

# Inicializa base de datos
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form.get('cedula')
        pw = request.form.get('password')
        if ced == 'admin' and pw == '1234':
            session.update({'user_id': 0, 'nombre': 'Administrador', 'rol': 'admin'})
            return redirect(url_for('index'))
        db = obtener_conexion()
        u = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if u:
            session.update({'user_id': u['id_usuario'], 'nombre': u['nombre'], 'rol': u['rol']})
            return redirect(url_for('index'))
        flash("Datos incorrectos", "danger")
    return render_template('login.html')


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()

    # LÓGICA PARA ADMIN: AGREGAR MÉDICOS
    if request.method == 'POST' and session['rol'] == 'admin':
        ced_m = request.form.get('ced_m')
        nom_m = request.form.get('nom_m')
        esp_m = request.form.get('esp_m')
        if ced_m and nom_m and esp_m:
            try:
                db.execute(
                    "INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                    (ced_m, nom_m, ced_m, esp_m))
                db.commit()
                flash("Médico registrado exitosamente", "success")
            except:
                flash("Error: Cédula duplicada", "danger")

    # DATOS PARA LAS TABLAS
    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    pacientes = db.execute("SELECT * FROM usuarios WHERE rol='paciente'").fetchall()

    # CITAS PARA EL MÉDICO (Si el usuario logueado es médico)
    citas_medico = []
    if session['rol'] == 'medico':
        citas_medico = db.execute("""
            SELECT c.*, u.nombre as paciente, u.cedula as ced_paciente 
            FROM citas c JOIN usuarios u ON c.id_paciente = u.id_usuario 
            WHERE c.id_medico = ? AND c.estado = 'Pendiente'
        """, (session['user_id'],)).fetchall()

    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, pacientes=pacientes, citas_medico=citas_medico)


@app.route('/atender_cita/<int:id_cita>', methods=['GET', 'POST'])
def atender_cita(id_cita):
    if session.get('rol') != 'medico': return redirect(url_for('index'))
    db = obtener_conexion()
    if request.method == 'POST':
        diag = request.form.get('diagnostico')
        rece = request.form.get('receta')
        db.execute("INSERT INTO consultas (id_cita, diagnostico, receta) VALUES (?,?,?)", (id_cita, diag, rece))
        db.execute("UPDATE citas SET estado='Atendido' WHERE id_cita=?", (id_cita,))
        db.commit();
        db.close()
        flash("Consulta guardada", "success")
        return redirect(url_for('admin_usuarios'))

    cita = db.execute(
        "SELECT c.*, u.nombre as paciente FROM citas c JOIN usuarios u ON c.id_paciente = u.id_usuario WHERE c.id_cita=?",
        (id_cita,)).fetchone()
    db.close()
    return render_template('atender.html', cita=cita)


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if session.get('rol') != 'paciente': return redirect(url_for('index'))
    db = obtener_conexion()
    if request.method == 'POST':
        id_m = request.form.get('id_m')
        esp = request.form.get('esp')
        fec = request.form.get('fec')
        hor = request.form.get('hor')
        db.execute("INSERT INTO citas (id_paciente, id_medico, especialidad, fecha, hora) VALUES (?,?,?,?,?)",
                   (session['user_id'], id_m, esp, fec, hor))
        db.commit();
        db.close()
        flash("Cita agendada", "success");
        return redirect(url_for('index'))

    medicos = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=medicos, hoy=date.today())


@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    if request.method == 'POST':
        ced = request.form.get('ced')
        nom = request.form.get('nom')
        pw = request.form.get('pass')
        ed = request.form.get('edad')
        di = request.form.get('dir')
        if len(ced) != 10:
            flash("Cédula debe tener 10 dígitos", "warning")
            return render_template('registro_paciente.html')
        db = obtener_conexion()
        try:
            db.execute(
                "INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                (ced, nom, pw, ed, di))
            db.commit()
            flash("Registro exitoso", "success");
            return redirect(url_for('login'))
        except:
            flash("Error en registro", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


@app.route('/logout')
def logout():
    session.clear();
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)