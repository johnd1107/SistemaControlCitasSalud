from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_pichincha_2026'

# Inicialización segura
with app.app_context():
    try:
        inicializar_db()
    except:
        pass


@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('rol') == 'admin': return redirect(url_for('admin_usuarios'))
    if session.get('rol') == 'medico': return redirect(url_for('panel_medico'))

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


@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session.get('rol') != 'admin': return redirect(url_for('login'))
    db = obtener_conexion()

    if request.method == 'POST':
        ced, nom, esp = request.form.get('ced_m'), request.form.get('nom_m'), request.form.get('esp_m')
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) VALUES (?,?,?, 'medico', ?)",
                       (ced, nom, ced, esp))
            db.commit()
            flash("Médico guardado", "success")
        except:
            flash("Error: Cédula duplicada", "danger")

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('admin_usuarios.html', medicos=medicos)


@app.route('/eliminar_medico/<int:id>')
def eliminar_medico(id):
    if session.get('rol') != 'admin': return redirect(url_for('login'))
    db = obtener_conexion()
    try:
        # Primero eliminamos sus citas para evitar error de integridad
        db.execute("DELETE FROM citas WHERE id_medico=?", (id,))
        # Luego eliminamos al médico
        db.execute("DELETE FROM usuarios WHERE id_usuario=?", (id,))
        db.commit()
        flash("Médico y sus citas eliminados", "warning")
    except Exception as e:
        print(f"Error: {e}")
        flash("No se pudo eliminar", "danger")
    finally:
        db.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = obtener_conexion()
    if request.method == 'POST':
        id_m, fec, hor = request.form.get('id_medico'), request.form.get('fecha'), request.form.get('hora')
        med = db.execute("SELECT especialidad FROM usuarios WHERE id_usuario=?", (id_m,)).fetchone()
        db.execute("INSERT INTO citas (id_paciente, id_medico, especialidad, fecha, hora) VALUES (?,?,?,?,?)",
                   (session['user_id'], id_m, med['especialidad'], fec, hor))
        db.commit()
        db.close()
        return redirect(url_for('index'))

    meds = db.execute("SELECT id_usuario, nombre, especialidad FROM usuarios WHERE rol='medico'").fetchall()
    db.close()
    return render_template('agendar.html', medicos=meds, hoy=date.today())


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


@app.route('/registro_paciente', methods=['GET', 'POST'])
def registro_paciente():
    # IMPORTANTE: Si alguien ya está logueado, cerramos su sesión para que no choque con el registro
    if request.method == 'POST':
        ced = request.form.get('cedula')
        nom = request.form.get('nombre')
        pw = request.form.get('password')

        db = obtener_conexion()
        try:
            # Forzamos el rol 'paciente' para que el login sepa a dónde enviarlo luego
            db.execute("""
                INSERT INTO usuarios (cedula, nombre, password, rol) 
                VALUES (?, ?, ?, 'paciente')
            """, (ced, nom, pw))
            db.commit()
            flash("¡Registro exitoso! Ahora puedes ingresar con tu cédula.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error en registro: {e}")
            flash("La cédula ya existe o los datos son incorrectos.", "danger")
        finally:
            db.close()

    return render_template('registro_paciente.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)