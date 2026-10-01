from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class ClienteForm(FlaskForm):
    nombres = StringField(
        'Nombres',
        validators=[DataRequired()]
    )

    apellidos = StringField(
        'Apellidos',
        validators=[DataRequired()]
    )

    email = StringField(
        'Correo electrónico',
        validators=[DataRequired(), Email()]
    )

    telefono = StringField(
        'Teléfono',
        validators=[DataRequired()]
    )

    submit = SubmitField(
        'Guardar Cliente'
    )


class LoginForm(FlaskForm):
    usuario = StringField(
        'Usuario',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Contraseña',
        validators=[DataRequired()]
    )

    submit = SubmitField(
        'Iniciar sesión'
    )


class RegistroForm(FlaskForm):
    usuario = StringField(
        'Usuario',
        validators=[DataRequired(), Length(min=3, max=50)]
    )

    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(),
            EqualTo(
                'password',
                message='Las contraseñas deben coincidir'
            )
        ]
    )

    submit = SubmitField(
        'Registrarse'
    )


class EmpleadoForm(FlaskForm):
    nombres = StringField(
        'Nombres',
        validators=[DataRequired()]
    )

    apellidos = StringField(
        'Apellidos',
        validators=[DataRequired()]
    )

    cargo = StringField(
        'Cargo',
        validators=[DataRequired()]
    )

    telefono = StringField(
        'Teléfono',
        validators=[DataRequired()]
    )

    email = StringField(
        'Correo electrónico',
        validators=[DataRequired(), Email()]
    )

    submit = SubmitField(
        'Guardar Empleado'
    )
class ServicioForm(FlaskForm):
    nombre_servicio = StringField(
        'Nombre del servicio',
        validators=[DataRequired()]
    )

    descripcion = StringField(
        'Descripción',
        validators=[DataRequired()]
    )

    precio = StringField(
        'Precio',
        validators=[DataRequired()]
    )

    submit = SubmitField(
        'Guardar Servicio'
    )