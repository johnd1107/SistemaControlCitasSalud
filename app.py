from flask import Flask, render_template, request, redirect, url_for, session, flash
from conexion.conexion import obtener_conexion, inicializar_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'salud_plus_pichincha_2026'

# Crear base de datos al iniciar
try:
    inicializar_db()
except Exception as e:
    print(f"Error al inicializar DB: {e}")


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('rol') in ['admin', 'medico']:
        return redirect(url_for('admin_usuarios'))

    db = obtener_conexion()
    citas = db.execute("""
        SELECT c.*, u.nombre as medico FROM citas c 
        JOIN usuarios u ON c.id_medico = u.id_usuario 
        WHERE c.id_paciente=?
    """, (session['user_id'],)).fetchall()
    db.close()
    return render_template('dashboard.html', citas=citas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ced = request.form.get('cedula')
        pw = request.form.get('password')

        # Acceso Manual Admin
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
    if request.method == 'POST':
        ced, nom, pw = request.form.get('cedula'), request.form.get('nombre'), request.form.get('password')
        db = obtener_conexion()
        try:
            db.execute("INSERT INTO usuarios (cedula, nombre, password, rol) VALUES (?,?,?,'paciente')", (ced, nom, pw))
            db.commit()
            flash("¡Registro exitoso! Ya puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
        except:
            flash("Error: La cédula ya existe.", "danger")
        finally:
            db.close()
    return render_template('registro_paciente.html')


# CORREGIDO: Se quitó el @@ sobrante
@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = obtener_conexion()

    # ACCIÓN: AGREGAR MÉDICO (Solo para el Admin)
    if request.method == 'POST' and session.get('rol') == 'admin':
        ced = request.form.get('ced_m')
        nom = request.form.get('nom_m')
        esp = request.form.get('esp_m')

        if ced and nom and esp:
            try:
                db.execute("""
                    INSERT INTO usuarios (cedula, nombre, password, rol, especialidad) 
                    VALUES (?, ?, ?, 'medico', ?)
                """, (ced, nom, ced, esp))
                db.commit()
                flash("Médico agregado exitosamente", "success")
            except Exception as e:
                print(f"Error al insertar: {e}")
                flash("Error: La cédula ya existe", "danger")
        else:
            flash("Todos los campos son obligatorios", "warning")

    medicos = db.execute("SELECT * FROM usuarios WHERE rol='medico'").fetchall()

    citas_m = []
    if session.get('rol') == 'medico':
        citas_m = db.execute("""
            SELECT c.*, u.nombre as paciente 
            FROM citas c JOIN usuarios u ON c.id_paciente = u.id_usuario 
            WHERE c.id_medico=?
        """, (session['user_id'],)).fetchall()

    db.close()
    return render_template('admin_usuarios.html', medicos=medicos, citas_medico=citas_m)


# CORREGIDO: Se unificó la función eliminar (estaba repetida)
@app.route('/eliminar_medico/<int:id>')
def eliminar_medico(id):
    if session.get('rol') != 'admin':
        flash("No tienes permiso para realizar esta acción", "danger")
        return redirect(url_for('login'))

    db = obtener_conexion()
    try:
        db.execute("DELETE FROM usuarios WHERE id_usuario=?", (id,))
        db.commit()
        flash("Médico eliminado del sistema", "info")
    except Exception as e:
        print(f"Error al eliminar: {e}")
        flash("Error al eliminar el médico", "danger")
    finally:
        db.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)