from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_2026_final_fix'

# Inicializa las tablas (Usuarios, Citas, Consultas)
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    citas_p = []
    if session['rol'] == 'paciente':
        citas_p = db.execute("""SELECT c.*, u.nombre as medico FROM citas c 
                                JOIN usuarios u ON c.id_medico = u.id_usuario 
                                WHERE c.id_paciente=?""", (session['user_id'],)).fetchall()
    db.close()
    return render_template('dashboard.html', citas=citas_p)


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
        flash("Cédula o contraseña incorrecta", "danger")
    return render_template('login.html')


# ESTA ES LA FUNCIÓN QUE DABA EL ERROR "BUILD ERROR"
@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    if request.method == 'POST':
        ced, nom, pw = request.form.get('ced'), request.form.get('nom'), request.form.get('pass')
        ed, di = request.form.get('edad'), request.form.get('dir')
        if len(ced) != 10:
            flash("La cédula debe tener 10 dígitos", "warning")
            return render_template('registro_paciente.html')
        db = obtener_conexion()
        try:
            db.execute(
                "INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                (ced, nom, pw, ed, di))
            db.commit()
            flash("Registro exitoso, ahora inicia sesión", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: Cédula ya registrada", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST' and session['rol'] == 'admin':
        ced, nom, esp = request.form.get('ced_m'), request.form.get('nom_m'), request.form.get('esp_m')
        db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                   (ced, nom, ced, esp))
        db.commit()

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    pacientes = db.execute("SELECT * FROM usuarios WHERE rol='paciente'").fetchall()
    citas_m = []
    if session['rol'] == 'medico':
        citas_m = db.execute("""SELECT c.*, u.nombre as paciente, u.cedula, u.domicilio FROM citas c 
                                JOIN usuarios u ON c.id_paciente = u.id_usuario 
                                WHERE c.id_medico=? AND c.estado='Pendiente'""", (session['user_id'],)).fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, pacientes=pacientes, citas_medico=citas_m)


@app.route('/atender/<int:id_cita>', methods=['GET', 'POST'])
def atender(id_cita):
    if session.get('rol') != 'medico': return redirect(url_for('index'))
    db = obtener_conexion()
    if request.method == 'POST':
        diag, rece = request.form.get('diag'), request.form.get('rece')
        db.execute("INSERT INTO consultas (id_cita, diagnostico, receta) VALUES (?,?,?)", (id_cita, diag, rece))
        db.execute("UPDATE citas SET estado='Atendido' WHERE id_cita=?", (id_cita,))
        db.commit();
        db.close()
        flash("Consulta finalizada", "success")
        return redirect(url_for('admin_usuarios'))
    cita = db.execute(
        "SELECT c.*, u.nombre as paciente, u.cedula, u.edad FROM citas c JOIN usuarios u ON c.id_paciente = u.id_usuario WHERE id_cita=?",
        (id_cita,)).fetchone()
    db.close()
    return render_template('atender.html', cita=cita)


@app.route('/imprimir_turno/<int:id_cita>')
def imprimir_turno(id_cita):
    db = obtener_conexion()
    d = db.execute("""SELECT c.*, p.nombre as paciente, m.nombre as medico 
                      FROM citas c JOIN usuarios p ON c.id_paciente = p.id_usuario 
                      JOIN usuarios m ON c.id_medico = m.id_usuario WHERE c.id_cita=?""", (id_cita,)).fetchone()
    db.close()
    return render_template('imprimir_turno.html', d=d)


@app.route('/logout')
def logout():
    session.clear();
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)