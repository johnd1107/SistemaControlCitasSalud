from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column('id_usuario', db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    id_paciente = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(15), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    historial_clinico = db.Column(db.Text)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)