from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_2026_seguro'

# Inicializa las tablas al arrancar
inicializar_db()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form.get('cedula')
        pw = request.form.get('password')

        # Acceso Admin
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
    if 'user_id' in session: return redirect(url_for('index'))

    if request.method == 'POST':
        ced = request.form.get('ced', '').strip()
        nom = request.form.get('nom', '').strip()
        pw = request.form.get('pass', '').strip()
        edad = request.form.get('edad', '').strip()
        dir = request.form.get('dir', '').strip()

        if len(ced) != 10:
            flash("La cédula debe tener exactamente 10 dígitos", "warning")
            return render_template('registro_paciente.html')

        db = obtener_conexion()
        try:
            db.execute(
                "INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                (ced, nom, pw, edad, dir))
            db.commit()
            flash("Registro exitoso. Inicia sesión con tu nueva clave.", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: Esta cédula ya está registrada", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session.get('rol') != 'admin': return redirect(url_for('index'))

    db = obtener_conexion()
    if request.method == 'POST':
        ced_m = request.form.get('ced_m')
        nom_m = request.form.get('nom_m')
        esp_m = request.form.get('esp_m')

        if ced_m and nom_m and esp_m:
            # La contraseña inicial del médico será su propia cédula
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                       (ced_m, nom_m, ced_m, esp_m))
            db.commit()
            flash(f"Médico {nom_m} registrado correctamente", "success")

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    pacientes = db.execute("SELECT * FROM usuarios WHERE rol='paciente'").fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, pacientes=pacientes)


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
        db.commit()
        db.close()
        flash("¡Cita agendada con éxito!", "success")
        return redirect(url_for('index'))

    # Obtenemos los médicos para que el paciente elija
    medicos = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=medicos, hoy=date.today())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)