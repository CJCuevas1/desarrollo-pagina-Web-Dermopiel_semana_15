from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres.")
    ])
    precio = DecimalField('Precio', validators=[
        DataRequired(message="El precio es obligatorio."),
        NumberRange(min=0.01, message="El precio debe ser mayor a 0.")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message="El stock es obligatorio."),
        NumberRange(min=0, message="El stock no puede ser negativo.")
    ])
    submit = SubmitField('Guardar Producto')