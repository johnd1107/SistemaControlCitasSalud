from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_final_2026'

inicializar_db()

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form['cedula']
        pw = request.form['password']
        if ced == 'admin' and pw == '1234':
            session.update({'user_id':0, 'nombre':'Administrador', 'rol':'admin'})
            return redirect(url_for('index'))
        db = obtener_conexion()
        u = db.execute("SELECT * FROM usuarios WHERE cedula=? AND password=?", (ced, pw)).fetchone()
        db.close()
        if u:
            session.update({'user_id':u['id_usuario'], 'nombre':u['nombre'], 'rol':u['rol']})
            return redirect(url_for('index'))
        flash("Datos incorrectos", "danger")
    return render_template('login.html')

# --- PERFIL PACIENTE: REGISTRO ---
@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    if request.method == 'POST':
        ced = request.form.get('ced', '').strip()
        nom = request.form.get('nom', '').strip()
        edad = request.form.get('edad', '').strip()
        dir = request.form.get('dir', '').strip()
        if not ced or not nom or not edad or not dir:
            flash("Todos los campos son obligatorios", "warning")
            return render_template('registro_paciente.html')
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, edad, domicilio) VALUES (?,?,?, 'paciente',?,?)",
                       (ced, nom, ced, edad, dir))
            db.commit()
            flash("Registro exitoso", "success")
            return redirect(url_for('login'))
        except: flash("Error: Cédula duplicada", "danger")
        finally: db.close()
    return render_template('registro_paciente.html')

# --- PERFIL ADMIN: GESTIÓN MÉDICOS ---
@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?,'medico',?)",
                   (request.form['ced'], request.form['nom'], request.form['ced'], request.form['esp']))
        db.commit()
        flash("Médico registrado", "success")
    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    pacientes = db.execute("SELECT * FROM usuarios WHERE rol='paciente'").fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, pacientes=pacientes)

# --- PERFIL PACIENTE: AGENDAR ---
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if session.get('rol') != 'paciente': return redirect(url_for('index'))
    db = obtener_conexion()
    if request.method == 'POST':
        db.execute("INSERT INTO citas (id_paciente, id_medico, especialidad, fecha, hora) VALUES (?,?,?,?,?)",
                   (session['user_id'], request.form['id_m'], request.form['esp'], request.form['fec'], request.form['hor']))
        db.commit(); db.close()
        flash("Cita agendada", "success"); return redirect(url_for('index'))
    medicos = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=medicos, hoy=date.today())

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)