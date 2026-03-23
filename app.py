import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Paciente, Producto

app = Flask(__name__)
app.config['SECRET_KEY'] = 'saludplus_secret_2026'

# --- CONFIGURACIÓN DE BASE DE DATOS DUAL ---
if os.environ.get('RENDER'):
    # Configuración para la NUBE (Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///render_salud.db'
else:
    # Configuración para tu PC (XAMPP)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/saludplus_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- RUTAS ---

@app.route('/')
@login_required
def index():
    return render_template('index.html', usuario=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Correo o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='scrypt')
        nuevo_u = Usuario(nombre=request.form['nombre'], email=request.form['email'], password=hashed_pw)
        db.session.add(nuevo_u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/inventario')
@login_required
def inventario():
    prods = Producto.query.all()
    return render_template('inventario.html', lista=prods)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)