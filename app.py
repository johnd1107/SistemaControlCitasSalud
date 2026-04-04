from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_pichincha_2026'

try:
    inicializar_db()
except:
    pass


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('rol') == 'admin': return redirect(url_for('admin_usuarios'))
    if session.get('rol') == 'medico': return redirect(url_for('panel_medico'))

    # PERFIL PACIENTE
    db = obtener_conexion()
    citas = db.execute("""
        SELECT c.*, u.nombre as medico FROM citas c 
        JOIN usuarios u ON c.id_medico = u.id_usuario 
        WHERE c.id_paciente=? ORDER BY c.fecha ASC, c.hora ASC
    """, (session['user_id'],)).fetchall()
    db.close()
    return render_template('dashboard.html', citas=citas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form.get('cedula')
        pw = request.form.get('password')
        if ced == 'admin' and pw == '1234':
            session.clear()
            session.update({'user_id': 0, 'nombre': 'Administrador', 'rol': 'admin'})
            return redirect(url_for('admin_usuarios'))
        db = obtener_conexion()
        u = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if u:
            session.clear()
            session.update({'user_id': u['id_usuario'], 'nombre': u['nombre'], 'rol': u['rol']})
            return redirect(url_for('index'))
        flash("Datos incorrectos", "danger")
    return render_template('login.html')


@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    # Limpiamos sesión para evitar el error de "ya logueado"
    if request.method == 'POST':
        ced, nom, pw = request.form.get('cedula'), request.form.get('nombre'), request.form.get('password')
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?,?,?,'paciente')", (ced, nom, pw))
            db.commit()
            flash("¡Registro exitoso! Inicia sesión.", "success")
            return redirect(url_for('login'))
        except:
            flash("La cédula ya existe.", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


# --- NUEVA RUTA EXCLUSIVA PARA EL MÉDICO ---
@app.route('/panel_medico')
def panel_medico():
    if session.get('rol') != 'medico': return redirect(url_for('login'))
    db = obtener_conexion()
    citas = db.execute("""
        SELECT c.*, u.nombre as paciente FROM citas c 
        JOIN usuarios u ON c.id_paciente = u.id_usuario 
        WHERE c.id_medico=? ORDER BY c.fecha ASC, c.hora ASC
    """, (session['user_id'],)).fetchall()
    db.close()
    return render_template('panel_medico.html', citas=citas)


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session.get('rol') != 'admin': return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        ced, nom, esp = request.form.get('ced_m'), request.form.get('nom_m'), request.form.get('esp_m')
        db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?, 'medico', ?)",
                   (ced, nom, ced, esp))
        db.commit()
    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos)


@app.route('/eliminar_medico/<int:id>')
def eliminar_medico(id):
    if session.get('rol') == 'admin':
        db = obtener_conexion()
        db.execute("DELETE FROM usuarios WHERE id_usuario=?", (id,))
        db.commit()
        db.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'user_id' not in session or session.get('rol') != 'paciente':
        return redirect(url_for('login'))

    db = obtener_conexion()
    if request.method == 'POST':
        id_m = request.form.get('id_medico')
        fec = request.form.get('fecha')
        hor = request.form.get('hora')

        # Obtenemos la especialidad del médico seleccionado para guardarla en la cita
        medico = db.execute("SELECT especialidad FROM usuarios WHERE id_usuario=?", (id_m,)).fetchone()

        db.execute("""
            INSERT INTO citas (id_paciente, id_medico, especialidad, fecha, hora) 
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_id'], id_m, medico['especialidad'], fec, hor))

        db.commit()
        db.close()
        flash("Cita agendada con éxito", "success")
        return redirect(url_for('index'))

    # Listamos solo a los usuarios que son médicos para el combo desplegable
    medicos = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=medicos, hoy=date.today())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)