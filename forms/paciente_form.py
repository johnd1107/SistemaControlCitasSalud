from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length


class PacienteForm(FlaskForm):
    # Definimos los campos basados en lo que tu sistema necesita capturar
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    cedula = StringField('Cédula', validators=[DataRequired(), Length(min=10, max=10)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=15)])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])

    submit = SubmitField('Guardar Paciente')