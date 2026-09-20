from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ProveedorForm(FlaskForm):
    empresa = StringField('Nombre de la Empresa / Razón Social', validators=[
        DataRequired(message="El nombre de la empresa es obligatorio.")
    ])
    contacto = StringField('Persona de Contacto', validators=[
        DataRequired(message="El contacto es obligatorio.")
    ])
    email = StringField('Correo de Contacto', validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Ingrese un correo válido.")
    ])
    submit = SubmitField('Guardar Proveedor')