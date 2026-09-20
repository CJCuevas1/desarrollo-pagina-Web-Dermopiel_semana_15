from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FacturaForm(FlaskForm):
    cliente_id = IntegerField('ID del Cliente', validators=[
        DataRequired(message="El ID de cliente es obligatorio.")
    ])
    producto_id = IntegerField('ID del Producto', validators=[
        DataRequired(message="El ID de producto es obligatorio.")
    ])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message="La cantidad es obligatoria."),
        NumberRange(min=1, message="La cantidad mínima es 1.")
    ])
    submit = SubmitField('Generar Factura')