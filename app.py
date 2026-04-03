from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_2026_total'

# Asegura que las tablas existan
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


# --- RUTA DE ADMINISTRACIÓN (Aquí agregas Médicos) ---
@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session.get('rol') != 'admin': return redirect(url_for('index'))

    db = obtener_conexion()
    if request.method == 'POST':
        ced_m = request.form.get('ced_m')
        nom_m = request.form.get('nom_m')
        esp_m = request.form.get('esp_m')

        if ced_m and nom_m and esp_m:
            try:
                # Se guarda al médico (su clave inicial es su cédula)
                db.execute(
                    "INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                    (ced_m, nom_m, ced_m, esp_m))
                db.commit()
                flash(f"Médico {nom_m} registrado con éxito", "success")
            except:
                flash("Error: Esa cédula ya existe", "danger")

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    pacientes = db.execute("SELECT * FROM usuarios WHERE rol='paciente'").fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, pacientes=pacientes)


@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    if request.method == 'POST':
        ced = request.form.get('ced', '').strip()
        nom = request.form.get('nom', '').strip()
        pw = request.form.get('pass', '').strip()
        ed = request.form.get('edad', '').strip()
        di = request.form.get('dir', '').strip()

        if len(ced) != 10:
            flash("Cédula inválida (requiere 10 dígitos)", "warning")
            return render_template('registro_paciente.html')

        db = obtener_conexion()
        try:
            db.execute(
                "INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                (ced, nom, pw, ed, di))
            db.commit()
            flash("Registro exitoso", "success")
            return redirect(url_for('login'))
        except:
            flash("La cédula ya está registrada", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


@app.route('/logout')
def logout():
    session.clear();
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)